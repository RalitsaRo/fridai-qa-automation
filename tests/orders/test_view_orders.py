"""View Orders — read-only checks against the real Orders & Fulfillment page.

Source: docs/order-management-guide.md § "Viewing Orders".
Locators VERIFIED 2026-07-16 against the live app. No side effects — this
test does not create, modify, or delete anything.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.dashboard_page import DashboardPage
from pages.orders_page import OrdersPage


@pytest.mark.smoke
def test_orders_page_reachable_via_nav(authenticated_page: Page, base_url: str) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.wait_for_loaded()
    dashboard.open_orders()

    orders = OrdersPage(authenticated_page)
    orders.wait_for_loaded()

    expect(authenticated_page).to_have_url(f"{base_url}/orders-list")


@pytest.mark.regression
def test_orders_table_has_packing_column(authenticated_page: Page) -> None:
    """Regression check for a Friday documentation gap: neither
    getting-started.md nor order-management-guide.md mention that Packing
    progress is tracked as a column separate from order Status. If this
    column disappears, the docs would (for once) be right — worth noticing.
    """
    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    expect(authenticated_page.get_by_role("columnheader", name="Packing")).to_be_visible()
    expect(authenticated_page.get_by_role("columnheader", name="Status")).to_be_visible()
