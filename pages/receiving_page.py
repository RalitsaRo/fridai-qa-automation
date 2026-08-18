"""Page Object for the Receiving queue and the per-PO receiving screen.

VERIFIED 2026-07-16 against the live app — this is the final leg of the
"how does a product get stock" chain (see orders_page.py and
purchase_orders_page.py for the rest of it). A PO only appears here once
its status is "Ready to receive" (reached via
`PurchaseOrdersPage.release_for_receiving()`).

Confirmed queue page (`/receiving`) elements:
- H1 "Receiving"
- "Purchase orders ready for warehouse receive (N in queue)"
- Table columns: PO, Supplier, Status, Receipt, Actions — action is
  "Start receiving", which navigates to `/receiving/{id}`.

## Per-PO receiving screen (`/receiving/{id}`) — a 3-step scan loop per line

Built for a physical barcode scanner: each control auto-focuses and
expects Enter after a scan, not a mouse click.

1. **Scan product** — text input, placeholder "Scan product SKU or
   barcode...". Fill + press Enter.
2. **Confirm quantity** — a `<input type="number">` auto-focuses,
   pre-filled with the full remaining expected quantity. Press Enter to
   accept the default (confirmed: `page.keyboard.press("Enter")`, not a
   `.fill()` — this is a bare focused input at this point).
3. **Scan put-away location** — text input, placeholder "Scan location
   barcode...", PLUS a same-purpose `<select>` ("Or select location
   manually..."). **CORRECTED 2026-08-17** — this dropdown DOES work; an
   earlier note here claimed it didn't, which was wrong. The on-screen
   hint reads "Scan location or select from list, then press Enter to
   confirm." — the earlier check only called `select_option()` and never
   followed up with Enter, so it looked like a no-op (no network request,
   step unchanged). Pressing Enter after selecting fires the real
   `POST /crm/purchase-orders/{id}/receive` and completes the line, same
   as the scan path. See `select_location_manually()` below.

   **Global nav regression, confirmed live 2026-08-11.** The Aug 10
   multi-warehouse release added a page-wide "Active warehouse" `<select>`
   (`aria-label="Active warehouse"`, `data-guidance-id="warehouse-shell"`)
   to the top nav on every page, not just this one -- a bare
   `page.locator("select")` anywhere in the app can now hit 2 elements
   instead of 1. `first_available_location_text()` below excludes it via
   an attribute-selector negation rather than an index, since the global
   selector's DOM position relative to a given page's own selects isn't
   guaranteed.

   **Data quality trap — confirmed live 2026-07-16, FIXED the same day.**
   Some seeded location codes mixed a Cyrillic "А" (U+0410) with Latin
   characters (e.g. "RZ-<CYRILLIC A>102-A-BIN01", visually
   indistinguishable from "RZ-A102-A-BIN01"), so typing a hand-written
   Latin-only version got "Location not found". All 8 affected locations
   (the "RaliZone" zone) were corrected via Locations > Edit Location >
   Save Changes; a fresh full-tree scan of all 412 locations now shows
   zero non-ASCII characters. `first_available_location_text()` below
   still reads the exact option text via JS as a defensive habit — new
   locations could in principle reintroduce the same class of bug, and
   this avoids ever hand-typing one either way.

Once every line is fully received, the page shows "Complete!" and a
"Finish receiving" button. Confirmed live: the product becomes searchable
with its new available stock in Create Order's Order Items step
immediately after this — even though the PO's own status at that point
reads **"Partially Received"**, not "Received" (that transition, and the
subsequent Received -> Completed via "Complete PO", were not chased
further — not needed for a product to become orderable).
"""

from __future__ import annotations

from pages.base_page import BasePage


class ReceivingPage(BasePage):
    """The Receiving queue (`/receiving`) and, after `start_receiving()`,
    the per-PO receiving screen (`/receiving/{id}`)."""

    path = "/receiving"

    def wait_for_loaded(self, timeout: int = 10_000) -> None:
        self.by_role("heading", "Receiving").wait_for(state="visible", timeout=timeout)

    def start_receiving(self, po_number: str) -> None:
        """Navigates from the queue to `/receiving/{id}` for `po_number`."""
        row = self.page.locator("tr", has_text=po_number)
        row.get_by_role("button", name="Start receiving").click()

    # ---- Per-line scan loop (on /receiving/{id}) -------------------------------

    def scan_product(self, sku: str) -> None:
        field = self.by_placeholder("Scan product SKU or barcode...")
        field.fill(sku)
        field.press("Enter")

    def accept_default_quantity(self) -> None:
        """Confirms the auto-focused quantity input's pre-filled default
        (the full remaining expected quantity) by pressing Enter."""
        self.page.keyboard.press("Enter")

    def first_available_location_text(self) -> str:
        """Reads option[1]'s exact text from the location <select> (this
        dropdown is real and functional — see `select_location_manually()`
        below — this accessor just lets callers read a location's exact
        text without hand-typing a code that might contain the
        Cyrillic-homoglyph trap described above).

        Confirmed live 2026-08-11: excludes the new page-wide "Active
        warehouse" global selector (see module docstring) via an
        attribute-selector negation — a bare `page.locator("select")`
        now resolves 2 elements on this screen."""
        location_select = self.page.locator('select:not([aria-label="Active warehouse"])')
        return location_select.evaluate("(el) => el.options[1].text")

    def scan_location(self, location_text: str) -> None:
        field = self.by_placeholder("Scan location barcode...")
        field.fill(location_text)
        field.press("Enter")

    def select_location_manually(self, index: int = 1) -> None:
        """Alternative to `scan_location()` — uses the "Or select location
        manually" dropdown instead of hand-typing/scanning a code.
        CONFIRMED WORKING live 2026-08-17 (an earlier note here wrongly
        called this broken): selecting an option alone does nothing
        visible, but selecting THEN pressing Enter — same pattern as the
        scan field — fires the real receive request and completes the
        line. `index=1` is the first real location option (index 0 is the
        "Or select location manually" placeholder)."""
        select = self.page.locator('select:not([aria-label="Active warehouse"])')
        select.select_option(index=index)
        select.press("Enter")

    def finish_receiving(self) -> None:
        self.by_role("button", "Finish receiving").click()

    def receive_full_line(self, sku: str) -> None:
        """Convenience: scan product -> accept default qty -> scan the
        first available location. Does not call `finish_receiving()` —
        callers should do that explicitly once all lines are done."""
        self.scan_product(sku)
        self.page.wait_for_timeout(500)
        self.accept_default_quantity()
        self.page.wait_for_timeout(500)
        self.scan_location(self.first_available_location_text())
