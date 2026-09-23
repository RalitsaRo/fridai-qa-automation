"""Create PO Warehouse field vs top-bar Active warehouse shell.

Product design:
- Specific warehouse in the top-bar → Create PO Warehouse is locked
  (pre-filled / not editable) or omitted; PO binds to the shell warehouse.
- \"All warehouses\" in the top-bar (Admin) → Warehouse is editable in the modal.

The automation User account has no \"All warehouses\" option, so this file
covers the specific-warehouse path and skips the All-warehouses path when
unavailable.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.purchase_orders_page import PurchaseOrdersPage


@pytest.mark.regression
def test_create_po_warehouse_follows_specific_shell_warehouse(authenticated_page: Page) -> None:
    orders_wh = PurchaseOrdersPage(authenticated_page)
    # Ensure a specific warehouse is active (default for this User role).
    active = orders_wh.current_active_warehouse()
    assert active != "All warehouses", (
        "Expected a specific Active warehouse for this account; got "
        f"{active!r}."
    )

    purchase_orders = PurchaseOrdersPage(authenticated_page)
    purchase_orders.goto()
    purchase_orders.wait_for_loaded()
    purchase_orders.start_create_po()

    assert purchase_orders.is_modal_warehouse_editable() is False, (
        "With a specific warehouse in the shell, Create PO Warehouse must "
        "not be editable."
    )
    # Whether the field is omitted or locked, the effective warehouse is
    # the shell selection.
    assert purchase_orders.current_warehouse() == active

    # set_warehouse must refuse rather than silently no-op.
    with pytest.raises(RuntimeError, match="Warehouse"):
        purchase_orders.set_warehouse(active)


@pytest.mark.regression
def test_create_po_warehouse_editable_under_all_warehouses(authenticated_page: Page) -> None:
    purchase_orders = PurchaseOrdersPage(authenticated_page)
    options = purchase_orders.warehouse_selector().evaluate(
        "(el) => Array.from(el.options).map(o => o.text.trim())"
    )
    if "All warehouses" not in options:
        pytest.skip(
            "Active warehouse has no 'All warehouses' option "
            f"(got {options!r}). Needs an Admin-capable account to exercise "
            "the editable Create PO Warehouse field."
        )

    purchase_orders.set_active_warehouse("All warehouses")
    purchase_orders.goto()
    purchase_orders.wait_for_loaded()
    purchase_orders.start_create_po()

    assert purchase_orders.is_modal_warehouse_editable() is True, (
        "With All warehouses in the shell, Create PO Warehouse must be editable."
    )
