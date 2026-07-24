"""Regression test for the FULL dependency chain uncovered during review —
this is the precise version of "you need products to create an order":

VERIFIED 2026-07-16, live: a Product record existing in the catalog is
NOT sufficient on its own. A freshly created product ("Automation Test
Product ...", SKU "TEST-AUTO-...") did not appear in the Order Items
product search under any query (full name, full SKU, or partial
substrings of either) — while the pre-existing "RaliPN1" (SKU "RaliP1"),
which has 997 units of received stock, appeared immediately.

Confirmed root cause: Products > (row) > "Inventory" navigates to
/inventory, which for a brand-new product shows "No inventory items" with
the explanatory text "Inventory is created when you receive purchase
orders. Create and receive a PO to get started." So the real prerequisite
chain for creating an order is:

    Product (catalog entry, zero stock)
        -> Purchase Order (for that product, from a Supplier)
            -> Receive the Purchase Order
                -> stock becomes "Available"
                    -> product now appears in Order Items search
                        -> order can be created

This test proves the middle of that chain (product exists, no PO/receipt
yet -> still not orderable) using only ProductsPage and OrdersPage, since
Purchase Orders / Receiving don't have Page Objects yet (see MEMORY.md).
No order is created — this only proves absence from the search.
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

from data.test_emails import disposable_email
from pages.orders_page import OrdersPage
from pages.products_page import ProductsPage


@pytest.mark.regression
def test_new_product_without_stock_not_orderable(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    sku = f"TEST-AUTO-{unique_suffix}"
    product_name = f"Automation Test Product {unique_suffix}"

    products = ProductsPage(authenticated_page)
    products.goto()
    products.wait_for_loaded()
    products.add_product(sku=sku, name=product_name)

    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    orders.start_create_order()
    orders.set_customer_name("Stock Regression Test Customer")
    orders.set_customer_email(disposable_email("stock-regression-test"))
    orders.go_to_order_items()

    modal = orders._order_items_modal()  # noqa: SLF001 — test-only introspection
    modal.get_by_placeholder("Scan barcode, SKU, or search by name...").fill(sku)
    authenticated_page.wait_for_timeout(1200)

    expect(modal.get_by_text(sku, exact=False)).to_have_count(0)
