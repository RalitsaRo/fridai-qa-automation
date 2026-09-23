"""Partial picking — a first-class flow in the Aug 19, 2026 order-queue rework.

Confirmed live 2026-08-19: the Pick Order modal's per-line quantity input
defaults to 0 (not the full remaining amount), and completing with less
than the full quantity opens a second "Incomplete pick — what next?"
confirmation with three explicit choices: go back and keep picking,
complete partial pick and leave the rest unpicked, or complete partial
pick and cancel the rest. This test exercises the middle (non-destructive)
choice end to end and asserts the resulting order state.

See pages/orders_page.py's module docstring for the full narrative.

⚠️ REAL DATA WARNING: creates one real Order (quantity 10) and partially
picks it on the shared test-phase instance (https://app.fridai.pro) —
same caveat as test_create_order.py.
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

from data.test_emails import disposable_email
from pages.orders_page import OrdersPage
from pages.products_page import ProductsPage
from pages.purchase_orders_page import PurchaseOrdersPage
from pages.receiving_page import ReceivingPage

KNOWN_STOCKED_PRODUCT_SKU = "RaliP1"
KNOWN_SUPPLIER = "Rali test supplier"
ORIGINAL_QUANTITY = 10
PICK_QUANTITY = 4


@pytest.mark.regression
def test_partial_pick_leaves_remainder_on_same_order(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    customer_name = f"Partial Pick Test Customer {unique_suffix}"

    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    # 1. Create a fresh, multi-unit order so there's something to
    #    partially pick.
    orders.start_create_order()
    orders.set_customer_name(customer_name)
    orders.set_customer_email(disposable_email(f"partial-pick-test-{unique_suffix}"))
    orders.set_channel("Direct to Consumer")
    orders.go_to_order_items()
    orders.add_line_item(KNOWN_STOCKED_PRODUCT_SKU, quantity=ORIGINAL_QUANTITY)
    orders.submit_new_order()
    orders.wait_for_loaded()

    order_row = authenticated_page.locator("tr", has_text=customer_name)
    expect(order_row).to_be_visible()
    order_number = order_row.locator("td").nth(1).inner_text().strip().splitlines()[0]

    # Sanity check: a fresh order is fully "ready to pick".
    assert orders.next_action_label(order_number).startswith("Pick")

    # 2. Pick only PICK_QUANTITY of the ORIGINAL_QUANTITY units.
    orders.click_next_action(order_number)
    orders.set_pick_quantity(PICK_QUANTITY)
    orders.submit_complete_picking()

    # 3. The "Incomplete pick" confirmation should appear -- choose to
    #    leave the rest unpicked (non-destructive).
    orders.choose_leave_rest_unpicked()

    # 4. Back on the list, the order should show "Partially Picked" and
    #    its next action should be to pack just the picked units.
    orders.goto()
    orders.wait_for_loaded()
    assert orders.order_row_status(order_number) == "Partially Picked", (
        f"Expected status 'Partially Picked' after picking {PICK_QUANTITY}/"
        f"{ORIGINAL_QUANTITY} units, got {orders.order_row_status(order_number)!r}"
    )
    expect(orders.order_row(order_number)).to_contain_text(f"{PICK_QUANTITY} ready to pack")
    assert orders.next_action_label(order_number) == f"Pack remaining ({PICK_QUANTITY})", (
        f"Expected next action 'Pack remaining ({PICK_QUANTITY})', got "
        f"{orders.next_action_label(order_number)!r}"
    )


@pytest.mark.regression
def test_complete_picking_disabled_at_zero_quantity(authenticated_page: Page) -> None:
    """Boundary check: confirmed live 2026-08-19 the "Complete Picking"
    button is disabled while every line's quantity is 0 — you can't
    complete a pick of nothing."""
    unique_suffix = str(int(time.time()))
    customer_name = f"Zero Qty Pick Test Customer {unique_suffix}"

    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    orders.start_create_order()
    orders.set_customer_name(customer_name)
    orders.set_customer_email(disposable_email(f"zero-qty-pick-test-{unique_suffix}"))
    orders.set_channel("Direct to Consumer")
    orders.go_to_order_items()
    orders.add_line_item(KNOWN_STOCKED_PRODUCT_SKU, quantity=1)
    orders.submit_new_order()
    orders.wait_for_loaded()

    order_row = authenticated_page.locator("tr", has_text=customer_name)
    expect(order_row).to_be_visible()
    order_number = order_row.locator("td").nth(1).inner_text().strip().splitlines()[0]

    orders.click_next_action(order_number)
    modal = orders._pick_modal()  # noqa: SLF001 — test-only introspection
    expect(modal.get_by_role("button", name="Complete Picking")).to_be_disabled()


CANCEL_ORIGINAL_QUANTITY = 6
CANCEL_PICK_QUANTITY = 2


@pytest.mark.regression
def test_cancel_the_rest_marks_order_fully_picked(authenticated_page: Page) -> None:
    """The destructive third choice: "Complete partial pick, cancel the
    rest". Confirmed live 2026-08-20 this is NOT the same end-state as
    "leave rest as unpicked" — cancelling the remainder means there's
    nothing left pending, so the order goes all the way to status
    "Picked" (not "Partially Picked") with a plain "Pack (N)" next action
    (no "remaining" wording), since the cancelled units are no longer
    part of what's left to do. The order's own PROGRESS/next-action
    reflect only the picked quantity — the cancelled units simply vanish
    from the outstanding work, they don't show up as a separate tracked
    shortfall anywhere on the list view.

    ⚠️ Destructive and irreversible on the real order (per the app's own
    warning in the confirmation modal) — uses a dedicated throwaway order
    for exactly this reason."""
    unique_suffix = str(int(time.time()))
    customer_name = f"Cancel Rest Test Customer {unique_suffix}"

    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    orders.start_create_order()
    orders.set_customer_name(customer_name)
    orders.set_customer_email(disposable_email(f"cancel-rest-test-{unique_suffix}"))
    orders.set_channel("Direct to Consumer")
    orders.go_to_order_items()
    orders.add_line_item(KNOWN_STOCKED_PRODUCT_SKU, quantity=CANCEL_ORIGINAL_QUANTITY)
    orders.submit_new_order()
    orders.wait_for_loaded()

    order_row = authenticated_page.locator("tr", has_text=customer_name)
    expect(order_row).to_be_visible()
    order_number = order_row.locator("td").nth(1).inner_text().strip().splitlines()[0]

    orders.click_next_action(order_number)
    orders.set_pick_quantity(CANCEL_PICK_QUANTITY)
    orders.submit_complete_picking()
    orders.choose_cancel_rest()

    orders.goto()
    orders.wait_for_loaded()
    assert orders.order_row_status(order_number) == "Picked", (
        f"Expected status 'Picked' after cancelling the {CANCEL_ORIGINAL_QUANTITY - CANCEL_PICK_QUANTITY} "
        f"unpicked units, got {orders.order_row_status(order_number)!r}"
    )
    assert orders.order_row_progress_text(order_number) == f"{CANCEL_PICK_QUANTITY} ready to pack", (
        f"Expected progress '{CANCEL_PICK_QUANTITY} ready to pack', got "
        f"{orders.order_row_progress_text(order_number)!r}"
    )
    assert orders.next_action_label(order_number) == f"Pack ({CANCEL_PICK_QUANTITY})", (
        f"Expected next action 'Pack ({CANCEL_PICK_QUANTITY})' (no 'remaining' -- "
        f"nothing is left pending once the rest is cancelled), got "
        f"{orders.next_action_label(order_number)!r}"
    )


@pytest.mark.regression
def test_multiline_order_partial_pick_sums_across_lines(authenticated_page: Page) -> None:
    """A 2-line order, picked fully on one line and partially on the
    other. Confirmed live 2026-08-20: the "Pick Items" list's DISPLAY
    order does NOT necessarily match the order lines were added to the
    order in (seen sorted differently, likely by product name) — this
    test locates each line by SKU via `pick_line_index_for_sku()` rather
    than assuming a fixed index, which is exactly the trap a naive
    index-based test would fall into.

    Confirmed the order-level PROGRESS/next-action reflect the SUM of
    picked units across every line, not a per-line breakdown: picking
    5/5 of one line and 3/8 of another (8 of 13 total) correctly showed
    order status "Partially Picked" and next action "Pack remaining (8)".
    """
    unique_suffix = str(int(time.time()))
    second_sku = f"TEST-MULTILINE-{unique_suffix}"
    second_product_name = f"Multiline Pick Test Product {unique_suffix}"
    second_qty_available = 8
    second_qty_to_pick = 3
    first_qty = 5  # RaliP1, picked in full

    # 1. Create and fully stock a second product so the order has two
    #    genuinely distinct, independently-stocked lines.
    products = ProductsPage(authenticated_page)
    products.goto()
    products.wait_for_loaded()
    products.add_product(sku=second_sku, name=second_product_name)

    purchase_orders = PurchaseOrdersPage(authenticated_page)
    purchase_orders.goto()
    purchase_orders.wait_for_loaded()
    purchase_orders.start_create_po()
    purchase_orders.set_supplier(KNOWN_SUPPLIER)
    purchase_orders.set_receiving_location(index=1)
    purchase_orders.set_initial_status("Placed")
    purchase_orders.go_to_po_items()
    purchase_orders.add_po_line_item(second_sku, quantity=second_qty_available)
    purchase_orders.submit_create_po()
    purchase_orders.wait_for_loaded()
    po_number = purchase_orders.first_po_number()
    purchase_orders.record_asn_skip_import(po_number)
    purchase_orders.wait_for_loaded()
    purchase_orders.release_for_receiving(po_number)
    purchase_orders.wait_for_loaded()
    expect(authenticated_page.locator("tr", has_text=po_number)).to_contain_text("Ready to receive")

    receiving = ReceivingPage(authenticated_page)
    receiving.goto()
    receiving.wait_for_loaded()
    receiving.start_receiving(po_number)
    receiving.receive_full_line(second_sku)
    receiving.finish_receiving()

    # 2. Create a 2-line order: RaliP1 (first_qty) + the new SKU (second_qty_available).
    orders = OrdersPage(authenticated_page)
    customer_name = f"Multiline Pick Test Customer {unique_suffix}"
    orders.goto()
    orders.wait_for_loaded()
    orders.start_create_order()
    orders.set_customer_name(customer_name)
    orders.set_customer_email(disposable_email(f"multiline-pick-test-{unique_suffix}"))
    orders.set_channel("Direct to Consumer")
    orders.go_to_order_items()
    orders.add_line_item(KNOWN_STOCKED_PRODUCT_SKU, quantity=first_qty)
    orders.add_line_item(second_sku, quantity=second_qty_available)
    orders.submit_new_order()
    orders.wait_for_loaded()

    order_row = authenticated_page.locator("tr", has_text=customer_name)
    expect(order_row).to_be_visible()
    order_number = order_row.locator("td").nth(1).inner_text().strip().splitlines()[0]
    total_items = first_qty + second_qty_available

    # 3. Pick RaliP1 in full and the new SKU partially -- located by SKU,
    #    NOT assumed index, since display order isn't add-order.
    orders.click_next_action(order_number)
    idx_first = orders.pick_line_index_for_sku(KNOWN_STOCKED_PRODUCT_SKU)
    idx_second = orders.pick_line_index_for_sku(second_sku)
    assert idx_first != idx_second, "Both SKUs resolved to the same Pick Items line index"

    orders.set_pick_quantity(first_qty, line_index=idx_first)
    orders.set_pick_quantity(second_qty_to_pick, line_index=idx_second)
    orders.submit_complete_picking()
    orders.choose_leave_rest_unpicked()

    # 4. The order-level progress reflects the SUM of both lines' picked
    #    quantities (first_qty + second_qty_to_pick), not either line alone.
    total_picked = first_qty + second_qty_to_pick
    orders.goto()
    orders.wait_for_loaded()
    assert orders.order_row_status(order_number) == "Partially Picked", (
        f"Expected status 'Partially Picked', got {orders.order_row_status(order_number)!r}"
    )
    assert orders.order_row_progress_text(order_number) == f"{total_picked} ready to pack", (
        f"Expected progress '{total_picked} ready to pack' ({first_qty} + "
        f"{second_qty_to_pick} summed across both lines), got "
        f"{orders.order_row_progress_text(order_number)!r}"
    )
    assert orders.next_action_label(order_number) == f"Pack remaining ({total_picked})", (
        f"Expected next action 'Pack remaining ({total_picked})' of {total_items} "
        f"total items, got {orders.next_action_label(order_number)!r}"
    )
