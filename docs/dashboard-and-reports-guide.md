# 📊 Dashboard Guide

How the Fridai Dashboard works in the live app (verified 2026-09-18).

## Dashboard (widget board)

After login you land on **`/dashboard`**. This is a **customizable widget board**, not a fixed KPI page.

### What is (and isn't) on the page

**Present:**
- Heading **Dashboard**
- Copy about customizing widgets and reordering via the grip handle
- Top-bar **warehouse selector** — widgets refresh for the selected warehouse
- **"+ Add Widget"** — add / remove / size widgets from a catalog (General / Operations / Network)

**Not present (older docs are wrong):**
- Fixed tiles for Active Orders / Inventory Summary / Recent Activity / Quick Actions
- A separate **Reports** area or nav item

### Empty state

If no widgets are configured yet: **"No widgets"** / "Get started by adding your first widget."

### Help

Top-bar **Help** opens: Help for this page / Getting Started (in-app tour) / Command palette.

## Reports

There is **no "Reports"** item in the main navigation. Navigating to `/reports` redirects to `/dashboard`. Use Dashboard widgets (and the rest of the app's list pages) for operational visibility instead.

---
*Originally a thin "Dashboard and Reports" outline reconstructed from the Friday claude.ai project on 2026-07-16. Rewritten 2026-09-18 to match the live widget-board Dashboard and the absence of a Reports nav.*
