"""Order Ops: Combine — merges two or more orders into one new order.

NEW as of the Aug 19, 2026 order-queue rework (mentioned in the original
Aug 10 release notes as "Split/Combine Sales Orders" but never exercised
live until now). Confirmed live 2026-08-20 — see pages/orders_page.py's
module docstring for the full narrative. Combine is the counterpart to
Split (test_split_order.py): where Split forks part of ONE order into a
new sibling, Combine merges MULTIPLE whole orders into one new order.

Confirmed precondition: Combine is only enabled when every SELECTED
order belongs to the SAME customer — verified live by comparing a
same-customer pair (enabled) against a different-customer pair
(disabled). Confirmed end-to-end behaviour: clicking "Combine" opens a
"Combine Orders" confirmation modal reading "Merge N orders for
{customer} into one new order. Source orders will be cancelled." —
after confirming, the source orders don't just get a "Cancelled" badge,
they disappear from the list ENTIRELY (not findable even via direct
search), while a new order appears tagged "Combined" with a
"from ORD-X, ORD-Y" lineage line, a combined line-item quantity (sum of
both sources), and the sources' shared customer/channel/warehouse.

⚠️ REAL DATA WARNING: creates multiple real Orders and actually combines
some of them (irreversibly cancelling the sources) on the shared
test-phase instance (https://app.fridai.pro) — same caveat as
test_create_order.py, but note Combine's cancellation is NOT undoable
the way a throwaway test order normally would be inconsequential.
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

from data.test_emails import disposable_email
from pages.orders_page import OrdersPage

KNOWN_STOCKED_PRODUCT_SKU = "RaliP1"


def _create_order(orders: OrdersPage, page: Page, customer_name: str, email: str, qty: int) -> None:
    orders.goto()
    orders.wait_for_loaded()
    orders.start_create_order()
    orders.set_customer_name(customer_name)
    orders.set_customer_email(email)
    orders.set_channel("Direct to Consumer")
    orders.go_to_order_items()
    orders.add_line_item(KNOWN_STOCKED_PRODUCT_SKU, quantity=qty)
    orders.submit_new_order()
    orders.wait_for_loaded()
    page.wait_for_timeout(1000)  # settle before the next order's list read


def _order_numbers_for_customer(page: Page, customer_name: str) -> list[str]:
    """All distinct order numbers currently visible for `customer_name`.
    Reads each matching row directly rather than caching a value returned
    right after creation — confirmed live that reading .first immediately
    after creating a SECOND same-named order can race the list refresh
    and return the same (first) order number twice."""
    rows = page.locator("tr", has_text=customer_name)
    return [
        rows.nth(i).locator("td").nth(1).inner_text().strip().splitlines()[0]
        for i in range(rows.count())
    ]


@pytest.mark.regression
def test_combine_requires_same_customer(authenticated_page: Page) -> None:
    orders = OrdersPage(authenticated_page)
    unique_suffix = str(int(time.time()))

    # Same customer, two orders -> Combine should be enabled.
    same_name = f"Combine Precondition Same {unique_suffix}"
    same_email = disposable_email(f"combine-precond-same-{unique_suffix}")
    _create_order(orders, authenticated_page, same_name, same_email, qty=1)
    _create_order(orders, authenticated_page, same_name, same_email, qty=1)

    orders.goto()
    orders.wait_for_loaded()
    same_numbers = _order_numbers_for_customer(authenticated_page, same_name)
    assert len(set(same_numbers)) == 2, f"Expected 2 distinct orders, got {same_numbers}"

    orders.select_order_checkbox(same_numbers[0])
    orders.select_order_checkbox(same_numbers[1])
    expect(orders.combine_button()).to_be_enabled()
    orders.clear_selection()

    # Different customers, two orders -> Combine should be disabled.
    name_a = f"Combine Precondition A {unique_suffix}"
    email_a = disposable_email(f"combine-precond-a-{unique_suffix}")
    name_b = f"Combine Precondition B {unique_suffix}"
    email_b = disposable_email(f"combine-precond-b-{unique_suffix}")
    _create_order(orders, authenticated_page, name_a, email_a, qty=1)
    _create_order(orders, authenticated_page, name_b, email_b, qty=1)

    orders.goto()
    orders.wait_for_loaded()
    order_a = _order_numbers_for_customer(authenticated_page, name_a)[0]
    order_b = _order_numbers_for_customer(authenticated_page, name_b)[0]

    orders.select_order_checkbox(order_a)
    orders.select_order_checkbox(order_b)
    expect(orders.combine_button()).to_be_disabled()


@pytest.mark.regression
def test_combine_merges_orders_and_cancels_sources(authenticated_page: Page) -> None:
    orders = OrdersPage(authenticated_page)
    unique_suffix = str(int(time.time()))
    customer_name = f"Combine E2E Test {unique_suffix}"
    email = disposable_email(f"combine-e2e-test-{unique_suffix}")

    _create_order(orders, authenticated_page, customer_name, email, qty=2)
    _create_order(orders, authenticated_page, customer_name, email, qty=3)

    orders.goto()
    orders.wait_for_loaded()
    source_numbers = _order_numbers_for_customer(authenticated_page, customer_name)
    assert len(set(source_numbers)) == 2, f"Expected 2 distinct source orders, got {source_numbers}"
    source_a, source_b = source_numbers

    orders.select_order_checkbox(source_a)
    orders.select_order_checkbox(source_b)
    orders.combine_button().click()
    authenticated_page.wait_for_timeout(1000)

    modal = authenticated_page.locator("div").filter(has_text="Combine Orders").filter(has_text="Merge").last
    expect(modal).to_contain_text("Source orders will be cancelled")
    expect(modal).to_contain_text(source_a)
    expect(modal).to_contain_text(source_b)
    modal.get_by_role("button", name="Combine orders", exact=True).click()
    authenticated_page.wait_for_timeout(2000)

    # The sources are gone entirely -- not just re-labeled Cancelled.
    orders.goto()
    orders.wait_for_loaded()
    orders.search(source_a)
    authenticated_page.wait_for_timeout(1200)
    assert authenticated_page.locator("table tbody tr").count() == 0, (
        f"Expected source order {source_a} to be fully gone after combining, "
        "but it's still findable via search."
    )

    # A genuinely new order exists, tagged Combined, with both sources'
    # quantities summed and their lineage recorded.
    orders.goto()
    orders.wait_for_loaded()
    combined_row = authenticated_page.locator("tr", has_text="Combined").filter(has_text=customer_name)
    expect(combined_row).to_be_visible()
    expect(combined_row).to_contain_text(f"from {source_a}")
    expect(combined_row).to_contain_text(source_b)
    expect(combined_row).to_contain_text("5 ready to pick")  # 2 + 3 summed
