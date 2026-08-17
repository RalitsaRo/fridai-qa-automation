"""Order Ops: Reallocate — moves a whole order to a different warehouse.

NEW as of the Aug 10, 2026 multi-warehouse release. Verified live
2026-08-13 — see pages/orders_page.py's "ORDER OPS" section for the full
narrative, including how this differs from Split (test_split_order.py):
Reallocate is all-or-nothing (no sibling order, no per-unit control).

Confirmed live 2026-08-13: reallocating doesn't just relabel the order's
Warehouse column — the order actually leaves its current warehouse's
scope. This test asserts BOTH sides of that: the order disappears from
its original warehouse's Orders list, and reappears under the target
warehouse once the global selector is switched there.

⚠️ REAL DATA WARNING: creates one real Order and moves it between real
warehouses on the shared test-phase instance (https://app.fridai.pro) —
same caveat as test_create_order.py.
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

from data.test_emails import disposable_email
from pages.orders_page import OrdersPage

KNOWN_STOCKED_PRODUCT_SKU = "RaliP1"


@pytest.mark.regression
def test_reallocate_order_moves_it_to_target_warehouse(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    customer_name = f"Reallocate Test Customer {unique_suffix}"

    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()
    origin_warehouse = orders.current_active_warehouse()

    # 1. Create a fresh order in whichever warehouse is currently active.
    orders.start_create_order()
    orders.set_customer_name(customer_name)
    orders.set_customer_email(disposable_email(f"reallocate-test-{unique_suffix}"))
    orders.set_channel("Direct to Consumer")
    orders.go_to_order_items()
    orders.add_line_item(KNOWN_STOCKED_PRODUCT_SKU, quantity=1)
    orders.submit_new_order()
    orders.wait_for_loaded()

    order_row = authenticated_page.locator("tr", has_text=customer_name)
    expect(order_row).to_be_visible()
    # The Order column's cell bundles the order number with a "N lines" /
    # SKU-allocation summary as extra lines in the same <td> (confirmed
    # live) — the order number itself is always the first line.
    order_number = order_row.locator("td").nth(1).inner_text().strip().splitlines()[0]

    # 2. Open it and reallocate to a different warehouse.
    orders.open_order_details(order_number)
    assert origin_warehouse in orders.current_order_detail_warehouse()

    orders.start_reallocate_order()
    options = orders.reallocate_target_warehouse_options()
    target_warehouse = next(
        opt for opt in options if opt not in ("Select warehouse", "") and opt != origin_warehouse
    )
    orders.set_reallocate_target_warehouse(target_warehouse)
    orders.submit_reallocate()

    # 3. It should be gone from the origin warehouse's list...
    orders.goto()
    orders.wait_for_loaded()
    assert not orders.order_row_visible(order_number), (
        f"Expected {order_number} to disappear from {origin_warehouse}'s "
        "Orders list after reallocating, but it's still there."
    )

    # 4. ...and present under the target warehouse, with the Warehouse
    #    column updated to match.
    orders.set_active_warehouse(target_warehouse)
    orders.wait_for_loaded()
    assert orders.order_row_visible(order_number), (
        f"Expected {order_number} to appear under {target_warehouse} after "
        "reallocating, but it wasn't found there."
    )
    assert target_warehouse in orders.order_row_warehouse(order_number)
