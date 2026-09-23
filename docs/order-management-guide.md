# 📋 Order Management Guide

Complete guide to managing orders in Fridai WMS - from creation to fulfillment.

## 📋 Table of Contents

1. [Viewing Orders](#viewing-orders)
2. [Creating Orders](#creating-orders)
3. [Order Statuses](#order-statuses)
4. [Picking Orders](#picking-orders)
5. [Packing Orders](#packing-orders)
6. [Shipping Orders](#shipping-orders)
7. [Processing Returns](#processing-returns)
8. [Order Tracking](#order-tracking)

## 👀 Viewing Orders

### Accessing the Orders Page

1. Expand **"Orders & Fulfillment"** in the left sidebar and click **"Orders"**
2. The page URL is **`/orders-list`** (not `/orders`)
3. You'll see the order queue with:
   - Work Queues tabs (All orders / Ready to pick / Ready to pack / Ready to ship / Partially fulfilled / Backorders)
   - Columns: **ORDER**, **CUSTOMER**, **WAREHOUSE**, **PROGRESS**, **STATUS**, **DATE**, **ACTION**
   - A per-row next-action button (Pick / Pack / Ship…) plus **View**

### Filtering Orders

Use the filter options to find specific orders:

- **Status Filter**: Filter by order status
- **Date Range**: Filter by order creation date
- **Channel**: Filter by channel (e.g. Direct to Consumer / Business to Business)
- **Assignee**: Filter by assigned user

### Searching Orders

- Use the search bar at the top
- Type to search by order number, customer name, or SKU
- Results update automatically as you type

### Viewing Order Details

1. Click **View** on an order row (or open the order from the list)
2. View complete order information including customer, lines, warehouse, and next actions (e.g. Reallocate / Split / Cancel remaining when available)

## ➕ Creating Orders

### Creating a New Order

1. On the Orders page (`/orders-list`), click **"Create Order"** (top right)
2. **Step 1 — Customer info**:
   - **Customer Name** (required)
   - **Customer Email** (required)
   - **Channel** (e.g. Direct to Consumer / Business to Business)
   - **Warehouse** is auto-filled from the top-bar warehouse selector (read-only)
3. Click **"Next"**
4. **Step 2 — Order Items**:
   - Search for a product by name or SKU — only products with **available stock** appear
   - Enter quantity and add the line
   - Repeat for additional items
5. Click **"Create Order"** to finish — Fridai allocates available stock on create

There is **no "Save Draft"** button and **no separate "Confirm Order"** action. The only final submit control is **"Create Order"**.

**Prerequisite**: a brand-new product has zero stock and will **not** appear in Order Items search until you create and **receive** a Purchase Order for it.

### Adding Products to Order

1. In Create Order Step 2 (Order Items)
2. Search for product by name or SKU
3. Select a result that has available stock
4. Enter quantity
5. Product is added to the order

### Customer Selection

- Enter customer name and email on Step 1 (required)
- Searching an existing customer may be available depending on the form variant
- New customers can be created as part of order creation (email must be a real deliverable domain — reserved domains like `.local` are rejected)

## 📊 Order Statuses

Understanding what each status means:

- **Draft**: Order created but not confirmed (no inventory reserved)
- **Confirmed**: Order approved and inventory allocated
- **Processing**: Order in fulfillment workflow
- **Picked**: All items picked from warehouse
- **Packed**: All items packed into boxes
- **Shipped**: Order sent to customer
- **Completed**: Order fully fulfilled
- **Cancelled**: Order cancelled (inventory released)
- **Returned**: Items returned by customer

### Status Transitions

Orders progress through statuses automatically:

- Confirmed → Picked (after picking complete)
- Picked → Packed (after packing complete)
- Packed → Shipped (after shipping complete)
- Shipped → Completed (after delivery confirmed)

## 📦 Picking Orders

### Single Order Picking

1. Find order in Orders list
2. Click **"Pick"** button (available for confirmed orders)
3. Review pick list with locations
4. Follow optimized pick route
5. Scan items as you pick them
6. Complete picking when all items scanned

### Bulk Picking (Multiple Orders)

1. Select multiple orders using checkboxes
2. Click **"Bulk Pick"** button
3. System consolidates items by location
4. Follow optimized pick route
5. Scan consolidated items
6. Complete when all items picked

### During Picking

- **View Locations**: Each item shows warehouse location
- **Scan Barcodes**: Validate items as you pick
- **Adjust Quantities**: Handle shortages
- **Check Progress**: See completion percentage

## 📦 Packing Orders

### Starting Packing

1. Go to packed order (status: picked)
2. Click **"Pack"** button
3. View items that need packing

### Packing Process

1. **Select Box Template**
   - Choose from predefined box sizes
   - Or enter custom dimensions
2. **Add Items to Box**
   - Assign items to boxes
   - Distribute items across multiple boxes if needed
3. **Enter Details**
   - Box weight
   - Box dimensions
   - Notes if needed
4. **Print Packing Slip**
   - Click "Print Packing Slip"
5. **Close Boxes**
   - Mark boxes as sealed
6. **Complete Packing**
   - All items assigned and boxes sealed

### Multi-Box Orders

- Create additional boxes as needed
- Assign items to appropriate boxes
- Each box can be sealed independently
- Print individual packing slips

## 🚚 Shipping Orders

### Shipping Setup

1. Select carrier (UPS, FedEx, DHL)
2. Choose service level
3. Generate shipping label

### Generating Labels

1. Click **"Generate Label"** on packed order
2. System connects to carrier API
3. Label generated and displayed
4. Click **"Print Label"**
5. Attach to package

### Shipping Process

1. Print shipping label
2. Attach to box
3. Click **"Mark as Shipped"**
4. Order status updates automatically
5. Tracking number recorded

### Tracking Information

- Tracking number displayed on order
- Update tracking in carrier system
- Customer receives tracking email

## 🔄 Processing Returns

### Creating a Return

1. Go to **"Returns"** section
2. Click **"Create Return"**
3. Search for original order
4. Select order from results

### Returning Items

1. **Select Items**: Click items to return (partial returns OK)
2. **Enter Quantities**: Specify quantity for each item
3. **Set Disposition**
   - **Resellable**: Restore to inventory
   - **Damaged**: Quarantine or write off
   - **Destroy**: Remove from inventory
4. **Enter Reason**: Add return reason/notes
5. **Process Return**: Complete return processing

### Return Processing

- Resellable items restored to inventory
- Order status updated to "returned"
- Return record created for tracking
- Customer notified of return receipt

## 🔍 Order Tracking

### Order History

View complete order history:

- Status changes with timestamps
- User who performed each action
- Items picked, packed, shipped
- Return information

### Customer View

Customers can track their orders via email with:

- Current status
- Tracking number (when shipped)
- Estimated delivery date
- Item details

## 💡 Tips and Best Practices

### Order Accuracy

- **Double-check quantities** before confirming
- **Verify customer information** is correct
- **Confirm stock availability** before committing
- **Review shipping address** carefully

### Efficiency

- **Use bulk operations** for multiple orders
- **Scan barcodes** instead of typing
- **Complete tasks in order** (pick → pack → ship)
- **Use filters** to find orders quickly

### Customer Service

- **Keep notes** on special instructions
- **Update customers** on status changes
- **Handle returns** promptly
- **Track issues** in order notes

## ❓ Frequently Asked Questions

**Q: Can I edit a confirmed order?**
A: Contact your administrator. Confirmed orders have inventory allocated.

**Q: What if I can't find an item while picking?**
A: Mark as short pick and continue. System tracks shortages.

**Q: Can I return part of an order?**
A: Yes! Select specific items and quantities when creating return.

**Q: How do I track shipped orders?**
A: Check the order details for tracking number, or use carrier website.

**Q: What happens if I cancel an order?**
A: Inventory is automatically released back to available stock.

## 🎓 Next Steps

- Learn about **Inventory Management**
- Explore **Bulk Operations**
- Customize your **Dashboard** widgets (there is no separate Reports section)

---

**Document Navigation:**
- Previous: Getting Started
- Next: Inventory Management Guide
- Back to Index

---
*Reconstructed from the "Friday" claude.ai project on 2026-07-16; Viewing Orders and Creating Orders corrected against the live app on 2026-09-18 (`/orders-list`, Work Queues, PROGRESS column, Create Order wizard with Create Order only — no Save Draft / Confirm Order).*
