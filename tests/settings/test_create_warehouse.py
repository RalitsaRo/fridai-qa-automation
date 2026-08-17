"""Settings > Warehouses > Add Warehouse — happy path.

NEW as of the Aug 10, 2026 multi-warehouse release. Verified live
2026-08-12 — see pages/warehouses_page.py for the full field-by-field
narrative, including the "Web fulfilment allowed" flag (the setting that
will matter once Fridai is integrated with Hemi) and the real UX issue
found with duplicate default warehouse names.

This test deliberately sets a distinct `name` (see the warning in
warehouses_page.py) and confirms the new warehouse shows up both in the
Warehouses list AND in the global "Active warehouse" selector (BasePage) —
the two places a user would actually look for it.

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


def test_create_warehouse_with_web_fulfilment_allowed(authenticated_page: Page) -> None:
    unique_suffix = str(int(time.time()))
    warehouse_name = f"Automation Test Warehouse {unique_suffix}"

    warehouses = WarehousesPage(authenticated_page)
    warehouses.goto()
    warehouses.wait_for_loaded()

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
    warehouses.goto()
    warehouses.wait_for_loaded()
    warehouses.start_add_warehouse()

    expect(warehouses.fulfillment_enabled_checkbox()).to_be_checked()
    expect(warehouses.receiving_enabled_checkbox()).to_be_checked()
    expect(warehouses.web_fulfilment_allowed_checkbox()).not_to_be_checked()
    expect(warehouses.default_network_fallback_checkbox()).not_to_be_checked()
    expect(warehouses.active_checkbox()).to_be_checked()
