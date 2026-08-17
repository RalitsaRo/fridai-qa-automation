"""Order Ops: Split — forks part of an order's units into a new sibling order.

NEW as of the Aug 10, 2026 multi-warehouse release. Verified live
2026-08-13 — see pages/orders_page.py's "ORDER OPS" section for the full
narrative, including how this differs from Reallocate
(test_reallocate_order.py): Split operates at individual sub-line
granularity and creates a brand-new sibling order, rather than moving the
whole order.

Confirmed live 2026-08-13 with a real 10-unit order: splitting off 3
units left the parent order at 7/7 allocated and produced a new sibling
order at 3/3 allocated, with `orders_total_count()` going from 26 to 27 —
this test asserts the same shape of result (allowing for whatever the
real starting count is at run time).

⚠️ REAL DATA WARNING: creates one real Order (quantity 10) and splits it
into two on the shared test-phase instance (https://app.fridai.pro) —
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
SPLIT_QUANTITY = 3


def _visible_order_numbers(page: Page) -> set[str]:
    """Order numbers on the current (first) page of the Orders table. The
    Order column's cell bundles the order number with a "N lines" /
    SKU-allocation summary as extra lines in the same <td> (confirmed
    live) — only the first line is the stable order number."""
    return {
        text.strip().splitlines()[0]
        for text in page.locator("table tbody tr td:nth-child(2)").all_inner_texts()
    }


@pytest.mark.regression
def test_split_order_creates_sibling_and_reduces_parent(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    customer_name = f"Split Test Customer {unique_suffix}"

    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    # 1. Create a fresh, multi-unit order so there's something to split.
    orders.start_create_order()
    orders.set_customer_name(customer_name)
    orders.set_customer_email(disposable_email(f"split-test-{unique_suffix}"))
    orders.set_channel("Direct to Consumer")
    orders.go_to_order_items()
    orders.add_line_item(KNOWN_STOCKED_PRODUCT_SKU, quantity=ORIGINAL_QUANTITY)
    orders.submit_new_order()
    orders.wait_for_loaded()

    order_row = authenticated_page.locator("tr", has_text=customer_name)
    expect(order_row).to_be_visible()
    # The Order column's cell bundles the order number with a "N lines" /
    # SKU-allocation summary as extra lines in the same <td> (confirmed
    # live) — the order number itself is always the first line.
    order_number = order_row.locator("td").nth(1).inner_text().strip().splitlines()[0]

    orders_before = orders.orders_total_count()
    known_order_numbers_before = _visible_order_numbers(authenticated_page)

    # 2. Split off SPLIT_QUANTITY units into a new sibling order (same
    #    warehouse — target left at "Same as parent order").
    orders.open_order_details(order_number)
    orders.start_split_order()
    orders.set_split_quantity(SPLIT_QUANTITY)
    orders.submit_split()

    # 3. One more order should now exist overall...
    orders.goto()
    orders.wait_for_loaded()
    assert orders.orders_total_count() == orders_before + 1, (
        "Expected exactly one new sibling order after splitting, got a "
        f"total count of {orders.orders_total_count()} (was {orders_before})."
    )

    # 4. ...and it should be a genuinely new order number, distinct from
    #    the parent. Compare just the order-number substrings, not the
    #    full cell text — the PARENT row's own cell text also legitimately
    #    changes after a split (its allocation summary goes from e.g.
    #    "10/10" to "7/7 allocated"), which would otherwise show up as a
    #    false "new" entry alongside the real sibling order.
    known_order_numbers_after = _visible_order_numbers(authenticated_page)
    new_order_numbers = known_order_numbers_after - known_order_numbers_before
    assert len(new_order_numbers) == 1, (
        f"Expected exactly one new order number to appear, got {new_order_numbers!r}"
    )
    sibling_order_number = next(iter(new_order_numbers))
    assert sibling_order_number != order_number

    # 5. The parent's row should reflect the reduced quantity, and the
    #    sibling's should reflect the moved quantity.
    expect(orders.order_row(order_number)).to_contain_text(
        f"{ORIGINAL_QUANTITY - SPLIT_QUANTITY}/{ORIGINAL_QUANTITY - SPLIT_QUANTITY} allocated"
    )
    expect(orders.order_row(sibling_order_number)).to_contain_text(
        f"{SPLIT_QUANTITY}/{SPLIT_QUANTITY} allocated"
    )
