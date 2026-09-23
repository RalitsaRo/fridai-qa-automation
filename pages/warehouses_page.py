"""Page Object for Settings > Warehouses (`/warehouses`).

NEW 2026-08-11, part of the Aug 10, 2026 multi-warehouse release. Confirmed
live 2026-08-12/13:

- H1 "Warehouses", subtitle "Manage warehouse locations, fulfillment
  settings, and network priority"
- Search input, placeholder "Search warehouses..."
- "+ Add Warehouse" button
- A real `<table>` (not a plain div list) with columns WAREHOUSE / ACTIONS
  (gear = edit, trash = delete) — `warehouse_row()` below relies on this.
- Reached via Settings > Warehouses in the sidebar, or `goto()` directly
  (unlike Orders, a direct `/warehouses` link works fine).

## Add Warehouse modal — 2026-08-12, all fields confirmed field-by-field

Name* (required, the only required field), Code (auto-generated if left
blank), Address Line 1, Address Line 2, City, State, Postal Code, Country,
Phone, Priority (a number input — lower = higher priority; decides which
warehouse gets picked from first when more than one could fulfil the same
order), Warehouse Type (select: Distribution Center / Shop / Store / 3PL /
Other), then 5 checkboxes in this exact DOM order: Fulfillment enabled
(checked by default), Receiving enabled (checked by default), **Web
fulfilment allowed** (unchecked by default — the flag that will matter
once Fridai is integrated with Hemi; see the New User Getting Started
Guide, Step 3), Default network fallback (unchecked by default), Active
(checked by default). Buttons: Cancel, Create Warehouse.

**Real UX issue, confirmed live 2026-08-11**: leaving Name at whatever
default the app suggests produces multiple warehouses all displaying as
"Second warehouse" — indistinguishable in the top-bar selector and
everywhere else. Always pass a distinct `name` to `set_name()`.
"""

from __future__ import annotations

from pages.base_page import BasePage


class WarehousesPage(BasePage):
    """Settings > Warehouses list page and its Add Warehouse modal."""

    path = "/warehouses"

    # ---- Readiness / list -------------------------------------------------

    def wait_for_loaded(self, timeout: int = 10_000) -> None:
        self.by_role("heading", "Warehouses").wait_for(state="visible", timeout=timeout)

    def search(self, query: str) -> None:
        self.by_placeholder("Search warehouses...").fill(query)

    def warehouse_row(self, name: str):
        """The `<tr>` for a warehouse whose Name column contains `name`."""
        return self.page.locator("tr", has_text=name)

    def warehouse_exists(self, name: str) -> bool:
        return self.warehouse_row(name).count() > 0

    # ---- Add Warehouse (VERIFIED live 2026-08-12, all fields) -------------

    def start_add_warehouse(self) -> None:
        self.by_role("button", "Add Warehouse").click()

    def _add_warehouse_modal(self):
        """Scope to the Add Warehouse modal. Uses "Create Warehouse" (the
        submit button, present only in the modal) rather than "Cancel" as
        the second anchor — "Cancel" alone risks the same footer-only
        false-match seen with the order Split modal (a small footer div
        containing both button labels can satisfy a loose filter before
        the real modal container does)."""
        return self.modal_scope("Add Warehouse", "Create Warehouse")

    def set_name(self, name: str) -> None:
        """Required. Pick something distinct — see the module docstring's
        warning about duplicate "Second warehouse" naming."""
        self._add_warehouse_modal().locator('input[type="text"]').nth(0).fill(name)

    def set_code(self, code: str) -> None:
        """Optional — auto-generated if left blank."""
        self._add_warehouse_modal().locator('input[type="text"]').nth(1).fill(code)

    def set_address_line1(self, value: str) -> None:
        self._add_warehouse_modal().locator('input[type="text"]').nth(2).fill(value)

    def set_address_line2(self, value: str) -> None:
        self._add_warehouse_modal().locator('input[type="text"]').nth(3).fill(value)

    def set_city(self, value: str) -> None:
        self._add_warehouse_modal().locator('input[type="text"]').nth(4).fill(value)

    def set_state(self, value: str) -> None:
        self._add_warehouse_modal().locator('input[type="text"]').nth(5).fill(value)

    def set_postal_code(self, value: str) -> None:
        self._add_warehouse_modal().locator('input[type="text"]').nth(6).fill(value)

    def set_country(self, value: str) -> None:
        self._add_warehouse_modal().locator('input[type="text"]').nth(7).fill(value)

    def set_phone(self, value: str) -> None:
        self._add_warehouse_modal().locator('input[type="text"]').nth(8).fill(value)

    def set_priority(self, priority: int) -> None:
        """Optional. Lower = higher priority — decides which warehouse is
        picked from first when more than one could fulfil the same order
        (most relevant once "Web fulfilment allowed" warehouses exist)."""
        self._add_warehouse_modal().locator('input[type="number"]').fill(str(priority))

    def set_warehouse_type(self, warehouse_type: str) -> None:
        """Optional. One of: 'Distribution Center', 'Shop / Store', '3PL', 'Other'.
        This is the only <select> inside the modal scope — the page-wide
        "Active warehouse" selector (see BasePage) lives outside it."""
        self._add_warehouse_modal().locator("select").select_option(label=warehouse_type)

    # Checkboxes, in confirmed DOM order.
    def _checkbox(self, index: int):
        return self._add_warehouse_modal().locator('input[type="checkbox"]').nth(index)

    def set_fulfillment_enabled(self, checked: bool) -> None:
        """Default: checked."""
        self._checkbox(0).set_checked(checked)

    def set_receiving_enabled(self, checked: bool) -> None:
        """Default: checked."""
        self._checkbox(1).set_checked(checked)

    def set_web_fulfilment_allowed(self, checked: bool) -> None:
        """Default: UNCHECKED. This is the flag that will matter once
        Fridai integrates with Hemi — only warehouses with this checked
        will be eligible to receive/fulfil Hemi-sourced ("web") orders."""
        self._checkbox(2).set_checked(checked)

    def set_default_network_fallback(self, checked: bool) -> None:
        """Default: unchecked."""
        self._checkbox(3).set_checked(checked)

    def set_active(self, checked: bool) -> None:
        """Default: checked."""
        self._checkbox(4).set_checked(checked)

    # Read-only accessors, for asserting default/current state without
    # reaching into `_checkbox()` directly from a test.
    def fulfillment_enabled_checkbox(self):
        return self._checkbox(0)

    def receiving_enabled_checkbox(self):
        return self._checkbox(1)

    def web_fulfilment_allowed_checkbox(self):
        return self._checkbox(2)

    def default_network_fallback_checkbox(self):
        return self._checkbox(3)

    def active_checkbox(self):
        return self._checkbox(4)

    def submit_create_warehouse(self) -> None:
        self._add_warehouse_modal().get_by_role("button", name="Create Warehouse").click()
        self.page.wait_for_timeout(1000)
