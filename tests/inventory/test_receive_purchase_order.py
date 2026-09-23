"""Full stock-provisioning chain, end to end: Product -> Purchase Order ->
Record ASN -> Release for receiving -> Receive -> product becomes
orderable.

This is the test that fully proves what test_new_product_without_stock_
not_orderable.py only proves the absence side of: not just "a new product
has no stock," but "here's the complete, real workflow that gives it
stock." Confirmed live 2026-07-16 — see pages/purchase_orders_page.py and
pages/receiving_page.py for the full narrative and the caveats (the
non-functional location <select>, the Cyrillic-homoglyph location codes,
the two-step "Record ASN"/"Release for receiving" confirmations).

Reuses the pre-existing "Rali test supplier" (Suppliers has no Page Object
yet — same pattern as reusing "RaliPN1" in test_create_order.py before
this test existed).

⚠️ REAL DATA: creates one Product and one Purchase Order every run. Fine
given the confirmed test-phase environment.
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
def test_receiving_a_purchase_order_makes_a_product_orderable(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    sku = f"TEST-PO-{unique_suffix}"
    product_name = f"PO Chain Test Product {unique_suffix}"
    quantity = 25

    # 1. Create a fresh, zero-stock product.
    products = ProductsPage(authenticated_page)
    products.goto()
    products.wait_for_loaded()
    products.add_product(sku=sku, name=product_name)

    # 2. Create a Purchase Order for it.
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

    # The newly created PO is the most recent, so it's the first table row.
    purchase_orders.wait_for_loaded()
    po_number = purchase_orders.first_po_number()
    assert po_number.startswith("PO-"), f"Expected a PO number in the first row, got {po_number!r}"

    # 3. Record ASN (Placed -> Supplier shipped), then release for
    #    receiving (Supplier shipped -> Ready to receive).
    purchase_orders.record_asn_skip_import(po_number)
    purchase_orders.wait_for_loaded()
    purchase_orders.release_for_receiving(po_number)
    purchase_orders.wait_for_loaded()
    expect(authenticated_page.locator("tr", has_text=po_number)).to_contain_text("Ready to receive")

    # 4. Receive it.
    receiving = ReceivingPage(authenticated_page)
    receiving.goto()
    receiving.wait_for_loaded()
    receiving.start_receiving(po_number)
    receiving.receive_full_line(sku)
    receiving.finish_receiving()

    # 5. Confirm the product is now orderable with the received quantity.
    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()
    orders.start_create_order()
    orders.set_customer_name("PO Chain Verification Customer")
    orders.set_customer_email(f"po-chain-verify-{unique_suffix}@friday-automation-test.com")
    orders.go_to_order_items()
    order_items_modal = orders._order_items_modal()  # noqa: SLF001 — test-only introspection
    order_items_modal.get_by_placeholder("Scan barcode, SKU, or search by name...").fill(sku)
    authenticated_page.wait_for_timeout(1200)

    expect(order_items_modal.get_by_text(f"{product_name} ({sku})", exact=False)).to_be_visible()
    expect(order_items_modal.get_by_text(str(quantity), exact=False)).to_be_visible()
