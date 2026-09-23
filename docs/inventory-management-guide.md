# 📦 Inventory Management Guide

How inventory works in Fridai WMS (verified against the live app).

## Critical rule: stock comes from receiving

A **Product** record alone has **zero stock**. Creating a product is not enough to sell or fulfill it.

Confirmed message on a new product's Inventory view:

> No inventory items — Inventory is created when you receive purchase orders. Create and receive a PO to get started.

The chain that makes a product **orderable**:

1. **Product** — create (or import) the SKU  
2. **Supplier** — must exist before you can raise a PO (CRM & Suppliers → Suppliers)  
3. **Purchase Order** — create a PO for that product (status usually starts as Placed)  
4. **Record ASN** — Advance Shipping Notice (or "Expected matches PO") → status becomes Supplier shipped  
5. **Release for receiving** → Ready to receive  
6. **Receive** on the Receiving page (scan SKU → quantity → location → Finish)  
7. Stock becomes **Available** → the product appears in Create Order → Order Items search  

Alternative path (documented by Fridai's in-app tour, not fully walked by QA yet): establish stock via **Cycle Count** instead of PO receive.

There is **no** inline "create product" / "create PO" shortcut inside Create Order.

## Navigation (Inventory Management)

Left sidebar → **Inventory Management**:

| Item | Purpose |
|------|---------|
| **Products** | Catalog (SKU, name, barcode, prices, thresholds) |
| **Inventory** | Stock levels / locations once inventory exists |
| **Stock Movements** | Ledger of receives, picks, ships, counts |
| **Cycle Count Tasks** | Cycle counts (alternate stock path) |
| **Purchase Orders** | Supplier POs (`/purchase-orders`) |
| **Receiving** | Receive released POs into locations (`/receiving`) |
| **Locations** | Zones / aisles / bays / bins |

## Products

### Add a product

1. Inventory Management → **Products** → **Add Product**  
2. Required: **SKU**, **Product Name**  
3. Optional: Barcode, Purchase Price, Low Stock Threshold, Status, Description  
4. Save  

After save, inventory is still empty until a PO is received (see chain above).

## Purchase Orders

### PO lifecycle (confirmed live)

`Draft` → `Placed` → `Supplier shipped` → `Ready to receive` → `Partially received` → `Received` → `Completed`  
(or **Cancelled** at supported points)

A product can become orderable as early as **Partially received** after a successful receive — you do not need the PO to reach Completed first.

### Create a Purchase Order

1. Inventory Management → **Purchase Orders** → **Create Purchase Order**  
2. **Step 1 — Details**: Supplier* (required), **Warehouse** (see below), Receiving Location*, Initial status (Draft / Placed), optional Expected Delivery Date / Notes  
3. **Next** → **Step 2 — PO Items**: search any product (stock not required here), set Qty, Add  
4. Click **Create Purchase Order**  

**Warehouse field (multi-warehouse shell):**
- If the top-bar Active warehouse is a **specific** warehouse → the PO is bound to that site. The modal Warehouse control is **locked** (pre-filled, not editable) or omitted entirely — switch the top-bar selector first if you need a different site.
- If the top-bar is **All warehouses** (typically Admin) → Warehouse becomes an **editable** required select in the modal.

### Record ASN → Release → Receive

1. On a **Placed** PO row: **Record ASN** → e.g. **Expected matches PO** → Confirm → status **Supplier shipped**  
2. **Release for receiving** (optional landed costs) → **Ready to receive**  
3. Go to **Receiving** (or use the row's **Receive** action)  
4. Scan / enter product → accept quantity → enter / select location → **Finish receiving**  

**Receiving tip:** if you use **"Or select location manually"**, select the option and press **Enter** (same as the scan field). Selecting alone is not enough.

## Inventory & stock movements

- **Inventory** page: view on-hand / location assignments once stock exists  
- **Stock Movements**: every receive, pick, ship, and count should write a movement (per Fridai's own tour)  
- **Available** stock is what Create Order's Order Items search uses — reserved / unreceived quantity does not make a new product searchable there  

## Best practices

- Create **Locations** and a **Supplier** before your first PO on a new warehouse  
- Prefer the full PO → ASN → Release → Receive path for testable, auditable stock  
- After receiving, confirm the SKU appears in Create Order before blaming the order form  
- Use the top-bar **warehouse selector** — POs, receiving, and inventory are warehouse-scoped  

## Related automation

- Full chain: `tests/inventory/test_receive_purchase_order.py`  
- Zero-stock product not orderable: `tests/orders/test_new_product_without_stock_not_orderable.py`  
- Unknown SKU in Order Items: `tests/orders/test_order_requires_product.py`  

---
*Originally a thin outline reconstructed from the Friday claude.ai project on 2026-07-16. Rewritten 2026-09-18 to document the live Product → PO → ASN → Release → Receive → orderable-stock chain and PO lifecycle.*
