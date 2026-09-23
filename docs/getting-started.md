# 🚀 Getting Started with Fridai WMS

**Welcome to Fridai Warehouse Management System!** This guide will help you get started with using the system.

## 📋 Table of Contents

1. [Logging In](#logging-in)
2. [Dashboard Overview](#dashboard-overview)
3. [Navigation](#navigation)
4. [Key Concepts](#key-concepts)
5. [Common Tasks](#common-tasks)
6. [Need Help?](#need-help)

## 🔐 Logging In

### First Time Login

1. Navigate to the Fridai login page
2. Enter your **email address**
3. Enter your **password**
4. Click **"Sign In"**

**Note**: Your administrator will provide your login credentials. If you don't have credentials, contact your administrator.

### Forgot Password

If you've forgotten your password:

1. Click **"Forgot password?"** on the login page (under the Password field)
2. Enter your account **email address**
3. Click **"Send reset link"** — Fridai sends a reset link if that email exists
4. Or click **"Back to sign in"** to return to the login page without requesting a reset

## 📊 Dashboard Overview

After logging in, you'll land on the **Dashboard** — a **customizable widget board**, not a fixed metrics page.

### What you'll see

- Heading **Dashboard** with copy about customizing widgets (drag the grip handle to reorder)
- A top-bar **warehouse selector** that scopes dashboard data to one warehouse (or All warehouses, when available)
- **"+ Add Widget"** to add, remove, or rearrange widgets (e.g. Sales, Best Selling Products, Low Stock Alerts, Dead Stock, and other General / Operations / Network widgets)

There is **no** built-in "Active Orders / Inventory Summary / Recent Activity / Quick Actions" metrics strip — older docs that describe those are outdated.

If the board is empty, you'll see **"No widgets"** and a prompt to add your first widget.

### Top bar (not a flat main nav)

The top bar holds the warehouse selector and **Help** (Help for this page / Getting Started tour / Command palette). Primary navigation is the **left sidebar** (see below).

## 🧭 Navigation

### Main Menu Structure

The left sidebar is an expandable accordion — click a section to expand it, then click the item you want. (Pin the sidebar if you only see icons.)

#### Dashboard

- **Dashboard** — customizable widget board

#### Orders & Fulfillment

- **Orders** — order queue at `/orders-list` (Work Queues + PROGRESS / STATUS)
- **Picking Tasks** — bulk picking operations
- **Packing Tasks** — bulk packing operations
- **Shipping Tasks** — bulk shipping operations
- **Returns** — process customer returns

#### Inventory Management

- **Products** — product catalog
- **Inventory** — stock levels
- **Stock Movements** — inventory history
- **Cycle Count Tasks** — cycle counts
- **Purchase Orders** — supplier orders
- **Receiving** — receive purchase orders into stock
- **Locations** — warehouse layout

#### CRM & Suppliers

- **Customers** — customer management
- **Suppliers** — supplier management

#### Settings

Settings / Warehouses / admin pages may be **role-gated** (not always visible in the sidebar for every user). There is **no separate "Reports"** nav item — `/reports` redirects to the Dashboard.

## 📚 Key Concepts

### Understanding Orders

**Orders** represent customer purchases that need to be fulfilled:

- **Draft**: Order created but not yet confirmed
- **Confirmed**: Order approved and inventory allocated
- **Picked**: Items picked from warehouse locations
- **Packed**: Items boxed and ready to ship
- **Shipped**: Items sent to customer
- **Completed**: Order fully fulfilled

### Understanding Inventory

**Inventory** refers to the stock available in your warehouse:

- **On Hand**: Total quantity physically in warehouse
- **Reserved**: Quantity allocated to orders
- **Available**: Quantity available for new orders (On Hand - Reserved)
- **Inbound**: Quantity expected from purchase orders

### Understanding Tasks

**Tasks** organize warehouse work:

- **Pick Tasks**: Selecting items from locations (can process multiple orders together)
- **Pack Tasks**: Packing items into boxes (organized by lots)
- **Ship Tasks**: Scanning packages for shipping (batch processing)

## 🎯 Common Tasks

### How to View Orders

1. Expand **"Orders & Fulfillment"** in the left sidebar and click **"Orders"** (URL: `/orders-list`)
2. Use Work Queues tabs and filters to find orders (status, channel, assignee, date)
3. Use **View** or the row's next-action button to work an order

### How to Create an Order

1. On the Orders page (`/orders-list`), click **"Create Order"**
2. Fill **Customer** info (name + email required) and choose **Channel**
3. Click **"Next"**, search products that already have **available stock**, set quantities
4. Click **"Create Order"** to finish — Fridai allocates on create

There is **no "Save Draft"** or **"Confirm Order"** button. A brand-new product with zero stock will not appear in Order Items search until a Purchase Order for it has been received.

### How to Pick an Order

1. Go to **"Picking Tasks"**
2. Click **"Create Pick Task"** (or select multiple orders from Orders page)
3. Follow the optimized pick route
4. Scan items as you pick them
5. Complete the task when finished

### How to Check Inventory

1. Click **"Inventory"** in the main menu
2. Search for a product by name or SKU
3. View current stock levels, locations, and costs
4. Click on a product for detailed information

### How to Add a Product

1. Click **"Products"** in the main menu
2. Click **"Add Product"**
3. Fill in product details (name, SKU, barcode)
4. Click **"Save"**

### How to Process a Return

1. Go to **"Returns"**
2. Search for the original order
3. Select items to return and set disposition
4. Complete the return processing

## 🔍 Search and Filtering

### Using Search

Most pages have a search bar:

- Type to search by name, SKU, order number, etc.
- Search results update automatically
- Click result to open details

### Using Filters

Many pages have filter options:

- **Status filters**: Filter by order/inventory status
- **Date range**: Filter by creation date
- **Customer/Supplier**: Filter by related party
- **Multiple filters**: Combine filters for precise results

## 📱 Tips for Efficiency

### Keyboard Shortcuts

- **Ctrl+K** (or Cmd+K on Mac): Quick search across system
- **Tab**: Move between fields
- **Enter**: Submit forms
- **Escape**: Close modals

### Quick Actions

Use the **bulk action buttons** on Orders page for multiple orders:

- **Bulk Pick**: Create pick task for multiple orders
- **Bulk Pack**: Create pack task for multiple orders
- **Bulk Ship**: Create ship task for multiple orders

### Best Practices

- **Always scan barcodes** when available for accuracy
- **Confirm quantities** before completing tasks
- **Check locations** before picking items
- **Update order status** as you progress
- **Use bulk operations** when processing multiple orders

## 🆘 Need Help?

### Getting Support

- **In-App Help**: Click the help icon (?) in the top right corner
- **Documentation**: Access user guides from the help menu
- **Contact Administrator**: Reach out to your system administrator
- **Technical Support**: Contact support@fridai.com

### Common Issues

**Problem**: Can't log in
- **Solution**: Check your credentials or use **"Forgot password?"** on the login page

**Problem**: Order not showing in list
- **Solution**: Check filters - reset filters to see all orders

**Problem**: Barcode not scanning
- **Solution**: Ensure barcode is clear and scanned barcode scanner is connected

**Problem**: Inventory count seems wrong
- **Solution**: Check recent stock movements or contact inventory manager

## 🎓 Next Steps

Now that you're familiar with the basics:

- **Explore the Dashboard** — add the widgets you care about; switch warehouse in the top bar
- **Try Common Tasks** - Practice the tasks you'll do regularly
- **Read Feature Guides** - Learn about specific features you'll use
- **Ask Questions** - Don't hesitate to ask for help

### Recommended Reading

- **Order Management Guide** - Detailed order processing
- **Inventory Management Guide** - Stock management
- **Bulk Operations Guide** - Task workflows

---

Welcome to Fridai! We're here to help you succeed.

**Document Navigation:**
- Next: Order Management Guide
- Back to Index

---
*Reconstructed from the "Friday" claude.ai project on 2026-07-16; Dashboard, navigation, Forgot password, and Create Order sections corrected against the live app on 2026-09-18 (widget board; `/orders-list`; Create Order only — no Save Draft / Confirm Order; no Reports nav).*
