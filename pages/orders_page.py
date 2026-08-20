"""Page Object for the Orders list / "Order Queue" page.

VERIFIED 2026-07-16 against the live app at `/orders-list` (NOT `/orders` —
direct navigation to `/orders` resolves to a different, seemingly broken
domain; see MEMORY.md for details. Reach this page via
`DashboardPage.open_orders()` or `goto()` on this Page Object, both of
which use the confirmed `/orders-list` path).

## Aug 19, 2026 release — visual rework of the order queue (CONFIRMED LIVE 2026-08-19)

The whole list view was reworked around order **lifecycle queues** instead
of a flat table. Everything below in this section replaces the pre-rework
description that used to live here (H1 "Orders & Fulfillment", separate
Channel/Assignee/Total/Packing columns, always-visible per-row
Pick/Pack/Ship/Cancel buttons) — kept only as history in old commits.

- **H1 is now "Orders"** (not "Orders & Fulfillment"), subtitle "Work the
  floor from allocate through ship. Queues overlap when an order still has
  mixed work."
- **Work Queues** — a real `role="tablist"` (`aria-label="Order work
  queues"`) of `role="tab"` buttons, each with a count badge glued to its
  label text and a `title` attribute explaining the queue: All orders
  ("Everything except combined source orders"), Ready to pick ("Allocated
  units waiting to be picked"), Ready to pack ("Picked units waiting to be
  packed"), Ready to ship, Partially fulfilled, Backorders. Selecting one
  filters the table to that queue.
- **Filters row** renamed/changed: "Any status" (was "All Statuses"),
  "All channels", "All assignees", "Date range" (was "Select date range").
- **Table columns are now**: (checkbox), ORDER, CUSTOMER, WAREHOUSE,
  PROGRESS, STATUS, DATE, ACTION — 8 `<td>`s total (indices 0-7). Channel,
  line count, and order total all moved INTO the ORDER cell as a combined
  line, e.g. "D2C · 1 lines · $500.10"; a **"Combined"** badge and a
  "from ORD-X, ORD-Y, ..." line appear there too for orders created by the
  new **Combine** bulk action (the counterpart to Split — see
  `combine_button()`). CUSTOMER now also carries the assignee name as an
  optional 3rd line.
- **PROGRESS column** (NEW) replaces the old separate Packing column: a
  colored horizontal bar + text like "5 ready to pack" / "3 ready to pick",
  or plain "Cancelled" text with no bar for cancelled orders.
- **ACTION column** is now minimized to ONE dynamic "next action" button
  (bold/black) — its label reflects both the stage and whether the order
  is partially through it: "Pick (N)", "Pack (N)", "Ship (N)", "Ship
  remaining (N)", "Pack remaining (N)", or (in "All warehouses" scope
  only) "Allocate (N)" for orders not yet allocated to any warehouse —
  plus a plain "View" link, plus (when more actions exist) a "More
  actions" kebab button (real `aria-label="More actions"`, NOT an
  accessibility gap) revealing extra actions like "Cancel remaining" as
  plain buttons (confirmed NOT rendered with ARIA menu/menuitem roles —
  they're regular buttons that appear once the kebab is clicked). Rows
  with nothing left to do (fully Shipped/Completed, or Cancelled) show
  only "View".
- **Partial fulfilment is a first-class, explicit flow at every stage**
  (confirmed live end-to-end for Pick — see `submit_complete_picking()`
  below), not an edge case: the Pick modal's per-line quantity input
  defaults to **0**, not the full remaining amount, forcing an explicit
  choice, and completing with less than the full remaining quantity opens
  a **second confirmation modal** ("Incomplete pick — what next?") with
  three explicit choices. An order picked at, say, WH-2 with 7 of 10 units
  already picked shows "Partially Picked" status and its next action
  becomes "Pack remaining (3)" for just the picked units.
- **Bulk actions are gated by the global warehouse selector — CONFIRMED
  LIVE 2026-08-19**: with a SPECIFIC warehouse active, selecting rows
  reveals "Bulk pick (N)", "Bulk pack (N)", "Bulk ship (N)", "Combine
  (N)", "Clear". With **"All warehouses"** active, the warehouse-specific
  ones disappear — only "Allocate (N)" and "Combine (N)" (plus "Clear")
  remain, since Pick/Pack/Ship are inherently tied to one physical
  warehouse but Allocate/Combine are not.

Order Ops (Reallocate / Split, from the order detail "View" modal) are
unaffected by this rework — see the dedicated section further down.

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
    """The Orders list / "Order Queue" page."""

    path = "/orders-list"

    # ---- Readiness ------------------------------------------------------------

    def wait_for_loaded(self, timeout: int = 10_000) -> None:
        """Confirmed live 2026-08-19: the H1 is now "Orders" (exact match —
        do NOT match on "Orders & Fulfillment", that heading no longer
        exists on this page after the visual rework)."""
        self.by_role("heading", "Orders", exact=True).wait_for(
            state="visible", timeout=timeout
        )

    # ---- Search & filter ---------------------------------------------------

    def search(self, query: str) -> None:
        self.by_placeholder("Search order number or customer").fill(query)

    def open_status_filter(self) -> None:
        """Confirmed live 2026-08-19: renamed from "All Statuses" to "Any
        status" as part of the visual rework."""
        self.by_role("button", "Any status").click()

    def open_channel_filter(self) -> None:
        self.by_role("button", "All channels").click()

    def open_assignee_filter(self) -> None:
        self.by_role("button", "All assignees").click()

    # ---- Work Queues tablist (NEW, confirmed live 2026-08-19) -------------------

    def open_queue_tab(self, name: str) -> None:
        """Click a Work Queues tab: 'All orders', 'Ready to pick', 'Ready
        to pack', 'Ready to ship', 'Partially fulfilled', or 'Backorders'.
        Confirmed live: a real `role="tab"` inside a `role="tablist"`
        (`aria-label="Order work queues"`) — `exact=False` because the
        accessible name glues a count badge onto the label
        (e.g. "Ready to pick17")."""
        self.page.get_by_role("tab", name=name, exact=False).click()
        self.page.wait_for_timeout(600)

    def queue_tab_count(self, name: str) -> int:
        """Reads the count badge glued to a Work Queues tab's label."""
        text = self.page.get_by_role("tab", name=name, exact=False).inner_text()
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0

    # ---- Row navigation & next-action (CONFIRMED live 2026-08-19) --------------

    def view_order(self, order_number: str) -> None:
        """Click "View" on the row whose Order cell contains `order_number`."""
        self.order_row(order_number).get_by_role("button", name="View").click()

    def next_action_label(self, order_number: str) -> str:
        """Reads the row's single "next action" button text — e.g.
        "Pick (3)", "Pack remaining (5)", "Ship (1)", "Allocate (2)".
        Raises if the order has nothing left to do (only "View" shown)."""
        action_cell = self.order_row(order_number).locator("td").last
        return action_cell.locator("button").first.inner_text().strip()

    def click_next_action(self, order_number: str) -> None:
        """Clicks the row's single "next action" button, whatever its
        current dynamic label is (Pick/Pack/Ship/Allocate, "remaining" or
        not). This is the correct way to advance an order now — the old
        pattern of matching a fixed "Pick"/"Pack"/"Ship" button name still
        works too (see `pick_order()` etc.) since those labels are still
        real substrings, but this is label-agnostic."""
        action_cell = self.order_row(order_number).locator("td").last
        action_cell.locator("button").first.click()
        self.page.wait_for_timeout(1000)

    def pick_order(self, order_number: str) -> None:
        """Confirmed live 2026-08-19: label is now "Pick (N)" (was bare
        "Pick") — `exact=False` matches either form."""
        self.order_row(order_number).get_by_role("button", name="Pick", exact=False).click()
        self.page.wait_for_timeout(1000)

    def pack_order(self, order_number: str) -> None:
        """Matches both "Pack (N)" and "Pack remaining (N)"."""
        self.order_row(order_number).get_by_role("button", name="Pack", exact=False).click()
        self.page.wait_for_timeout(1000)

    def ship_order(self, order_number: str) -> None:
        """Matches both "Ship (N)" and "Ship remaining (N)"."""
        self.order_row(order_number).get_by_role("button", name="Ship", exact=False).click()
        self.page.wait_for_timeout(1000)

    def open_more_actions(self, order_number: str) -> None:
        """Opens the row's "More actions" kebab (⋯). Confirmed live
        2026-08-19: this button has a real `aria-label="More actions"` —
        NOT an accessibility gap, despite having no visible text. Only
        rendered for rows that have more than just "View" available."""
        self.order_row(order_number).get_by_role("button", name="More actions").click()
        self.page.wait_for_timeout(500)

    def click_more_action(self, action_text: str) -> None:
        """After `open_more_actions()`, click a revealed action by its
        text (e.g. "Cancel remaining"). Confirmed live 2026-08-19: these
        are plain `role="button"` elements, NOT rendered with ARIA
        menu/menuitem roles — a `get_by_role("menu")` / `get_by_role
        ("menuitem")` query finds nothing even when the kebab is open."""
        self.page.get_by_role("button", name=action_text, exact=False).click()

    def cancel_order(self, order_number: str) -> None:
        """Confirmed live 2026-08-19: Cancel is no longer a direct row
        button — it's revealed via the "More actions" kebab, and its
        label may read "Cancel" or "Cancel remaining" depending on
        fulfilment progress. This opens the kebab and clicks whichever
        variant is present."""
        self.open_more_actions(order_number)
        self.click_more_action("Cancel")

    # ---- List-level helpers (CONFIRMED live 2026-08-19) ------------------------

    def orders_total_count(self) -> int:
        """Confirmed live 2026-08-19: the old "Showing N orders total"
        text is gone — the equivalent count now lives on the "All orders"
        Work Queues tab."""
        return self.queue_tab_count("All orders")

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
        switch the global warehouse selector first.

        Confirmed live 2026-08-19: columns are now (checkbox=0), ORDER=1,
        CUSTOMER=2, WAREHOUSE=3, PROGRESS=4, STATUS=5, DATE=6, ACTION=7 —
        Warehouse moved from index 4 to index 3 as part of the visual
        rework (Channel/Assignee/Total folded into the ORDER/CUSTOMER
        cells, and a new PROGRESS column was inserted)."""
        row = self.order_row(order_number)
        return row.locator("td").nth(3).inner_text().strip()

    def order_row_progress_text(self, order_number: str) -> str:
        """Reads the PROGRESS column text (NEW, confirmed live 2026-08-19)
        — e.g. "5 ready to pack", "3 ready to pick", or "Cancelled" for a
        cancelled order (no progress bar in that case)."""
        return self.order_row(order_number).locator("td").nth(4).inner_text().strip()

    def order_row_status(self, order_number: str) -> str:
        """Reads the STATUS column badge text — e.g. "Processing",
        "Picked", "Partially Picked", "Partially Packed", "Cancelled"."""
        return self.order_row(order_number).locator("td").nth(5).inner_text().strip()

    # ---- Bulk selection & bulk actions (CONFIRMED live 2026-08-19) -------------

    def select_all_orders_checkbox(self) -> None:
        """Checks the table header's "select all" checkbox — selects every
        row currently in view (i.e. matching the active Work Queue /
        filters), not just the current page.

        Confirmed live 2026-08-20: uses `.click()`, NOT Playwright's
        `.check()`. `.check()` clicks and then strictly re-verifies the
        `checked` property changed, but that verification can catch this
        checkbox mid a brief re-render (e.g. right after a warehouse
        switch or Work Queue change) and time out with "Clicking the
        checkbox did not change its state" — even though the click itself
        genuinely worked. A plain `.click()` followed by a short settle
        wait was confirmed reliable in the same scenario where `.check()`
        consistently failed."""
        self.page.wait_for_timeout(500)
        self.page.locator("table thead input[type='checkbox']").first.click()
        self.page.wait_for_timeout(500)

    def select_order_checkbox(self, order_number: str) -> None:
        """See `select_all_orders_checkbox()` for why `.click()` is used
        instead of `.check()`."""
        self.order_row(order_number).locator('input[type="checkbox"]').click()
        self.page.wait_for_timeout(300)

    def clear_selection(self) -> None:
        self.page.get_by_role("button", name="Clear", exact=True).click()

    def _bulk_action_bar(self):
        """Scope to the floating bulk-action bar that appears at the
        bottom of the viewport once 1+ rows are selected. Confirmed live
        2026-08-19: it's a dark floating bar containing "N selected" text,
        the action buttons, and "Clear" — that combination is unique
        enough to anchor on, since no other part of the page combines
        both "selected" and "Clear" text. Scoping matters here: several
        per-ROW next-action buttons can independently read "Allocate (N)"
        (in "All warehouses" scope) with a different accessible name each
        time, but a bare page-wide `get_by_role("button", name="Allocate")`
        collides across all of them plus the real bulk button — confirmed
        live this raises a strict-mode violation with 7 matches on a page
        with several unallocated orders."""
        return self.page.locator("div").filter(has_text="selected").filter(has_text="Clear").last

    def bulk_pick_button(self):
        """Only present when a SPECIFIC warehouse is active in the global
        selector (see BasePage) — confirmed live 2026-08-19 this and
        `bulk_pack_button()`/`bulk_ship_button()` are ABSENT under "All
        warehouses", since Pick/Pack/Ship are tied to one physical
        warehouse. Use `.count()` or `expect(...).to_be_visible()` /
        `not_to_be_visible()` to assert presence, don't assume it exists."""
        return self._bulk_action_bar().get_by_role("button", name="Bulk pick", exact=False)

    def bulk_pack_button(self):
        return self._bulk_action_bar().get_by_role("button", name="Bulk pack", exact=False)

    def bulk_ship_button(self):
        return self._bulk_action_bar().get_by_role("button", name="Bulk ship", exact=False)

    def allocate_bulk_button(self):
        """Confirmed live 2026-08-19: present under BOTH a specific
        warehouse and "All warehouses" — for orders not yet allocated to
        any warehouse (Allocate isn't warehouse-specific the way
        Pick/Pack/Ship are). MUST be scoped to `_bulk_action_bar()` — see
        its docstring for why a page-wide query breaks."""
        return self._bulk_action_bar().get_by_role("button", name="Allocate", exact=False)

    def combine_button(self):
        """Confirmed live 2026-08-19: the counterpart to Split (see the
        Order Ops section below) — combines the selected orders into one.
        Present under both a specific warehouse and "All warehouses", but
        confirmed live it can render DISABLED depending on the selection
        (observed disabled with 17/39 orders selected — exact precondition,
        e.g. same customer or compatible statuses, not yet determined).
        NOT yet exercised end-to-end by this suite — tracked as a
        follow-up."""
        return self._bulk_action_bar().get_by_role("button", name="Combine", exact=False)

    # ---- Pick task modal (NEW rework, CONFIRMED live 2026-08-19, incl. partials) --

    def _pick_modal(self):
        """Scope to the "Pick Order {number}" modal."""
        return self.modal_scope("Pick Order", "Complete Picking")

    def set_pick_quantity(self, quantity: int, *, line_index: int = 0) -> None:
        """Sets a line item's pick quantity. Confirmed live 2026-08-19:
        the modal has a "Qty" input near the top (for the barcode-scan
        add-flow) PLUS one editable quantity input per line under "Pick
        Items" — this targets the line inputs specifically via
        `nth(line_index + 1)` (index 0 is the top Qty field), not
        `.last()`, so it works correctly for multi-line orders too.
        Confirmed the per-line input defaults to 0, not the full
        remaining amount — partial picking is the explicit default
        interaction, not an edge case.

        `line_index` is DISPLAY order in the "Pick Items" list, which is
        confirmed live 2026-08-20 to NOT necessarily match the order line
        items were added to the order in — a 2-line order (RaliP1 added
        first, a second SKU added second) showed the second SKU FIRST in
        the Pick modal. Use `pick_line_index_for_sku()` to find the right
        index by SKU/product name rather than assuming add-order for any
        order with more than one line."""
        self._pick_modal().locator('input[type="number"]').nth(line_index + 1).fill(str(quantity))

    def pick_line_index_for_sku(self, sku_or_name: str) -> int:
        """Finds a line's position in the "Pick Items" list by SKU or
        product name substring, for use as `set_pick_quantity()`'s
        `line_index` — see that method's docstring for why display order
        can't be assumed to match the order lines were added in. Raises
        `ValueError` if no line matches.

        CONFIRMED LIVE 2026-08-20: a naive `locator("div").filter(has_text=
        ...)` approach does NOT work here — "Quantity:"/"Location:" text
        appears at multiple NESTED div levels per line (an outer wrapper
        spanning all lines, a per-line row, and smaller inner divs), so
        every such filter matches several ancestors of the same line
        rather than one container per line, and every line ends up
        resolving to index 0. This walks up from each number input's own
        DOM position instead (first ancestor whose text contains
        "Location:" — that's always the immediate per-line row, never the
        multi-line wrapper, since we stop at the nearest match) to build
        an accurate {input position: line text} map via JS."""
        modal = self._pick_modal()
        # `.slice(1)` drops the top "Qty" scan-add field up front — its
        # own ancestor chain has no "Location:" text nearby, so an
        # unbounded walk-up doesn't stop until it reaches a top-level
        # container spanning ALL lines, which then falsely substring-
        # matches every SKU at index 0 (confirmed live 2026-08-20: this
        # was the actual bug in an earlier version of this method, which
        # tried to filter it out afterward by checking for a non-empty
        # result — that check doesn't work, since the over-broad walk
        # always finds *some* non-empty ancestor eventually).
        line_texts: list[str] = modal.evaluate(
            """
            (el) => Array.from(el.querySelectorAll('input[type="number"]')).slice(1).map((input) => {
                let node = input;
                while (node && !(node.textContent || '').includes('Location:')) {
                    node = node.parentElement;
                }
                return node ? node.textContent : '';
            })
            """
        )
        for i, text in enumerate(line_texts):
            if sku_or_name in text:
                return i
        raise ValueError(f"No Pick Items line found matching {sku_or_name!r} in {line_texts!r}")

    def mark_all_as_picked(self) -> None:
        """Shortcut button that fills every line's quantity to its full
        remaining amount in one click."""
        self._pick_modal().get_by_role("button", name="Mark All as Picked").click()

    def submit_complete_picking(self) -> None:
        """Confirmed live 2026-08-19: disabled while every line's quantity
        is 0 (can't complete a pick of nothing). If the total entered is
        LESS than the order's full remaining quantity, this does not
        finish the pick — it opens a second confirmation modal (see
        `choose_*` methods below); only a full-quantity submission
        completes immediately."""
        self._pick_modal().get_by_role("button", name="Complete Picking").click()
        self.page.wait_for_timeout(1000)

    def _incomplete_pick_modal(self):
        """Scope to the "Incomplete pick — what next?" confirmation modal
        that appears after `submit_complete_picking()` with a partial
        quantity."""
        return self.modal_scope("Incomplete pick", "Go back and keep picking")

    def choose_go_back_and_keep_picking(self) -> None:
        """Dismisses the confirmation and returns to the pick list without
        completing anything."""
        self._incomplete_pick_modal().get_by_role(
            "button", name="Go back and keep picking", exact=False
        ).click()

    def choose_leave_rest_unpicked(self) -> None:
        """Confirmed live 2026-08-19: ships the picked quantity now and
        leaves the remainder on the SAME order to be picked later — the
        order's status becomes "Partially Picked" and its next action
        becomes "Pack remaining (N)" for just the picked units. Confirmed
        these choice cards are real `<button>` elements whose accessible
        name concatenates both the bold title and the description line —
        `exact=False` is required."""
        self._incomplete_pick_modal().get_by_role(
            "button", name="Complete partial pick, leave rest as unpicked", exact=False
        ).click()
        self.page.wait_for_timeout(1500)

    def choose_cancel_rest(self) -> None:
        """Ships the picked quantity now and CANCELS the remaining unpicked
        units — confirmed live the app itself warns "this cannot be
        undone". Not yet exercised end-to-end by this suite (destructive;
        exercise with care in real test data)."""
        self._incomplete_pick_modal().get_by_role(
            "button", name="Complete partial pick, cancel the rest", exact=False
        ).click()
        self.page.wait_for_timeout(1500)

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

    # ---- Order detail: ORDER OPS (Reallocate / Split) — NEW, VERIFIED live 2026-08-13 --

    def open_order_details(self, order_number: str) -> None:
        """Opens the order detail modal for `order_number` via its row's
        "View" button."""
        self.order_row(order_number).get_by_role("button", name="View").click()
        self.page.wait_for_timeout(1000)

    def _order_details_modal(self):
        """Scope to the order detail modal.

        CORRECTED 2026-08-20 (Aug 19 order-queue rework): the modal
        heading changed from "Order Details: ORD-..." to just
        "Order ORD-..." (plus a status badge next to it) — dropping the
        word "Details" broke the old `modal_scope("Order Details", ...)`
        anchor entirely (zero matches, not a false-match like the Split
        modal trap — just nothing found). "NEXT ACTION" is a new, stable,
        modal-only label (the bar holding the primary action button plus
        Reallocate/Split/Cancel remaining) used as the anchor instead;
        "Close" is still the modal's own footer button."""
        return self.modal_scope("NEXT ACTION", "Close")

    def current_order_detail_warehouse(self) -> str:
        """Reads the "Warehouse: X" line on the order detail Overview tab."""
        text = self._order_details_modal().get_by_text("Warehouse:", exact=False).first.inner_text()
        return text.split("Warehouse:", 1)[1].strip()

    def start_reallocate_order(self) -> None:
        """Requires the order details modal to already be open (see
        `open_order_details()`). Click "Reallocate" — confirmed live
        2026-08-20 this now lives in the "NEXT ACTION" bar alongside the
        primary action button and "Split"/"Cancel remaining" (the old
        standalone "ORDER OPS" section/label no longer exists — see
        `_order_details_modal()`)."""
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
        "Split" — confirmed live 2026-08-20 this now lives in the "NEXT
        ACTION" bar (see `start_reallocate_order()`)."""
        self._order_details_modal().get_by_role("button", name="Split", exact=True).click()
        self.page.wait_for_timeout(800)

    def cancel_remaining_from_details(self) -> None:
        """Requires the order details modal to already be open. Confirmed
        live 2026-08-20: "Cancel remaining" is styled as a red text link
        rather than a bordered button but is still a real `role="button"`
        element, shown in the same "NEXT ACTION" bar as Reallocate/Split."""
        self._order_details_modal().get_by_role("button", name="Cancel remaining", exact=False).click()

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
