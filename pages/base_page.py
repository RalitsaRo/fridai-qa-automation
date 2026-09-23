"""Base Page Object class.

Every Page Object in `pages/` should subclass `BasePage`. Conventions mirror
the ones used in the sister `../automation_ui/` (Hemi) suite, with one
confirmed difference: **the real Fridai app (https://app.fridai.pro) has no
`data-testid` attributes anywhere** (verified 2026-07-16 by inspecting the
live DOM). `by_test_id()` is kept for parity with Hemi's BasePage but will
not resolve anything real here — use `by_role()` / `by_placeholder()`
instead, which match how this app is actually built (plain `<button>`/
`<input>` elements with visible text or `placeholder` as the only stable
signal).

- One Page Object class per page or major component.
- Page Object methods expose business actions (e.g. `login(user, pw)`,
  `create_order(...)`) — they do NOT contain assertions.
- Tests call Page Object methods and hold all `expect()` assertions
  themselves.
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator


class BasePage:
    """Base class for all Page Objects."""

    # Subclasses set this to the relative path of the page (e.g. "/orders-list").
    # `goto()` joins it onto the configured BASE_URL.
    path: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    # ---- Navigation ---------------------------------------------------------

    def goto(self) -> None:
        """Navigate to this page's path. Base URL comes from the `page` fixture."""
        self.page.goto(self.path)

    # ---- Locator helpers ----------------------------------------------------

    def by_test_id(self, test_id: str) -> Locator:
        """Resolve a locator by `data-testid`.

        NOT USABLE against the real Fridai app — kept only so any future
        Page Object mirrored from Hemi's suite fails loudly/obviously rather
        than silently matching the wrong element. Use `by_role()` /
        `by_placeholder()` instead.
        """
        return self.page.get_by_test_id(test_id)

    def by_role(self, role: str, name: str, **kwargs) -> Locator:
        """Resolve a locator by ARIA role + accessible name (button text,
        input label, etc.). This is the primary locator strategy for
        Fridai, since the app has no data-testid attributes."""
        return self.page.get_by_role(role, name=name, **kwargs)

    def by_placeholder(self, text: str) -> Locator:
        """Resolve an <input> by its `placeholder` attribute."""
        return self.page.get_by_placeholder(text)

    def modal_scope(self, heading_text: str, other_text: str) -> Locator:
        """Best-effort scope to a modal/dialog container.

        Fridai's modals have no `role="dialog"` and no `data-testid` — a
        modal is just a plain `<div>` rendered on top of the page that's
        still there behind it. Confirmed live 2026-07-16: querying the page
        directly for the modal's own "Next" button raised a Playwright
        strict-mode violation, because the Orders list page behind the
        "Create Order" modal has its own pagination "Next" button with the
        identical role+name. Scoping every locator to the container returned
        here avoids that collision.

        `heading_text` should be the modal's own heading (e.g. "Create New
        Order"); `other_text` should be some other string only the modal
        contains (e.g. "Cancel") so the match doesn't also catch a
        coincidentally-similar wrapper elsewhere on the page.
        """
        return self.page.locator("div").filter(has_text=heading_text).filter(has_text=other_text).last

    # ---- Shared left-nav (confirmed present on every authenticated page) ----

    def open_nav_section(self, section_text: str) -> None:
        """Expand a top-level, collapsible nav section (e.g. "Orders &
        Fulfillment", "Inventory Management"). No-ops harmlessly if already
        expanded — clicking an already-open section just collapses it, so
        callers should not call this twice in a row for the same section."""
        self.by_role("button", section_text).click()

    def click_nav_item(self, item_text: str, *, exact: bool = True) -> None:
        """Click a nav item revealed after `open_nav_section()`. `exact`
        defaults to True because several nav labels are substrings of each
        other (e.g. "Orders" vs. "Orders & Fulfillment").

        CONFIRMED LIVE 2026-08-11 (the Aug 10 multi-warehouse release): leaf
        nav items changed from `<button>` to `<a><span>text</span></a>` —
        this method used to target role="button" and broke as a result. The
        top-level, collapsible SECTION headers (`open_nav_section()`, e.g.
        "Orders & Fulfillment") are still real `<button>`s; only the leaf
        items you click after expanding a section changed to links."""
        self.by_role("link", item_text, exact=exact).click()

    # ---- Global warehouse selector (Aug 10, 2026 multi-warehouse release) ---

    def warehouse_selector(self) -> Locator:
        """The page-wide "Active warehouse" `<select>` added to the top nav
        on every authenticated page (confirmed live 2026-08-11). Scopes
        most of the app (Dashboard, Orders, Purchase Orders, etc.) to one
        warehouse, or "All warehouses" for Administrators. Always locate it
        by this `aria-label`, never a bare `page.locator("select")` — see
        `ReceivingPage.first_available_location_text()` for why."""
        return self.page.locator('select[aria-label="Active warehouse"]')

    def set_active_warehouse(self, label: str) -> None:
        """Switch the global warehouse selector to `label` (e.g. "WH-2 —
        First Warehouse", or "All warehouses"). Confirmed live 2026-08-13:
        this re-scopes the current page's data (Orders, Dashboard, etc.),
        so a short settle wait is built in here — callers still doing
        their own `wait_for_loaded()` afterward is fine/redundant, not
        harmful."""
        self.warehouse_selector().select_option(label=label)
        self.page.wait_for_timeout(1200)

    def current_active_warehouse(self) -> str:
        """Read-only: the warehouse currently selected in the global
        selector."""
        return self.warehouse_selector().evaluate("(el) => el.options[el.selectedIndex].text")

    # ---- Common readiness checks -------------------------------------------

    def wait_for_loaded(self, test_id: str, timeout: int = 10_000) -> None:
        """Wait for a sentinel element (by test id) to be visible. Subclasses
        should call this in their own `wait_for_loaded()` overrides with the
        appropriate sentinel for their page.

        NOT USABLE as-is (see `by_test_id` above) — subclasses override this
        with a role/text-based sentinel instead."""
        self.by_test_id(test_id).wait_for(state="visible", timeout=timeout)
