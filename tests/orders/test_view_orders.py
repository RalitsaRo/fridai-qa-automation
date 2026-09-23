"""View Orders — read-only checks against the real Orders list page.

Source: docs/order-management-guide.md § "Viewing Orders".
Locators VERIFIED 2026-07-16 against the live app. No side effects — this
test does not create, modify, or delete anything.

UPDATED 2026-08-19 for the visual rework of the order queue (see
pages/orders_page.py's module docstring): the page's H1 is now "Orders"
(was "Orders & Fulfillment"), and the standalone "Packing" column was
replaced by a combined "PROGRESS" column (bar + text like "5 ready to
pack") that folds packing progress and pick/pack/ship status into one
place.
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
def test_orders_table_has_progress_column(authenticated_page: Page) -> None:
    """Regression check, UPDATED 2026-08-19: this used to check for a
    standalone "Packing" column (a doc gap — neither getting-started.md
    nor order-management-guide.md mentioned it). The Aug 19 order-queue
    rework replaced it with a "PROGRESS" column that folds pick/pack/ship
    progress into one bar + text (e.g. "5 ready to pack") — still
    separate from the "STATUS" column, just renamed and richer. If this
    column disappears or merges into Status, that's worth noticing.
    """
    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    expect(authenticated_page.get_by_role("columnheader", name="PROGRESS")).to_be_visible()
    expect(authenticated_page.get_by_role("columnheader", name="STATUS")).to_be_visible()
