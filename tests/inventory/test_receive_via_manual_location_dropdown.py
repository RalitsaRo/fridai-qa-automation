"""Regression test for a corrected finding: the "Or select location
manually" dropdown on the Receiving screen DOES work.

CORRECTED 2026-08-17 — a prior finding (2026-07-16) wrongly called this
dropdown non-functional. Re-verified live: selecting an option alone does
nothing visible (no request, step unchanged), but the screen's own
instruction text — "Scan location or select from list, then press Enter
to confirm." — was missed by the original check. Selecting an option and
pressing Enter fires the real `POST /crm/purchase-orders/{id}/receive`
and completes the line, identical to the scan-text path
(`ReceivingPage.scan_location()`). See `ReceivingPage.select_location_manually()`.

This test exercises the dropdown path end to end as its own regression
guard, complementing test_receive_purchase_order.py (which exercises the
scan/type path).

⚠️ REAL DATA WARNING: creates one real Product and one real Purchase
Order every run — same caveat as test_receive_purchase_order.py.
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

from pages.orders_page import OrdersPage
from pages.products_page import ProductsPage
from pages.purchase_orders_page import PurchaseOrdersPage
from pages.receiving_page import ReceivingPage

KNOWN_SUPPLIER = "Rali test supplier"


@pytest.mark.regression
def test_receiving_via_manual_location_dropdown_completes_the_line(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    sku = f"TEST-DROPDOWN-{unique_suffix}"
    product_name = f"Manual Location Dropdown Test Product {unique_suffix}"
    quantity = 5

    products = ProductsPage(authenticated_page)
    products.goto()
    products.wait_for_loaded()
    products.add_product(sku=sku, name=product_name)

    purchase_orders = PurchaseOrdersPage(authenticated_page)
    purchase_orders.goto()
    purchase_orders.wait_for_loaded()
    purchase_orders.start_create_po()
    purchase_orders.set_supplier(KNOWN_SUPPLIER)
    purchase_orders.set_receiving_location(index=1)
    purchase_orders.set_initial_status("Placed")
    purchase_orders.go_to_po_items()
    purchase_orders.add_po_line_item(sku, quantity=quantity)
    purchase_orders.submit_create_po()

    purchase_orders.wait_for_loaded()
    po_number = purchase_orders.first_po_number()

    purchase_orders.record_asn_skip_import(po_number)
    purchase_orders.wait_for_loaded()
    purchase_orders.release_for_receiving(po_number)
    purchase_orders.wait_for_loaded()
    # Poll for the status flip rather than a fixed sleep — matches
    # test_receive_purchase_order.py's proven pattern.
    expect(authenticated_page.locator("tr", has_text=po_number)).to_contain_text("Ready to receive")

    receiving = ReceivingPage(authenticated_page)
    receiving.goto()
    receiving.wait_for_loaded()
    receiving.start_receiving(po_number)

    receiving.scan_product(sku)
    authenticated_page.wait_for_timeout(500)
    receiving.accept_default_quantity()
    authenticated_page.wait_for_timeout(500)

    # The dropdown path, instead of scan_location().
    receiving.select_location_manually(index=1)
    authenticated_page.wait_for_timeout(1500)

    expect(authenticated_page.get_by_text("Complete!", exact=False)).to_be_visible()
    receiving.finish_receiving()
    authenticated_page.wait_for_timeout(1500)

    # Confirm the product is now orderable with the received quantity.
    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()
    orders.start_create_order()
    orders.set_customer_name("Dropdown Verification Customer")
    orders.set_customer_email(f"dropdown-verify-{unique_suffix}@friday-automation-test.com")
    orders.go_to_order_items()
    order_items_modal = orders._order_items_modal()  # noqa: SLF001 — test-only introspection
    order_items_modal.get_by_placeholder("Scan barcode, SKU, or search by name...").fill(sku)
    authenticated_page.wait_for_timeout(1200)

    expect(order_items_modal.get_by_text(f"{product_name} ({sku})", exact=False)).to_be_visible()
    expect(order_items_modal.get_by_text(str(quantity), exact=False)).to_be_visible()
