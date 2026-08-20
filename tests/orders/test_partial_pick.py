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

KNOWN_STOCKED_PRODUCT_SKU = "RaliP1"
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
