"""Page Object for the Fridai Dashboard (post-login landing page).

VERIFIED 2026-07-16 against the live app. Reality diverges substantially
from docs/getting-started.md § "Dashboard Overview", which describes
Active Orders / Inventory Summary / Recent Activity / Quick Actions —
**none of that exists**. The real dashboard is a widget board:
- H1 "Dashboard" + subtitle "Customize your dashboard with widgets"
- "+ Add Widget" button
- A default "Best Selling Products" widget with an "All time" range filter

The real left-nav is a nested accordion, not the flat bar the docs describe:
Dashboard (+ "Dashboard Pulse" sub-item) / Inventory Management (Products,
Inventory, Stock Movements, Cycle Count Tasks, Purchase Orders, Receiving,
Locations) / Orders & Fulfillment (Orders, Returns, Picking Tasks, Packing
Tasks, Shipping Tasks) / CRM & Suppliers (Customers, Suppliers) / Settings
(User Management, Integrations, Print stations). Nav helpers live on
`BasePage` (`open_nav_section` / `click_nav_item`) since the nav persists
across every authenticated page.
"""

from __future__ import annotations

from pages.base_page import BasePage


class DashboardPage(BasePage):
    """The Fridai Dashboard / home screen (widget board)."""

    path = "/dashboard"

    # ---- Readiness ----------------------------------------------------------

    def wait_for_loaded(self, timeout: int = 10_000) -> None:
        self.by_role("heading", "Dashboard").wait_for(state="visible", timeout=timeout)

    # ---- Widgets --------------------------------------------------------------

    def add_widget_button(self):
        return self.by_role("button", "+ Add Widget")

    def best_selling_products_widget(self):
        return self.by_role("heading", "Best Selling Products")

    # ---- Navigation (confirmed nested-accordion structure) -------------------

    def open_orders(self) -> None:
        self.open_nav_section("Orders & Fulfillment")
        self.click_nav_item("Orders")

    def open_inventory(self) -> None:
        self.open_nav_section("Inventory Management")
        self.click_nav_item("Inventory")

    def open_products(self) -> None:
        self.open_nav_section("Inventory Management")
        self.click_nav_item("Products")

    def open_locations(self) -> None:
        self.open_nav_section("Inventory Management")
        self.click_nav_item("Locations")

    def open_purchase_orders(self) -> None:
        self.open_nav_section("Inventory Management")
        self.click_nav_item("Purchase Orders")

    def open_customers(self) -> None:
        self.open_nav_section("CRM & Suppliers")
        self.click_nav_item("Customers")

    def open_suppliers(self) -> None:
        self.open_nav_section("CRM & Suppliers")
        self.click_nav_item("Suppliers")
