"""Regression test for the exact dependency flagged during review: a new
Fridai user cannot create an order until at least one Product exists.

VERIFIED 2026-07-16: Order creation's "Order Items" step (Step 2) is a
live search against the existing Products catalog with NO inline
"create product" fallback. Searching a real SKU returns a clickable
suggestion showing name, SKU, and live available stock (e.g.
"RaliPN1 (RaliP1) — 997"); searching a SKU that doesn't exist returns
nothing to click. This test asserts the latter half of that — the
no-results case — since it's the one that actually blocks a new user and
is safe to run repeatedly with no side effects (no product/order is
created).

If this test ever starts failing because Fridai adds an inline
"create product from here" option, that's a genuine product improvement —
update pages/orders_page.py's docstring and Step 5 of
Friday_New_User_Getting_Started_Guide.docx accordingly rather than just
deleting this test.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from data.test_emails import disposable_email
from pages.orders_page import OrdersPage


@pytest.mark.regression
def test_order_items_search_finds_nothing_for_unknown_product(authenticated_page: Page) -> None:
    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    orders.start_create_order()
    orders.set_customer_name("Regression Test Customer")
    orders.set_customer_email(disposable_email("regression-test"))
    orders.go_to_order_items()

    bogus_sku = "ZZZ-DEFINITELY-NOT-A-REAL-PRODUCT-9999"
    modal = orders._order_items_modal()  # noqa: SLF001 — test-only introspection
    modal.get_by_placeholder("Scan barcode, SKU, or search by name...").fill(bogus_sku)
    authenticated_page.wait_for_timeout(1200)

    expect(modal.get_by_text(bogus_sku, exact=False)).to_have_count(0)
