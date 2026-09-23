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
- Table columns: (blank leading column — checkbox/expand, no header text),
  PO Number, Supplier, **Warehouse** (NEW 2026-08-10 release — the column
  header count was Supplier/Status/Receipt/Total/Actions before; confirmed
  live 2026-08-11 the real order is now blank/PO Number/Supplier/
  Warehouse/Status/Receipt/Total/Actions), Status, Receipt, Total, Actions
- Per-row action buttons vary by status: Draft/Placed -> "Record ASN",
  "Edit", "Cancel"; Supplier shipped -> "Release for receiving", "Cancel";
  Ready to receive / Partially received -> "Receive" (jumps to the
  Receiving page); Received -> "Complete PO".

## Create Purchase Order — 2-step wizard, same modal caveats as Create Order

Step 1 ("Purchase Order Details"), confirmed live 2026-08-11 after the
Aug 10 multi-warehouse release added a field — order is now: Supplier*
(required select — a supplier must already exist, e.g. via CRM &
Suppliers > Suppliers > "Add Supplier"), **Warehouse*** (NEW — a select
that's always disabled and pre-filled with whatever warehouse is
currently active in the global warehouse selector at the top of the app;
it is NOT meant to be interacted with here — switch the global selector
*before* opening Create Purchase Order if you need a different
warehouse), Receiving Location* (required select, populated from real bin
locations — now the 3rd select, not the 2nd), Initial status
(Draft/Placed — now the 4th select), Expected Delivery Date (optional
date), Notes (optional). Buttons: Cancel, Next (disabled until Supplier is
chosen — confirmed the Warehouse field does not need to be touched for
Next to enable).

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

    def first_po_number(self) -> str:
        """The PO Number cell of the table's first (most recent) row.

        CORRECTED 2026-08-20 to not assume a fixed column index. The Aug
        10 release inserted a blank leading column (checkbox/expand, no
        header text) ahead of PO Number, making it the table's 2nd `<td>`
        (index 1) instead of the 1st — this method was patched to
        `nth(1)` accordingly. Confirmed live 2026-08-20 that blank column
        is GONE again (table headers are back to PO NUMBER/SUPPLIER/
        WAREHOUSE/STATUS/RECEIPT/TOTAL/ACTIONS, 7 columns, no leading
        blank) — `nth(1)` now reads the SUPPLIER cell instead. Rather than
        chase a third index if this flips again, this scans the row's
        cells for the first one starting with "PO-" (the real PO number
        format), which is correct regardless of how many columns precede
        it."""
        cells = self.page.locator("table tbody tr").first.locator("td").all_inner_texts()
        for cell in cells:
            text = cell.strip()
            if text.startswith("PO-"):
                return text
        raise ValueError(f"No cell starting with 'PO-' found in the first row: {cells!r}")

    # ---- Create Purchase Order -------------------------------------------------
    # Warehouse field behaviour (product design, confirmed with PO 2026-09-21):
    #
    # - Top-bar Active warehouse = a SPECIFIC warehouse:
    #     Create PO Step 1 does not expose an editable Warehouse control
    #     (live DOM with WH-2: no Warehouse <select> at all). The PO is
    #     bound to the shell warehouse. Older builds showed a disabled,
    #     pre-filled Warehouse select — treat either presentation as "locked".
    # - Top-bar Active warehouse = "All warehouses" (Admin-capable accounts):
    #     Warehouse becomes a required, editable <select> in the modal so
    #     the user picks which site the PO belongs to.
    #
    # The current automation User role has no "All warehouses" option, so
    # tests exercise the specific-warehouse path only. `set_warehouse()` is
    # still provided for Admin runs.
    #
    # Other Step-1 fields (order when Warehouse is omitted):
    #   Supplier* → Receiving Location* → Initial status → Date / Notes
    # Receiving Location stays empty/disabled until a Supplier is chosen.

    def start_create_po(self) -> None:
        self.by_role("button", "Create Purchase Order").click()

    def _po_details_modal(self):
        return self.modal_scope("Create Purchase Order", "Cancel")

    def _po_step1_selects(self) -> dict[str, object]:
        """Map Step-1 selects by their nearby label text.

        Returns keys among: supplier, warehouse, location, status.
        `warehouse` is only present when the top-bar is All warehouses
        (or on older builds that always rendered a locked Warehouse select).
        """
        modal = self._po_details_modal()
        mapping: dict[str, object] = {}
        count = modal.locator("select").count()
        for i in range(count):
            sel = modal.locator("select").nth(i)
            near = sel.evaluate(
                "(el) => (el.parentElement && el.parentElement.innerText || '').trim()"
            )
            head = near.split("\n", 1)[0].strip().lower()
            if head.startswith("supplier"):
                mapping["supplier"] = sel
            elif head.startswith("warehouse"):
                mapping["warehouse"] = sel
            elif head.startswith("receiving location") or head.startswith("receiving"):
                mapping["location"] = sel
            elif head.startswith("initial status") or head.startswith("initial"):
                mapping["status"] = sel
        return mapping

    def modal_warehouse_select(self):
        """In-modal Warehouse <select>, or an empty locator if omitted."""
        mapped = self._po_step1_selects().get("warehouse")
        if mapped is not None:
            return mapped
        # Empty locator — callers use .count() == 0
        return self._po_details_modal().locator("select[data-fridai-missing-warehouse]")

    def is_modal_warehouse_editable(self) -> bool:
        """True only when Create PO shows an enabled Warehouse select
        (expected when Active warehouse = All warehouses)."""
        sel = self.modal_warehouse_select()
        if sel.count() == 0:
            return False
        return not sel.is_disabled()

    def set_supplier(self, supplier_name: str) -> None:
        """Step 1, required. A supplier must already exist (see CRM & Suppliers).

        Also waits for Receiving Location options to populate — confirmed
        live 2026-09-21: location select is empty/disabled until a
        supplier is chosen.
        """
        selects = self._po_step1_selects()
        selects["supplier"].select_option(label=supplier_name)
        # Wait until location has real options (placeholder + at least one bin).
        self.page.wait_for_function(
            """() => {
              const modal = [...document.querySelectorAll('div')].find(d =>
                (d.innerText || '').includes('Create Purchase Order')
                && (d.innerText || '').includes('Receiving Location')
              );
              if (!modal) return false;
              const blocks = [...modal.querySelectorAll('select')].map(s => ({
                near: (s.parentElement && s.parentElement.innerText || '').trim(),
                disabled: s.disabled,
                n: s.options.length,
              }));
              const loc = blocks.find(b =>
                b.near.toLowerCase().startsWith('receiving')
              );
              return loc && !loc.disabled && loc.n > 1;
            }""",
            timeout=10_000,
        )

    def current_warehouse(self) -> str:
        """Warehouse this PO will be created for.

        Prefer the in-modal Warehouse select when present (locked or
        editable). Otherwise fall back to the top-bar Active warehouse —
        the live specific-warehouse path omits the modal field entirely.
        """
        sel = self.modal_warehouse_select()
        if sel.count() > 0:
            return sel.evaluate("(el) => el.options[el.selectedIndex].text")
        return self.current_active_warehouse()

    def set_warehouse(self, warehouse_label: str) -> None:
        """Set Create PO Warehouse when the top-bar is All warehouses.

        Raises if the field is omitted (specific warehouse in the shell)
        or present but disabled (locked to the shell warehouse).
        """
        sel = self.modal_warehouse_select()
        if sel.count() == 0:
            raise RuntimeError(
                "Create PO has no Warehouse field — Active warehouse is a "
                "specific site, so the PO is bound to the shell warehouse. "
                "Switch the top-bar to 'All warehouses' (Admin) to choose "
                f"a warehouse in the modal. Currently: {self.current_active_warehouse()!r}."
            )
        if sel.is_disabled():
            raise RuntimeError(
                "Create PO Warehouse field is locked/pre-filled because a "
                "specific warehouse is active in the top-bar. Switch to "
                "'All warehouses' to edit it. "
                f"Current shell: {self.current_active_warehouse()!r}; "
                f"modal value: {self.current_warehouse()!r}."
            )
        sel.select_option(label=warehouse_label)

    def set_receiving_location(self, *, index: int | None = None, label: str | None = None) -> None:
        """Step 1, required. Pass either `index` (1 = first real option,
        since index 0 is the \"Select a location\" placeholder) or `label`
        for an exact location name.

        Call **after** `set_supplier()` — locations only load once a
        supplier is selected.
        """
        select = self._po_step1_selects()["location"]
        if label is not None:
            select.select_option(label=label)
        else:
            select.select_option(index=index if index is not None else 1)

    def set_initial_status(self, status: str) -> None:
        """Step 1, optional. status: 'Draft' or 'Placed'."""
        self._po_step1_selects()["status"].select_option(label=status)

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
