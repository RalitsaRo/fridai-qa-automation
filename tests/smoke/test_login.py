"""Smoke test: confirm login works and lands on the Dashboard.

Source: docs/getting-started.md § "Logging In" (First Time Login).
Locators VERIFIED 2026-07-16 against the live app — see pages/login_page.py
and pages/dashboard_page.py for what was actually confirmed (the real
dashboard is a widget board, not the Active-Orders/Inventory-Summary layout
the docs describe).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.dashboard_page import DashboardPage


@pytest.mark.smoke
def test_login_lands_on_dashboard(authenticated_page: Page) -> None:
    dashboard = DashboardPage(authenticated_page)
    dashboard.wait_for_loaded()

    expect(dashboard.add_widget_button()).to_be_visible()
