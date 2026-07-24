"""Page Object for the Products page.

VERIFIED 2026-07-16 against the live app at `/products` (direct navigation
works fine here, unlike `/orders` — see orders_page.py).

Confirmed page elements:
- H1 "Products"
- Buttons: "Bulk Actions (Coming Soon)" (disabled/future), "Upload Products",
  "Add Product"
- Search input, placeholder "Search by name, SKU, or barcode..."
- "All Statuses" filter button, "Clear Filters" button
- Row checkboxes (bulk select) + per-row actions: "Edit", "Inventory", "Delete"
- Table columns: Product, SKU, Barcode, Purchase Price, Low Stock
  Threshold, Status, Actions

## "Add Product" modal — verified 2026-07-16 (real form, heading "Create
New Product")

Unlike the Orders page's "Create Order" modal, this one does NOT collide
with anything on the background Products page (no shared button text), so
plain page-wide `by_placeholder()` / `by_role()` locators work fine here —
no `modal_scope()` needed.

Confirmed fields, in real DOM order (note: SKU comes BEFORE Product Name,
opposite of the order docs/getting-started.md lists them):
- SKU * (required) — placeholder "Enter SKU"
- Product Name * (required) — placeholder "Enter product name"
- Barcode (optional) — placeholder "Enter barcode"
- Default Purchase Price (optional, number) — placeholder "0.00"
- Low Stock Threshold (optional, number) — placeholder "0"
- Status — native <select>: Active / Inactive / Discontinued (not
  mentioned in any doc)
- Description (optional, textarea) — placeholder "Enter product description"
- Buttons: "Cancel", "Create Product"

This is a real, existing product in the catalog as of 2026-07-16 (useful
as a known-good search term for Orders' line-item step):
Product "RaliPN1", SKU "RaliP1", barcode "123" — confirmed with live
available stock (997) when searched from Create Order's Step 2.
"""

from __future__ import annotations

from pages.base_page import BasePage


class ProductsPage(BasePage):
    """The Products / catalog page."""

    path = "/products"

    def wait_for_loaded(self, timeout: int = 10_000) -> None:
        self.by_role("heading", "Products").wait_for(state="visible", timeout=timeout)

    def search(self, query: str) -> None:
        self.by_placeholder("Search by name, SKU, or barcode...").fill(query)

    def clear_filters(self) -> None:
        self.by_role("button", "Clear Filters").click()

    def start_add_product(self) -> None:
        self.by_role("button", "Add Product").click()

    def edit_product(self, name_or_sku: str) -> None:
        row = self.page.locator("tr", has_text=name_or_sku)
        row.get_by_role("button", name="Edit").click()

    def delete_product(self, name_or_sku: str) -> None:
        row = self.page.locator("tr", has_text=name_or_sku)
        row.get_by_role("button", name="Delete").click()

    # ---- Add Product form (VERIFIED 2026-07-16) --------------------------------

    def add_product(
        self,
        sku: str,
        name: str,
        barcode: str | None = None,
        purchase_price: float | None = None,
        low_stock_threshold: int | None = None,
        status: str = "Active",
        description: str | None = None,
    ) -> None:
        """Fill and submit the "Create New Product" form. `sku` and `name`
        are the only required fields in the real UI."""
        self.start_add_product()
        self.by_placeholder("Enter SKU").fill(sku)
        self.by_placeholder("Enter product name").fill(name)
        if barcode:
            self.by_placeholder("Enter barcode").fill(barcode)
        if purchase_price is not None:
            self.by_placeholder("0.00").fill(str(purchase_price))
        if low_stock_threshold is not None:
            self.by_placeholder("0").fill(str(low_stock_threshold))
        if status != "Active":
            self.page.locator("select").select_option(label=status)
        if description:
            self.by_placeholder("Enter product description").fill(description)
        self.by_role("button", "Create Product").click()
        # Confirmed live: a caller that immediately searches for this
        # product elsewhere (e.g. PurchaseOrdersPage.add_po_line_item())
        # can race the creation — give it a moment to settle/index.
        self.page.wait_for_timeout(1500)
