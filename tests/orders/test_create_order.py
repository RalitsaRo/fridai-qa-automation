"""Order creation happy path.

Source: docs/order-management-guide.md § "Creating Orders".
Flow VERIFIED 2026-07-16 against the live app — see pages/orders_page.py
and pages/products_page.py for exactly what was confirmed.

Uses the pre-existing product "RaliPN1" (SKU "RaliP1") rather than
creating a fresh one, because a freshly created Product has ZERO stock and
is NOT selectable in this step — see
test_new_product_without_stock_not_orderable.py. "RaliPN1" already has
received stock (confirmed 997 available) from an existing Purchase Order
(PO-3-000001), so it's a safe, known-good line item for exercising the
order-creation flow itself. Building Page Objects for Purchase
Orders/Receiving (the actual stock-provisioning flow) is tracked as a
follow-up in MEMORY.md, not done here.

⚠️ REAL DATA WARNING: BASE_URL points at https://app.fridai.pro. The
product owner has confirmed this is a test-phase environment (no
production exists yet), so creating throwaway data here is expected and
acceptable — but it's still a real, shared instance, not an isolated
per-test sandbox. This test creates one real Order every time it runs.

Also confirmed live 2026-07-16: use `data.test_emails.disposable_email()`
for the customer email, NOT a `@....local` address — the real backend's
`POST /crm/customers` call (triggered by submitting this form) strictly
validates email deliverability and rejects `.local` as a reserved
special-use domain with an HTTP 422. See data/test_emails.py.
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

from data.test_emails import disposable_email
from pages.orders_page import OrdersPage

KNOWN_STOCKED_PRODUCT_SKU = "RaliP1"


@pytest.mark.regression
def test_create_and_submit_order(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    customer_name = f"Automation Test Customer {unique_suffix}"

    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    orders.start_create_order()
    orders.set_customer_name(customer_name)
    orders.set_customer_email(disposable_email(f"automation-test-{unique_suffix}"))
    orders.set_channel("Direct to Consumer")
    orders.go_to_order_items()
    orders.add_line_item(KNOWN_STOCKED_PRODUCT_SKU, quantity=1)
    orders.submit_new_order()

    # Back on the Orders & Fulfillment list — confirm the new order appears.
    orders.wait_for_loaded()
    expect(authenticated_page.get_by_text(customer_name)).to_be_visible()
