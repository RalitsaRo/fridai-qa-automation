"""Page Object for the Purchase Orders list page and its Create/ASN/Release
flows.

VERIFIED 2026-07-16 against the live app at `/purchase-orders`. This is the
other half of the "how does a product get stock" chain — see
orders_page.py's module docstring for the full picture. Confirmed real
lifecycle: **Draft -> Placed -> Supplier shipped -> Ready to receive ->
Partially received -> Received -> Completed** (or Cancelled at any point).
None of this is documented anywhere in the source docs.

Confirmed page elements:
- H1 "Purchase Orders"
- "Import CSV (new PO)", "Create Purchase Order" buttons
- Search input, placeholder "Search PO number..."
- Status filter (native <select>, options = the lifecycle above) and
  Supplier filter (native <select>)
- Table columns: PO Number, Supplier, Status, Receipt, Total, Actions
- Per-row action buttons vary by status: Draft/Placed -> "Record ASN",
  "Edit", "Cancel"; Supplier shipped -> "Release for receiving", "Cancel";
  Ready to receive / Partially received -> "Receive" (jumps to the
  Receiving page); Received -> "Complete PO".

## Create Purchase Order — 2-step wizard, same modal caveats as Create Order

Step 1 ("Purchase Order Details"): Supplier* (required select — a
supplier must already exist, e.g. via CRM & Suppliers > Suppliers > "Add
Supplier"; NOT built out here, tests reuse the pre-existing "Rali test
supplier"), Receiving Location* (required select, populated from real bin
locations), Initial status (Draft/Placed), Expected Delivery Date
(optional date), Notes (optional). Buttons: Cancel, Next.

Step 2 ("PO Items"): a "+ New Product" button (unlike Create Order, this
flow appears to support adding a brand-new product inline — not exercised
here), a product search (placeholder "Scan barcode or search product to
add to PO..." — unlike Order Items' search, THIS one returns every
product regardless of current stock, since the whole point is to add
stock to it), a Qty input, "Add" button, then "Back" / "Create Purchase
Order".

## Record ASN (Advance Shipping Notice) — moves Placed -> Supplier shipped

Two-step: click "Record ASN" on a row, then either "Upload ASN CSV" or
"Expected matches PO" (skip import), which reveals a further "Confirm"
button that actually submits.

## Release for receiving — moves Supplier shipped -> Ready to receive

Clicking the row's "Release for receiving" opens a small modal asking for
landed cost components (Shipping/Taxes/Misc, all optional) with its own
"Release for receiving" submit button — same modal-collision risk as
everywhere else in this app (no data-testid/role=dialog), so this is
scoped via `BasePage.modal_scope()`.

Once "Ready to receive", the PO shows up in `ReceivingPage`'s queue.
"""

from __future__ import annotations

from pages.base_page import BasePage


class PurchaseOrdersPage(BasePage):
    """The Purchase Orders list page."""

    path = "/purchase-orders"

    def wait_for_loaded(self, timeout: int = 10_000) -> None:
        self.by_role("heading", "Purchase Orders").wait_for(state="visible", timeout=timeout)

    def search(self, query: str) -> None:
        self.by_placeholder("Search PO number...").fill(query)

    # ---- Create Purchase Order (VERIFIED 2026-07-16) --------------------------

    def start_create_po(self) -> None:
        self.by_role("button", "Create Purchase Order").click()

    def _po_details_modal(self):
        return self.modal_scope("Create Purchase Order", "Cancel")

    def set_supplier(self, supplier_name: str) -> None:
        """Step 1, required. A supplier must already exist (see CRM & Suppliers)."""
        self._po_details_modal().locator("select").nth(0).select_option(label=supplier_name)

    def set_receiving_location(self, *, index: int | None = None, label: str | None = None) -> None:
        """Step 1, required. Pass either `index` (1 = first real option,
        since index 0 is the "Select a location" placeholder) or `label`
        for an exact location name. NOTE: some seeded location codes
        contain a Cyrillic "А" (U+0410) homoglyph mixed with Latin
        characters (confirmed live, e.g. "RZ-<CYRILLIC A>102-A-BIN01") —
        prefer `index` over hand-typing a `label` to avoid this trap."""
        select = self._po_details_modal().locator("select").nth(1)
        if label is not None:
            select.select_option(label=label)
        else:
            select.select_option(index=index if index is not None else 1)

    def set_initial_status(self, status: str) -> None:
        """Step 1, optional. status: 'Draft' or 'Placed'."""
        self._po_details_modal().locator("select").nth(2).select_option(label=status)

    def go_to_po_items(self) -> None:
        self._po_details_modal().get_by_role("button", name="Next").click()

    def _po_items_modal(self):
        return self.modal_scope("PO Items", "Add Items to Purchase Order")

    def add_po_line_item(self, search_query: str, quantity: int) -> None:
        """Step 2. Unlike Order Items' search, this one returns products
        regardless of current stock (it's how they GET stock)."""
        modal = self._po_items_modal()
        modal.get_by_placeholder("Scan barcode or search product to add to PO...").fill(search_query)
        self.page.wait_for_timeout(800)
        modal.get_by_text(search_query, exact=False).first.click()
        modal.locator('input[type="number"]').fill(str(quantity))
        modal.get_by_role("button", name="Add").click()

    def submit_create_po(self) -> None:
        """Submits the PO. Confirmed live: the list table takes a moment
        to refresh with the new row afterward — a caller reading the
        first row immediately (e.g. to capture the new PO number) can
        otherwise see stale data. This waits before returning."""
        self._po_items_modal().get_by_role("button", name="Create Purchase Order").last.click()
        self.page.wait_for_timeout(2000)

    # ---- Record ASN (Placed -> Supplier shipped) -------------------------------

    def record_asn_skip_import(self, po_number: str) -> None:
        """Record ASN for `po_number`, choosing "Expected matches PO"
        (skip CSV import) and confirming. Two clicks are required: the
        first reveals a "Confirm" button, the second actually submits."""
        row = self.page.locator("tr", has_text=po_number)
        row.get_by_role("button", name="Record ASN").click()
        self.by_role("button", "Expected matches PO").click()
        self.page.wait_for_timeout(500)
        self.by_role("button", "Confirm").click()

    # ---- Release for receiving (Supplier shipped -> Ready to receive) --------

    def release_for_receiving(self, po_number: str) -> None:
        """Opens a landed-cost modal (Shipping/Taxes/Misc, all optional)
        and submits it with defaults."""
        row = self.page.locator("tr", has_text=po_number)
        row.get_by_role("button", name="Release for receiving").click()
        self.page.wait_for_timeout(500)
        modal = self.modal_scope("Release for receiving", "Cancel")
        modal.get_by_role("button", name="Release for receiving").click()
