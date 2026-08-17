"""Page Object for the Orders & Fulfillment list page.

VERIFIED 2026-07-16 against the live app at `/orders-list` (NOT `/orders` —
direct navigation to `/orders` resolves to a different, seemingly broken
domain; see MEMORY.md for details. Reach this page via
`DashboardPage.open_orders()` or `goto()` on this Page Object, both of
which use the confirmed `/orders-list` path).

Confirmed page elements:
- H1 "Orders & Fulfillment"
- Bulk action buttons: "Bulk Pick (0)", "Bulk Pack (0)", "Bulk Ship (0)"
  (the "(0)" reflects the current checkbox-selection count)
- "Create Order" button
- Search input, placeholder "Search by order number, customer..."
- Filter buttons: "All Statuses", "All Channels", "All Assignees",
  "Select date range"; "Clear All Filters" to reset
- Table columns: checkbox, Order, Customer, Channel, Assignee, Total,
  Status, **Packing** (a column separate from Status — resolves part of
  the boxes-vs-lots documentation ambiguity: packing progress is tracked
  independently of order status), Date, Actions
- Per-row action buttons: "View", "Pick (N)", "Pack", "Ship", "Cancel"
- A real order status seen live: "Processing" — confirms
  docs/order-management-guide.md's 9-status list over
  docs/getting-started.md's 6-status list for this field.

## Create Order — verified 2026-07-16 (2-step wizard, no data-testid)

**Full prerequisite chain confirmed live — a Product record alone is NOT
enough.** Step 2's product field is a live search against the Products
catalog (see products_page.py) filtered to products with AVAILABLE STOCK,
not just an existing catalog entry:
- Searching "Rali" (the pre-existing, already-stocked product) returned a
  suggestion with name, SKU, and live available stock:
  "RaliPN1 (RaliP1) — 997".
- Searching a nonexistent SKU returned nothing (no product at all).
- Searching a FRESHLY CREATED product's exact name/SKU (via
  `ProductsPage.add_product()`) *also* returned nothing — proving
  existence in the catalog isn't sufficient on its own.
- Root cause, confirmed via Products > (row) > "Inventory": a new
  product's inventory page reads "No inventory items — Inventory is
  created when you receive purchase orders. Create and receive a PO to
  get started." The 997 for RaliPN1 traces to a real, already-received
  Purchase Order (PO-3-000001, supplier "Rali test supplier").

So the real chain is: **Product -> Purchase Order (for that product) ->
Receive the PO -> stock becomes Available -> product appears in Order
Items search -> order can be created.** There is no inline "create
product" or "create PO" fallback anywhere in the Create Order flow.
Purchase Orders / Receiving don't have Page Objects yet (tracked as a
follow-up in MEMORY.md) — for now, tests either use the known-stocked
"RaliPN1"/"RaliP1" product (`tests/orders/test_create_order.py`) or assert
the negative cases directly (`test_order_requires_product.py`,
`test_new_product_without_stock_not_orderable.py`). See also Step 5 of
`output/Friday/Friday_New_User_Getting_Started_Guide.docx` for the
user-facing callout.

Step 1 ("Customer Info") confirmed fields: Search Existing Customer
(autocomplete), Customer Name* / Email* / Phone / Address, Channel
(a native `<select>` with real option text **"Direct to Consumer"** /
**"Business to Business"** — the docs' "D2C"/"B2B" abbreviations don't
appear anywhere in the real UI; confirmed live 2026-08-11, still only
these two options post-Aug-10-release. There is no "Web" channel option
here — confirmed as expected: Fridai isn't receiving web orders yet
since it isn't integrated with Hemi. The real "Web orders" concept lives
in Settings > Warehouses > "Add Warehouse" instead — a per-warehouse
"Web fulfilment allowed" checkbox plus a Priority field that decides
which eligible warehouse gets picked from first; see MEMORY.md), then
**Warehouse** (NEW as of the Aug 10 multi-warehouse release — a select
that's always disabled and pre-filled with whatever warehouse is
currently active in the app's global warehouse selector; same pattern as
Create Purchase Order, see `PurchaseOrdersPage.current_warehouse()` — it
is now the 2nd select in this modal, so Channel must be targeted by
index, not a bare `locator("select")`), then an optional "Shipping
Address" sub-section (Recipient Name*, Phone, Address Line 1/2, City,
State/Province, Postal Code, Country). None of Step 1's fields carry a
`data-testid`, and several (Customer Name, Email) aren't even
programmatically associated with their `<label>` (`get_by_label()` times
out) — they're located here by input `type` and DOM order instead, which
is fragile; see the UX Recommendations doc.

Step 2 ("Order Items") confirmed fields: a product search input
(placeholder "Scan barcode, SKU, or search by name..."), a quantity
number input, an "Add" button, an "Order Notes" textarea, and "Back" /
"Create Order" buttons. **There is no "Save Draft" button anywhere in this
flow** — contradicts docs/order-management-guide.md, which describes
"Save Draft" and "Confirm Order" as two distinct final actions.
"""

from __future__ import annotations

from pages.base_page import BasePage


class OrdersPage(BasePage):
    """The Orders & Fulfillment list page."""

    path = "/orders-list"

    # ---- Readiness ------------------------------------------------------------

    def wait_for_loaded(self, timeout: int = 10_000) -> None:
        self.by_role("heading", "Orders & Fulfillment").wait_for(
            state="visible", timeout=timeout
        )

    # ---- Search & filter (confirmed) -------------------------------------------

    def search(self, query: str) -> None:
        self.by_placeholder("Search by order number, customer...").fill(query)

    def open_status_filter(self) -> None:
        self.by_role("button", "All Statuses").click()

    def open_channel_filter(self) -> None:
        self.by_role("button", "All Channels").click()

    def open_assignee_filter(self) -> None:
        self.by_role("button", "All Assignees").click()

    def clear_all_filters(self) -> None:
        self.by_role("button", "Clear All Filters").click()

    # ---- Row navigation & actions (confirmed) ----------------------------------

    def view_order(self, order_number: str) -> None:
        """Click "View" on the row whose Order cell contains `order_number`."""
        row = self.page.locator("tr", has_text=order_number)
        row.get_by_role("button", name="View").click()

    def pick_order(self, order_number: str) -> None:
        row = self.page.locator("tr", has_text=order_number)
        row.get_by_role("button", name="Pick").click()

    def pack_order(self, order_number: str) -> None:
        row = self.page.locator("tr", has_text=order_number)
        row.get_by_role("button", name="Pack").click()

    def ship_order(self, order_number: str) -> None:
        row = self.page.locator("tr", has_text=order_number)
        row.get_by_role("button", name="Ship").click()

    def cancel_order(self, order_number: str) -> None:
        row = self.page.locator("tr", has_text=order_number)
        row.get_by_role("button", name="Cancel").click()

    # ---- Creating a new order (VERIFIED 2026-07-16 — 2-step wizard) -----------

    def start_create_order(self) -> None:
        self.by_role("button", "Create Order").click()

    def _customer_info_modal(self):
        """Scope to Step 1 ("Customer Info"). See BasePage.modal_scope() —
        needed because the background Orders page's own controls collide
        with the modal's when queried page-wide."""
        return self.modal_scope("Create New Order", "Cancel")

    def _order_items_modal(self):
        """Scope to Step 2 ("Order Items")."""
        return self.modal_scope("Order Items", "Add Items to Order")

    def set_customer_name(self, name: str) -> None:
        """Step 1, required. NOTE: not associated with its <label> in the
        real DOM (get_by_label times out) — located by input order instead:
        text input #0 is "Search Existing Customer", #1 is "Customer Name"."""
        self._customer_info_modal().locator('input[type="text"]').nth(1).fill(name)

    def set_customer_email(self, email: str) -> None:
        """Step 1, required. The only type="email" input in the modal."""
        self._customer_info_modal().locator('input[type="email"]').first.fill(email)

    def set_channel(self, channel: str) -> None:
        """channel: 'Direct to Consumer' or 'Business to Business' — these
        are the real <select> option labels; the docs' 'D2C'/'B2B' shorthand
        does not appear anywhere in the live UI. Confirmed live 2026-08-11:
        no 'Web' option exists here — see the module docstring for where
        the real "Web orders" concept lives instead.

        Confirmed live 2026-08-11: this is now the 1st of 2 selects in the
        modal (index 0) — the Aug 10 release inserted a disabled Warehouse
        select (see `current_warehouse()`) right after it, so a bare
        `locator("select")` now hits a strict-mode violation."""
        self._customer_info_modal().locator("select").nth(0).select_option(label=channel)

    def current_warehouse(self) -> str:
        """Read-only: the warehouse this order will be created for.
        Confirmed live 2026-08-11 — this select (index 1) is always
        disabled and pre-filled from the app's global warehouse selector;
        there is nothing to set here. Switch the global selector beforehand
        if you need a different warehouse. Same pattern as
        `PurchaseOrdersPage.current_warehouse()`."""
        select = self._customer_info_modal().locator("select").nth(1)
        return select.evaluate("(el) => el.options[el.selectedIndex].text")

    def go_to_order_items(self) -> None:
        """Step 1 -> Step 2. The button is disabled until Customer Name and
        Email are both filled."""
        self._customer_info_modal().get_by_role("button", name="Next").click()

    def add_line_item(self, search_query: str, quantity: int) -> None:
        """Step 2. Searches the existing Products catalog — if nothing
        matches `search_query` (e.g. the catalog is empty, or the SKU/name
        is wrong), no suggestion appears and there is nothing to click; this
        method will then hang/timeout on the suggestion click, which is the
        correct failure mode for that case (see
        test_order_requires_product.py for an explicit assertion on it
        instead of relying on this timeout)."""
        modal = self._order_items_modal()
        modal.get_by_placeholder("Scan barcode, SKU, or search by name...").fill(search_query)
        self.page.wait_for_timeout(800)  # debounce before the suggestion renders
        modal.get_by_text(search_query, exact=False).first.click()
        modal.locator('input[type="number"]').fill(str(quantity))
        modal.get_by_role("button", name="Add").click()

    def submit_new_order(self) -> None:
        """Step 2's final action. Confirmed: there is no separate "Save
        Draft" button in the real UI — only "Create Order"."""
        self._order_items_modal().get_by_role("button", name="Create Order").click()

    # ---- List-level helpers (VERIFIED live 2026-08-13) -------------------------

    def orders_total_count(self) -> int:
        """Parses the "Showing N orders total" text above the table."""
        text = self.page.get_by_text("Showing", exact=False).first.inner_text()
        # e.g. "Showing 27 orders total"
        return int(text.split()[1])

    def order_row(self, order_number: str):
        return self.page.locator("tr", has_text=order_number)

    def order_row_visible(self, order_number: str) -> bool:
        """Whether `order_number` appears in the CURRENTLY SCOPED list (per
        the global warehouse selector — see BasePage.set_active_warehouse).
        Confirmed live 2026-08-13: reallocating an order to a different
        warehouse makes it disappear from its original warehouse's list
        entirely, not just show a different Warehouse column value — this
        is the right way to assert that."""
        return self.order_row(order_number).count() > 0

    def order_row_warehouse(self, order_number: str) -> str:
        """Reads the Warehouse column of a visible order row. Raises if the
        order isn't in the current scope — check `order_row_visible()` or
        switch the global warehouse selector first."""
        row = self.order_row(order_number)
        # Columns: checkbox, Order, Customer, Channel, Warehouse, Assignee,
        # Total, Status, Packing, Date, Actions.
        return row.locator("td").nth(4).inner_text().strip()

    # ---- Order detail: ORDER OPS (Reallocate / Split) — NEW, VERIFIED live 2026-08-13 --

    def open_order_details(self, order_number: str) -> None:
        """Opens the order detail modal for `order_number` via its row's
        "View" button."""
        self.order_row(order_number).get_by_role("button", name="View").click()
        self.page.wait_for_timeout(1000)

    def _order_details_modal(self):
        """Scope to the order detail modal. "Order Details" is a stable
        substring of the dynamic heading ("Order Details: ORD-...");
        "Close" is the modal's own footer button, unique enough here since
        no order-row action is also named "Close"."""
        return self.modal_scope("Order Details", "Close")

    def current_order_detail_warehouse(self) -> str:
        """Reads the "Warehouse: X" line on the order detail Overview tab."""
        text = self._order_details_modal().get_by_text("Warehouse:", exact=False).first.inner_text()
        return text.split("Warehouse:", 1)[1].strip()

    def start_reallocate_order(self) -> None:
        """Requires the order details modal to already be open (see
        `open_order_details()`). Click "ORDER OPS > Reallocate"."""
        self._order_details_modal().get_by_role("button", name="Reallocate", exact=True).click()
        self.page.wait_for_timeout(800)

    def _reallocate_modal(self):
        """Scope to the "Reallocate Order" modal. Unlike Split, "Reallocate
        Order" (heading) is NOT a substring of the submit button's own
        text ("Reallocate") case-insensitively, so a bare "Cancel" anchor
        does not collide with the footer here — confirmed live 2026-08-13."""
        return self.modal_scope("Reallocate Order", "Cancel")

    def reallocate_target_warehouse_options(self) -> list[str]:
        """The Reallocate modal's target dropdown options, incl. the
        "Select warehouse" placeholder — confirmed live 2026-08-13 this
        list excludes whichever warehouse the order is currently in.
        Prefer this over hardcoding a seeded warehouse name."""
        return self._reallocate_modal().locator("select").evaluate(
            "(el) => Array.from(el.options).map(o => o.text)"
        )

    def set_reallocate_target_warehouse(self, warehouse_label: str) -> None:
        """Required — the modal has no default target (placeholder "Select
        warehouse"), unlike Split's target, which defaults to "Same as
        parent order"."""
        self._reallocate_modal().locator("select").select_option(label=warehouse_label)

    def submit_reallocate(self) -> None:
        """Confirmed live 2026-08-13: this whole-order move happens
        immediately (no further confirmation step) and the order
        disappears from the CURRENT warehouse scope's Orders list right
        away — see `order_row_visible()`."""
        self._reallocate_modal().get_by_role("button", name="Reallocate", exact=True).click()
        self.page.wait_for_timeout(1500)

    def start_split_order(self) -> None:
        """Requires the order details modal to already be open. Click
        "ORDER OPS > Split"."""
        self._order_details_modal().get_by_role("button", name="Split", exact=True).click()
        self.page.wait_for_timeout(800)

    def _split_modal(self):
        """Scope to the "Split Order" modal.

        CONFIRMED LIVE 2026-08-13 — do NOT use "Cancel" as the second
        anchor here (unlike `_reallocate_modal()`): the modal's own submit
        button reads "Split order", which matches the heading filter
        "Split Order" case-insensitively (Playwright's `has_text` string
        matching is case-insensitive). A small footer div containing just
        "Cancel" + "Split order" then satisfies BOTH filters and `.last`
        picks that tiny div instead of the real modal — every locator
        inside it then times out with zero matches. "Target warehouse" is
        a body-only label that isn't in the footer, so it forces the
        larger, correct container."""
        return self.modal_scope("Split Order", "Target warehouse")

    def set_split_target_warehouse(self, warehouse_label: str) -> None:
        """Optional — defaults to "Same as parent order". Pass this to
        split units into a sibling order at a DIFFERENT warehouse."""
        self._split_modal().locator("select").select_option(label=warehouse_label)

    def set_split_quantity(self, quantity: int, *, line_index: int = 0) -> None:
        """How many units of a line item to move into the new sibling
        order. `line_index` selects which line item's row when an order
        has more than one (0 = first) — only single-line orders have been
        exercised so far, so this defaults to the only case confirmed
        live."""
        self._split_modal().locator('input[type="number"]').nth(line_index).fill(str(quantity))

    def submit_split(self) -> None:
        """Confirmed live 2026-08-13: creates a genuinely new sibling
        order (its own order number, e.g. "ORD-<today's date>-<hex>" —
        NOT sharing the parent's date/number), reduces the parent's
        allocated quantity by the moved amount, and increases
        `orders_total_count()` by exactly 1. The sibling carries over the
        same customer/channel/warehouse (unless a different target
        warehouse was set) but is otherwise an independent order that
        proceeds through Pick/Pack/Ship on its own."""
        self._split_modal().get_by_role("button", name="Split order", exact=True).click()
        self.page.wait_for_timeout(1500)
