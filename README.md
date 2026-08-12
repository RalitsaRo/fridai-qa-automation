# Fridai UI Automation Suite

Playwright + Python E2E automation for Fridai (the WMS Threecolts is building
as a future add-on to Hemi), built on the **Page Object Model**.

This repo was split out from the Hemi QA workspace on 2026-07-24 into its own
history at `https://github.com/RalitsaRo/fridai-qa-automation` — Fridai is a
separate product with its own app, its own login, and (currently) no
confirmed backend access, so there are no DB/SSH fixtures here. Hemi's
equivalent suite (`automation_ui/`, same Page Object Model conventions this
repo was originally modeled on) lives in the separate `hemi-qa-automation`
repo — the two are no longer sibling folders.

**Status: verified against the live app, including the full stock-provisioning
chain (2026-07-16).** `BASE_URL` points at Fridai's real instance
(`https://app.fridai.pro`) — the product owner has confirmed this is a
**test-phase environment** (no production exists yet), so tests creating
throwaway data are expected and fine, though it's still a real, shared
instance rather than an isolated per-test sandbox. 9/9 tests pass end-to-end,
including a Product → Purchase Order → Receiving → orderable-stock flow that
provisions its own test data from scratch.

Credentials (`FRIDAI_TEST_USER` / `FRIDAI_TEST_PASSWORD`) live in the local
`.env` (gitignored) — the user fills those in directly; the agent never
enters or displays them.

---

## Important: this app has no `data-testid` attributes

Unlike Hemi's `automation_ui/` (which locates everything via
`self.by_test_id("...")`), the real Fridai app was inspected and **has no
`data-testid` attributes anywhere**, and its modals have no `role="dialog"`
either — a modal is just a plain `<div>` rendered on top of the still-present
background page. `BasePage.by_test_id()` is kept only for parity with Hemi's
suite — it won't resolve anything real here. The actual locator strategy:

- `self.by_role("button", "Sign in")` — ARIA role + visible/accessible text (primary strategy)
- `self.by_placeholder("Email address")` — `<input placeholder="...">` when there's no button/heading role to key off
- `self.modal_scope("Create New Order", "Cancel")` — scopes to a modal container by finding the smallest ancestor `<div>` containing both its heading and some other unique-to-the-modal text. **Confirmed necessary**, not just defensive: querying the page directly for the "Create Order" modal's own "Next" button raised a Playwright strict-mode violation, because the Orders list page behind it has its own pagination "Next" button with the identical role+name.

See `pages/orders_page.py` and `pages/purchase_orders_page.py` for the fullest real-world examples of all three in combination.

---

## The full "you need a product to create an order" chain — now provable end to end

This came up during review and turned out to be deeper than it first looked:

1. **A Product record alone is not enough.** Creating a product (`ProductsPage.add_product()`) gives it zero stock.
2. Order creation's "Order Items" step is a **live search against products with available stock**, not just the catalog — a freshly created product does not appear in that search under any query.
3. Root cause, confirmed via Products → (row) → "Inventory": a new product's inventory view reads *"No inventory items — Inventory is created when you receive purchase orders. Create and receive a PO to get started."*
4. The real chain: **Product → Purchase Order (for that product) → Record ASN → Release for receiving → Receive it → stock becomes Available → product appears in Order Items search → order can be created.** No inline "create product"/"create PO" shortcut exists anywhere in Create Order.
5. `tests/inventory/test_receive_purchase_order.py` now walks this **entire chain from scratch** — creates a product, creates a PO for it, records its ASN, releases it for receiving, receives it via the scan-flow, and confirms it's orderable with the received quantity. `PurchaseOrdersPage` and `ReceivingPage` (in `pages/`) hold the real, verified locators for every step.

Two other tests cover the two ways this can fail for a user, without needing the full chain:
- `tests/orders/test_order_requires_product.py` — a product that doesn't exist at all returns nothing in Order Items search.
- `tests/orders/test_new_product_without_stock_not_orderable.py` — a product that exists but has zero stock *also* returns nothing (this is the one that actually matches what a new user hits).
- `tests/orders/test_create_order.py` (the plain happy path) still uses the pre-existing, already-stocked **"RaliPN1" / SKU "RaliP1"** rather than the full PO/receiving chain, since that'd be slower for a test that isn't about stock provisioning specifically.

Step 4 of `output/Friday/Friday_New_User_Getting_Started_Guide.docx` (v1.2) carries the user-facing, field-by-field version of this whole chain.

**Two real bugs found while building the Receiving flow:**
- Some seeded warehouse **location codes contained a Cyrillic "А" (U+0410) homoglyph** mixed with Latin characters (e.g. a location displaying identically to "RZ-A102-A-BIN01" was actually "RZ-\<CYRILLIC A\>102-A-BIN01") — hand-typing the Latin version got "Location not found." **Fixed 2026-07-16** — all 8 affected "RaliZone" locations' "Location Code" field were corrected via the app's own Locations > Edit Location > Save Changes UI. Verified with a fresh full-tree scan (0/412 locations now contain any non-ASCII character) and a live end-to-end test (hand-typing the plain Latin code into a real receiving flow now succeeds). `ReceivingPage.first_available_location_text()` still reads the real option text via JS as a defensive habit, even though the specific trap it was written for is now gone.
- The **"Or select location manually" dropdown does not work at all** — selecting an option fires no network request and leaves the step unchanged. This is a code-level bug (not a data issue), so it was **not fixed** — the scan/type text field is the only functional path, and remains the recommended approach in the guide.

**Separate gotcha found earlier:** the backend's `POST /crm/customers` call (fired when submitting Create Order) does real email-deliverability validation and rejects `.local` as a reserved special-use domain (HTTP 422). Use `data.test_emails.disposable_email()` for any customer email a test actually submits — see `data/test_emails.py`.

**Two timing races found and fixed** (both are `page.wait_for_timeout()` calls added to Page Object methods, not test-level workarounds): `ProductsPage.add_product()` and `PurchaseOrdersPage.submit_create_po()` each need a brief settle period before a caller searches for the just-created record elsewhere — otherwise the search can run against stale/unindexed data.

---

## Read the docs — then read the "reality" notes

The 5 Fridai reference guides are mirrored here from the source claude.ai
project (see `MEMORY.md` at the workspace root for the full project entry).
They're a useful map, but a live-DOM inspection on 2026-07-16 found the real
app diverges from them substantially:

1. [`docs/getting-started.md`](docs/getting-started.md) — describes a Dashboard with Active Orders / Inventory Summary / Recent Activity / Quick Actions. **None of that exists.** The real Dashboard is a customizable widget board. Also: the documented "Forgot Password" link does not exist on the real login page.
2. [`docs/order-management-guide.md`](docs/order-management-guide.md) — its 9-status order list (vs. Getting Started's 6) is the one confirmed correct. The Orders page lives at `/orders-list`, not `/orders`. Docs describe "Save Draft" and "Confirm Order" as two distinct final actions — **the real UI only has "Create Order."**
3. [`docs/inventory-management-guide.md`](docs/inventory-management-guide.md) — a thin outline; doesn't mention that inventory is *only* created via received Purchase Orders (the whole chain above), nor the real PO lifecycle (Draft → Placed → Supplier shipped → Ready to receive → Partially received → Received → Completed/Cancelled).
4. [`docs/bulk-operations-guide.md`](docs/bulk-operations-guide.md) — describes packing as lot-based; the real Orders table has a **Packing** column separate from **Status**.
5. [`docs/dashboard-and-reports-guide.md`](docs/dashboard-and-reports-guide.md) — thin outline; no real "Reports" nav item was found at all.

**Real nav structure** (confirmed live, a nested accordion — click a section to expand it, then click the sub-item):
- **Dashboard** (+ "Dashboard Pulse" — undocumented)
- **Inventory Management** → Products, Inventory, Stock Movements, Cycle Count Tasks, Purchase Orders, Receiving, Locations
- **Orders & Fulfillment** → Orders, Returns, Picking Tasks, Packing Tasks, Shipping Tasks
- **CRM & Suppliers** → Customers, Suppliers
- **Settings** → User Management, Integrations, Print stations

---

## Stack

- **Python** 3.10+ (this machine's poetry env ended up on 3.14 — works fine, no compile issues)
- **Playwright** (via `pytest-playwright`)
- **pytest** for discovery, markers, and reporting
- **poetry** for dependency management
- **python-dotenv** for local env config

---

## Layout

```
friday_automation_ui/
├── pages/
│   ├── __init__.py
│   ├── base_page.py         # by_role()/by_placeholder()/modal_scope() — the real locator strategy
│   ├── login_page.py        # verified
│   ├── dashboard_page.py    # verified
│   ├── orders_page.py       # verified, incl. the full 2-step Create Order wizard
│   ├── products_page.py     # verified, incl. the Add Product form
│   ├── purchase_orders_page.py  # verified: create PO, Record ASN, Release for receiving
│   └── receiving_page.py    # verified: the scan-based receiving queue + per-PO flow
├── tests/
│   ├── conftest.py          # fixtures: env loading, base URL, real login (waits for Dashboard to settle)
│   ├── smoke/
│   ├── orders/               # create-order happy path + 2 stock-dependency regression tests
│   ├── products/
│   └── inventory/            # full Product -> PO -> Receiving -> orderable chain, end to end
├── fixtures/                # reusable setup helpers (currently empty — see fixtures/README.md)
├── data/                    # static test data — test_emails.py (see the email gotcha above)
├── docs/                    # Fridai reference guides (mirrored from the claude.ai project)
├── pyproject.toml
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

---

## First-time setup

```bash
# 1. Install poetry (one-time, machine-wide) if not already present:
#    https://python-poetry.org/docs/#installation

# 2. Install Python dependencies into a project-local venv.
poetry install

# 3. Install Playwright browsers (chromium is enough for local runs).
poetry run playwright install chromium

# 4. A `.env` already exists with BASE_URL=https://app.fridai.pro filled in.
#    Add your own FRIDAI_TEST_USER / FRIDAI_TEST_PASSWORD to it — it's
#    gitignored, so this never gets committed.
```

Until `FRIDAI_TEST_USER` / `FRIDAI_TEST_PASSWORD` are filled in, any test
using `authenticated_page` will fail fast with a clear `RuntimeError` rather
than hanging or giving a confusing Playwright timeout. `test_homepage_loads`
doesn't need credentials and can run as soon as `BASE_URL` resolves.

---

## Running tests

```bash
# Run everything (9 tests, ~50s). Test-phase env — safe to run freely.
poetry run pytest

# Run only smoke tests.
poetry run pytest -m smoke

# Run a single file or test in headed mode for debugging.
poetry run pytest tests/inventory/test_receive_purchase_order.py --headed
```

`test_create_order.py`, `test_new_product_without_stock_not_orderable.py`, and
`test_receive_purchase_order.py` each create real data (an order, a product,
or a product + PO) every run — fine given the test-phase environment, but be
aware the Products/Orders/Purchase Orders lists will accumulate
automation-created rows over time.

---

## Conventions

**Page Objects** (`pages/`):
- Subclass `BasePage`.
- One class per page or major component.
- Locators via `self.by_role(role, name)` / `self.by_placeholder(text)` / `self.modal_scope(heading, other_text)` — this app has no `data-testid` or `role="dialog"`, so `self.by_test_id(...)` is a dead end here (kept only for parity with Hemi's suite).
- Methods expose business actions: `login(user, pw)`, `open_orders()`, `set_customer_name(name)`, `record_asn_skip_import(po_number)`.
- **No assertions inside Page Objects** — they describe capability, not expectation.
- If a real-app timing quirk shows up (a search racing a just-created record, a modal needing a settle delay), fix it **inside the Page Object method**, not by scattering `wait_for_timeout()` calls across every test that happens to hit it.

**Tests** (`tests/`):
- Mirror manual TC / BDD scenario structure.
- Call Page Object methods; never instantiate raw locators.
- Hold all `expect()` assertions.
- Tag with markers: `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.critical`, `@pytest.mark.negative`, etc.

**Fixtures** (`tests/conftest.py`, `fixtures/`):
- Session-scoped for env loading and config.
- `authenticated_page` performs a real login via `LoginPage`, then waits for the Dashboard heading to render before returning — a hard `goto()` right after login can otherwise race the post-login redirect (confirmed live). If Fridai ever adds CAPTCHA, switch to the saved-auth-state pattern used in Hemi's `automation_ui/tests/conftest.py` (separate repo — see above).

**Data** (`data/`):
- JSON / CSV / Python constants. No secrets — credentials go in `.env`. `test_emails.py` holds the one confirmed gotcha (don't use `.local` domains — see above).

---

## Adding a new page

1. Create `pages/<name>_page.py` with a class extending `BasePage`.
2. Define locators inside the class via `self.by_role(...)` / `self.by_placeholder(...)`. If the page has a modal, use `self.modal_scope(heading, other_text)` rather than querying the page directly — assume background content is still present and can collide.
3. Expose business actions as methods.
4. Set `path = "/your/route"` so `goto()` works — verify the real route first; this app's SPA routing doesn't always match what you'd guess (`/orders-list`, not `/orders`).
5. Add a test under `tests/<area>/test_<flow>.py` that uses the Page Object and holds assertions.

## Fridai has its own built-in onboarding tour (discovered 2026-07-24)

Click "Help" (top right, once logged in) → "Getting Started" for an interactive, progress-tracked, two-part tutorial with tooltips pointing at the real UI (not videos, despite the "Watch again" label). It confirms — in the product's own words — several things we'd already reverse-engineered, plus some we hadn't tested:

- **Tutorial 1 — Warehouse setup**: Create locations → Create a supplier ("Suppliers represent who you buy from. You need one before raising a purchase order.") → Create or import products → Establish stock (explicit choice of **Purchase order receive** or **Cycle count**, the latter untested by us).
- **Tutorial 2 — Order fulfilment**: Create a customer (standalone, via CRM & Suppliers > Customers) → Create a sales order ("Fridai allocates on create") → Pick (Picking Tasks) → Pack (Packing Tasks — "Labels are optional until a courier is configured") → Ship (Shipping Tasks) → Review stock movements (Stock Movements ledger).

`output/Friday/Friday_New_User_Getting_Started_Guide.docx` (v1.4) now incorporates all of this. See the workspace `MEMORY.md` (Hemi repo) for the full write-up.

## Known follow-ups

1. Build Page Objects for Suppliers, standalone Customer creation, Picking/Packing/Shipping Tasks, Stock Movements, and Cycle Count — the tour above confirms what each does, but none have been walked through field-by-field by us yet.
2. Chase the "Ready to receive"/"Partially Received" → "Received" → "Completed" transitions if a test ever needs a PO in exactly that state (not needed for a product to become orderable — confirmed that happens at "Partially Received" already).
3. Formalize all the doc-vs-reality gaps and the two real bugs (location homoglyphs, non-functional location dropdown) into the workspace's Documentation Validation Report (`G:\My Drive\Rali\Fridai\outputs\Friday\Friday_Validation_Report.docx`).
