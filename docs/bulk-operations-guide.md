# 🔧 Bulk Operations & Order Queue Guide

How multi-order work and fulfillment actions work in Fridai (verified against the live app, including the Aug 19, 2026 order-queue rework).

## Where the work lives

Primary surface: **Orders & Fulfillment → Orders** at **`/orders-list`**.

Also available as dedicated nav items (field-by-field coverage still thinner than the Orders queue):

- **Picking Tasks**
- **Packing Tasks** — labels are optional until a courier is configured (per Fridai's in-app tour)
- **Shipping Tasks**

## Orders queue (not lot-based packing columns)

The Orders table is **not** organized around a separate **Packing** column or "lots".

Confirmed columns:

| Column | Role |
|--------|------|
| ORDER | Order number + summary |
| CUSTOMER | Customer |
| WAREHOUSE | Fulfilling warehouse |
| **PROGRESS** | Combined progress (bar + text), e.g. "ready to pick/pack" |
| **STATUS** | Order status (e.g. Processing, Partially Picked, Picked) |
| DATE | Date |
| ACTION | Dynamic next action (Pick / Pack / Ship…) + **View** (+ More actions when needed) |

**Work Queues** tabs (counts overlap when an order still has mixed work):

- All orders  
- Ready to pick  
- Ready to pack  
- Ready to ship  
- Partially fulfilled  
- Backorders  

Older docs that describe packing as **"lot-based"** (scanning items into lots / multi-lot management) do **not** match this UI. Treat packing as order/queue fulfillment work (Pack next-action / Packing Tasks), not a lot ledger on the Orders table.

## Bulk actions on the Orders page

With one or more orders selected, bulk actions appear in the action bar.

### Warehouse gating (confirmed live)

| Top-bar warehouse | Bulk actions shown |
|-------------------|--------------------|
| A **specific** warehouse | Bulk pick / Bulk pack / Bulk ship + Combine (and Allocate when applicable) |
| **All warehouses** | Warehouse-specific Bulk pick/pack/ship are **hidden**; Allocate + Combine remain |

Always check the warehouse selector before assuming bulk pick/pack/ship are missing.

## Per-order next actions

Each row exposes a single primary next action, for example:

- **Pick (N)** / **Pack (N)** / **Pack remaining (N)** / **Ship remaining (N)**  
- **View** for details  
- **More actions** (kebab) for extras such as **Cancel remaining**  

### Partial pick (confirmed)

On Pick, line quantities can default to **0**. Completing with less than the full amount opens an incomplete-pick choice:

1. Go back and keep picking  
2. Leave the rest unpicked → order can become **Partially Picked**  
3. Cancel the rest → order can become fully **Picked** (nothing left pending) — **not** the same as leaving unpicked  

Multi-line orders can pick different quantities per line; overall PROGRESS reflects the sum.

## Combine

- Select **2+** orders for the **same customer**  
- **Combine** merges them into a new combined order  
- Source orders disappear from the queue (not merely cancelled)  

Different-customer selection is rejected (precondition).

## Dedicated task pages (high level)

Use these when working from task lists rather than the Orders queue:

### Picking Tasks

- Create / work pick tasks (often from multiple ready-to-pick orders)  
- Scan items and complete quantities  

### Packing Tasks

- Pack picked work for shipping  
- **Not** documented here as lot containers — follow the on-screen Pack flow / tour  

### Shipping Tasks

- Ship packed work  
- Tracking / courier details when configured  

## Best practices

- Prefer a **specific warehouse** in the top bar when you need Bulk pick/pack/ship  
- Use **Work Queues** to focus Ready to pick / pack / ship  
- Use the row **next-action** button for single-order flow; use checkboxes + bulk bar for batches  
- Do not expect a **Packing** column or lot IDs on the Orders table — use **PROGRESS** + **STATUS**  

## Related automation

- Warehouse-gated bulk actions: `tests/orders/test_bulk_actions_warehouse_gating.py`  
- Partial pick outcomes: `tests/orders/test_partial_pick.py`  
- Combine: `tests/orders/test_combine_orders.py`  
- Progress column smoke: `tests/orders/test_view_orders.py`  

---
*Originally a thin "lot-based packing" outline reconstructed from the Friday claude.ai project on 2026-07-16. Rewritten 2026-09-18 to match the live Orders queue (PROGRESS/STATUS, Work Queues, warehouse-gated bulk actions) and to remove incorrect lot-based packing wording.*
