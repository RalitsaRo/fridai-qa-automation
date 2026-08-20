"""Bulk actions are gated by the global warehouse selector.

NEW as of the Aug 19, 2026 order-queue rework. Confirmed live 2026-08-19:
selecting orders (via the header "select all" checkbox) reveals a bulk
action bar whose contents depend on the ACTIVE warehouse scope:

- A SPECIFIC warehouse active: "Bulk pick (N)", "Bulk pack (N)",
  "Bulk ship (N)", "Combine (N)", "Clear".
- "All warehouses" active: only "Allocate (N)" and "Combine (N)"
  (plus "Clear") — the warehouse-specific fulfilment actions disappear,
  since Pick/Pack/Ship are tied to one physical warehouse but
  Allocate/Combine are not.

See pages/orders_page.py's module docstring for the full narrative.

No side effects — this only selects rows and inspects the resulting bar,
never actually submits a bulk action.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.orders_page import OrdersPage


@pytest.mark.regression
def test_bulk_pick_pack_ship_available_with_specific_warehouse(authenticated_page: Page) -> None:
    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    # Any specific (non-"All warehouses") entry works; whatever the
    # account's default active warehouse is satisfies this.
    active = orders.current_active_warehouse()
    assert active != "All warehouses", (
        "Test setup assumption broken: expected a specific warehouse to be "
        "active by default, got 'All warehouses'."
    )

    orders.select_all_orders_checkbox()

    expect(orders.bulk_pick_button()).to_be_visible()
    expect(orders.bulk_pack_button()).to_be_visible()
    expect(orders.bulk_ship_button()).to_be_visible()
    expect(orders.combine_button()).to_be_visible()


@pytest.mark.regression
def test_bulk_pick_pack_ship_hidden_with_all_warehouses(authenticated_page: Page) -> None:
    orders = OrdersPage(authenticated_page)
    orders.goto()
    orders.wait_for_loaded()

    orders.set_active_warehouse("All warehouses")
    orders.wait_for_loaded()
    orders.select_all_orders_checkbox()

    expect(orders.bulk_pick_button()).to_have_count(0)
    expect(orders.bulk_pack_button()).to_have_count(0)
    expect(orders.bulk_ship_button()).to_have_count(0)

    # Allocate and Combine remain available -- "no bulk options" under
    # All warehouses means no WAREHOUSE-SPECIFIC ones, not literally none.
    expect(orders.allocate_bulk_button()).to_be_visible()
    expect(orders.combine_button()).to_be_visible()
