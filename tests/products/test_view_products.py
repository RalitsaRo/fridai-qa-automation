"""View Products — read-only check against the real Products page.

Locators VERIFIED 2026-07-16 against the live app. No side effects.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.products_page import ProductsPage


@pytest.mark.smoke
def test_products_page_loads(authenticated_page: Page) -> None:
    products = ProductsPage(authenticated_page)
    products.goto()
    products.wait_for_loaded()

    expect(products.by_role("button", "Add Product")).to_be_visible()
    expect(products.by_placeholder("Search by name, SKU, or barcode...")).to_be_visible()
