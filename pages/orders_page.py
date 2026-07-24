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
appear anywhere in the real UI), then an optional "Shipping Address"
sub-section (Recipient Name*, Phone, Address Line 1/2, City,
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
        does not appear anywhere in the live UI."""
        self._customer_info_modal().locator("select").select_option(label=channel)

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
