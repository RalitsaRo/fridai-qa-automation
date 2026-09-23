"""Settings > Warehouses > Add Warehouse — happy path.

NEW as of the Aug 10, 2026 multi-warehouse release. Verified live
2026-08-12 — see pages/warehouses_page.py for the full field-by-field
narrative, including the "Web fulfilment allowed" flag (the setting that
will matter once Fridai is integrated with Hemi) and the real UX issue
found with duplicate default warehouse names.

RECHECK 2026-09-21: /warehouses returns Access Denied for the current
automation account (role label \"User\"). These tests skip in that case
until FRIDAI_TEST_USER is granted warehouse-management / Admin rights.

⚠️ REAL DATA WARNING: creates one real Warehouse on the shared test-phase
instance (https://app.fridai.pro) — same caveat as test_create_order.py.
Warehouses have no confirmed delete/cleanup path exercised by this suite
yet, so this accumulates over repeated runs (tracked as a follow-up).
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

from pages.warehouses_page import WarehousesPage

pytestmark = pytest.mark.regression


def _require_warehouses_access(page: Page, warehouses: WarehousesPage) -> None:
    """Warehouses is role-gated. Skip when the account cannot open the page."""
    warehouses.goto()
    page.wait_for_timeout(1000)
    if page.get_by_text("Access Denied", exact=False).count() > 0:
        pytest.skip(
            "Current account cannot open /warehouses (Access Denied). "
            "Grant warehouse-management / Admin permission to FRIDAI_TEST_USER "
            "to run these settings tests."
        )
    warehouses.wait_for_loaded()


def test_create_warehouse_with_web_fulfilment_allowed(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    warehouse_name = f"Automation Test Warehouse {unique_suffix}"

    warehouses = WarehousesPage(authenticated_page)
    _require_warehouses_access(authenticated_page, warehouses)

    warehouses.start_add_warehouse()
    warehouses.set_name(warehouse_name)
    warehouses.set_priority(5)
    warehouses.set_warehouse_type("Distribution Center")
    # Explicitly enable the flag that matters for the future Hemi
    # integration — confirmed unchecked by default.
    warehouses.set_web_fulfilment_allowed(True)
    warehouses.submit_create_warehouse()

    # 1. Appears in the Warehouses list.
    warehouses.wait_for_loaded()
    assert warehouses.warehouse_exists(warehouse_name), (
        f"Expected {warehouse_name!r} to appear in the Warehouses list "
        "after creation."
    )

    # 2. Appears in the global "Active warehouse" selector too.
    options = warehouses.warehouse_selector().evaluate(
        "(el) => Array.from(el.options).map(o => o.text)"
    )
    assert any(warehouse_name in opt for opt in options), (
        f"Expected {warehouse_name!r} to appear in the global warehouse "
        f"selector; got options {options!r}."
    )


def test_new_warehouse_defaults_web_fulfilment_allowed_unchecked(authenticated_page: Page) -> None:
    """Confirms the default state documented in warehouses_page.py, so a
    future UI change to these defaults gets caught here rather than only
    being noticed informally."""
    warehouses = WarehousesPage(authenticated_page)
    _require_warehouses_access(authenticated_page, warehouses)
    warehouses.start_add_warehouse()

    expect(warehouses.fulfillment_enabled_checkbox()).to_be_checked()
    expect(warehouses.receiving_enabled_checkbox()).to_be_checked()
    expect(warehouses.web_fulfilment_allowed_checkbox()).not_to_be_checked()
    expect(warehouses.default_network_fallback_checkbox()).not_to_be_checked()
    expect(warehouses.active_checkbox()).to_be_checked()
