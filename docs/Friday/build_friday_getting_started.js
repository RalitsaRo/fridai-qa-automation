const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, HeadingLevel, ShadingType,
} = require("docx");
const fs = require("fs");

const FONT = "Calibri";
const BLACK = "000000";
const PAGE = { width: 12240, height: 15840 }; // US Letter

const cellBorder = {
  top: { style: BorderStyle.SINGLE, size: 4, color: BLACK },
  bottom: { style: BorderStyle.SINGLE, size: 4, color: BLACK },
  left: { style: BorderStyle.SINGLE, size: 4, color: BLACK },
  right: { style: BorderStyle.SINGLE, size: 4, color: BLACK },
};

function headerCell(text, width) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders: cellBorder,
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "FFFFFF" },
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, font: FONT, size: 22, color: BLACK })] })],
  });
}

function bodyCell(text, width, opts = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders: cellBorder,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text, font: FONT, size: 20, color: BLACK, bold: opts.bold || false })] })],
  });
}

function title(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, font: FONT, size: 52, color: BLACK })],
    spacing: { after: 200 },
  });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, font: FONT, size: 32, color: BLACK })],
    spacing: { before: 320, after: 160 },
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, font: FONT, size: 24, color: BLACK })],
    spacing: { before: 240, after: 100 },
  });
}
function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, font: FONT, size: 22, color: BLACK, italics: opts.italics || false, bold: opts.bold || false })],
    spacing: { after: 140 },
  });
}
function bullet(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, font: FONT, size: 22, color: BLACK, italics: opts.italics || false })],
    bullet: { level: 0 },
    spacing: { after: 80 },
  });
}
function numberedStep(text, listRef) {
  return new Paragraph({
    children: [new TextRun({ text, font: FONT, size: 22, color: BLACK })],
    numbering: { reference: listRef, level: 0 },
    spacing: { after: 80 },
  });
}
function note(text) {
  return new Paragraph({
    children: [new TextRun({ text: "Note: " + text, font: FONT, size: 20, color: "444444", italics: true })],
    spacing: { after: 160 },
    indent: { left: 360 },
  });
}
function warning(text) {
  return new Paragraph({
    children: [new TextRun({ text: "\u26A0 " + text, font: FONT, size: 22, color: BLACK, bold: true })],
    spacing: { after: 140 },
  });
}

// ---- Summary of Changes ---------------------------------------------------

const SOC_WIDTHS = [1400, 1600, 1800, 5400];
const summaryTable = new Table({
  width: { size: 10200, type: WidthType.DXA },
  columnWidths: SOC_WIDTHS,
  rows: [
    new TableRow({ children: [headerCell("Version", SOC_WIDTHS[0]), headerCell("Date", SOC_WIDTHS[1]), headerCell("Author", SOC_WIDTHS[2]), headerCell("Description of Change", SOC_WIDTHS[3])] }),
    new TableRow({
      children: [
        bodyCell("1.0", SOC_WIDTHS[0]),
        bodyCell("2026-07-16", SOC_WIDTHS[1]),
        bodyCell("QA (Fridai project)", SOC_WIDTHS[2]),
        bodyCell("Initial version. Combines the source Fridai documentation with live verification against https://app.fridai.pro (test-phase instance) so a new user knows exactly what to expect and what's still unconfirmed.", SOC_WIDTHS[3]),
      ],
    }),
    new TableRow({
      children: [
        bodyCell("1.1", SOC_WIDTHS[0]),
        bodyCell("2026-07-16", SOC_WIDTHS[1]),
        bodyCell("QA (Fridai project)", SOC_WIDTHS[2]),
        bodyCell("Verified the full order-creation flow live, including the \"Add Product\" and \"Create Order\" forms. Found and documented a real prerequisite: a new product has zero stock and cannot be added to an order until a Purchase Order for it has been received. Updated the Add Product step with real fields and the Create Order step with real fields and a corrected final action (\"Create Order\", not \"Save Draft\"/\"Confirm Order\").", SOC_WIDTHS[3]),
      ],
    }),
    new TableRow({
      children: [
        bodyCell("1.2", SOC_WIDTHS[0]),
        bodyCell("2026-07-16", SOC_WIDTHS[1]),
        bodyCell("QA (Fridai project)", SOC_WIDTHS[2]),
        bodyCell("Walked the full stock-provisioning chain live, field by field: Create Purchase Order → Record ASN → Release for receiving → Receiving scan flow. Found two more real issues: some warehouse location codes contain a Cyrillic \"А\" homoglyph indistinguishable from a normal letter, and the \"select location manually\" dropdown next to the scan field does not work at all. Both called out as warnings.", SOC_WIDTHS[3]),
      ],
    }),
    new TableRow({
      children: [
        bodyCell("1.3", SOC_WIDTHS[0]),
        bodyCell("2026-07-16", SOC_WIDTHS[1]),
        bodyCell("QA (Fridai project)", SOC_WIDTHS[2]),
        bodyCell("The Cyrillic-homoglyph location codes (8 locations under the \"RaliZone\" zone) have been fixed directly in the app — corrected via Locations > Edit Location > Save Changes, verified with a fresh scan of all locations (zero remaining) and a live hand-typed receiving test. The \"select location manually\" dropdown issue is unrelated to location data and remains unfixed (a code-level issue) — that warning stays.", SOC_WIDTHS[3]),
      ],
    }),
    new TableRow({
      children: [
        bodyCell("1.4", SOC_WIDTHS[0]),
        bodyCell("2026-07-24", SOC_WIDTHS[1]),
        bodyCell("QA (Fridai project)", SOC_WIDTHS[2]),
        bodyCell("Discovered Fridai's own built-in onboarding tour (Help, top right → \"Getting Started\") — an interactive, progress-tracked walkthrough covering the same journey in two parts (Warehouse Setup, Order Fulfilment). Walked all 10 of its steps live and folded the confirmed content in: a new \"Create a Supplier\" step (previously missing entirely), an alternative Cycle Count path for establishing stock, and a fully rewritten Order Fulfilment section (Pick / Pack / Ship / Review Stock Movements) using the tool's own confirmed step descriptions. Also confirmed the Command Palette (Ctrl+K) is real, not just documented. Renumbered all subsequent steps to fit the new content.", SOC_WIDTHS[3]),
      ],
    }),
    new TableRow({
      children: [
        bodyCell("1.5", SOC_WIDTHS[0]),
        bodyCell("2026-07-31", SOC_WIDTHS[1]),
        bodyCell("QA (Fridai project)", SOC_WIDTHS[2]),
        bodyCell("Tested this entire guide, step by step, against a genuinely new registration with zero existing data (not our seeded test account). Found a critical gap: this guide never had a \"Create Your First Location\" step, and a brand-new account starts with 0 locations — Step 6a's \"Create Purchase Order\" would fail immediately because the Receiving Location dropdown is empty. Fixed by adding a new Step 3, documenting the real 5-step Create Location wizard (Zone → Aisle → Bay → Bin → Review) end to end. Also confirmed the real Add Supplier form fields (previously \"not yet inspected\"), and verified the entire chain — Location → Supplier → Product → Purchase Order → Receive → Order — works correctly end to end on a blank account once done in the right order. Found a real bug along the way: the \"Getting Started\" tour shows 100% (10/10 steps) complete even on this zero-data account, even immediately after clicking \"Reset progress\" — contradicts its own claim that \"progress follows warehouse data.\" All subsequent steps renumbered.", SOC_WIDTHS[3]),
      ],
    }),
    new TableRow({
      children: [
        bodyCell("1.6", SOC_WIDTHS[0]),
        bodyCell("2026-08-14", SOC_WIDTHS[1]),
        bodyCell("QA (Fridai project)", SOC_WIDTHS[2]),
        bodyCell("Covers the Aug 10, 2026 multi-warehouse release, verified live 2026-08-11 through 2026-08-13. Step 2 (Dashboard & Navigation) updated with the new top-bar warehouse selector and the categorized \"Add Widget\" catalog (General/Operations/Network). New Step 3 — \"Set Up & Understand Warehouses\" — walks the Add Warehouse form field by field, including Priority and the \"Web fulfilment allowed\" flag (the setting that will matter once Fridai integrates with Hemi). All subsequent steps renumbered (old Steps 3–10 are now Steps 4–9, 11, 12). Steps 7a (Create Purchase Order) and 8 (Create Order) updated for a new auto-filled, disabled Warehouse field in both modals. New Step 10 — \"Split & Reallocate Orders\" — documents both new Order Ops actions on an order's detail view: Reallocate (whole-order move to a different warehouse) and Split (fork part of an order's units into a new sibling order, at individual sub-line granularity). Confirmed the Create Order Channel field still has no \"Web\" option and clarified that's expected — Fridai isn't receiving Hemi-sourced orders yet; readiness lives at the per-warehouse \"Web fulfilment allowed\" flag instead. Also flagged a real UX issue: warehouses can end up with duplicate auto-generated names (\"Second warehouse\") if not renamed at creation. Status table updated throughout.", SOC_WIDTHS[3]),
      ],
    }),
    new TableRow({
      children: [
        bodyCell("1.7", SOC_WIDTHS[0]),
        bodyCell("2026-08-17", SOC_WIDTHS[1]),
        bodyCell("QA (Fridai project)", SOC_WIDTHS[2]),
        bodyCell("CORRECTION: the \"select location manually\" dropdown at Step 7d (Receive it) was wrongly marked broken since v1.2 (2026-07-16). Re-verified live: it works correctly — the earlier check selected an option but never pressed Enter afterward, which is what the screen's own instruction text says to do (\"Scan location or select from list, then press Enter to confirm.\"). Selecting an option and pressing Enter fires the real receive request and completes the line, identical to the scan-text path. Step 7d's warning rewritten accordingly.", SOC_WIDTHS[3]),
      ],
    }),
  ],
});

// ---- Status legend table ---------------------------------------------------

const STAT_WIDTHS = [4200, 6000];
const statusTable = new Table({
  width: { size: 10200, type: WidthType.DXA },
  columnWidths: STAT_WIDTHS,
  rows: [
    new TableRow({ children: [headerCell("Area", STAT_WIDTHS[0]), headerCell("Status", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Login", STAT_WIDTHS[0]), bodyCell("Verified live 2026-07-16", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Dashboard", STAT_WIDTHS[0]), bodyCell("Verified live — a customizable widget board (Best Selling Products, Dead Stock, Sales, Returns, Low Stock Alerts confirmed present); differs substantially from older written docs", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Top-bar warehouse selector", STAT_WIDTHS[0]), bodyCell("NEW, verified live 2026-08-11 (Aug 10 multi-warehouse release) — scopes the Dashboard, Orders, Purchase Orders, and more to one warehouse or \"All warehouses\"; see Step 2", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("\"+ Add Widget\" catalog", STAT_WIDTHS[0]), bodyCell("Verified live 2026-08-12 — categorized General/Operations/Network catalog with per-widget descriptions and size controls; see Step 2", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Help menu (Help for this page / Getting Started / Command palette)", STAT_WIDTHS[0]), bodyCell("Verified live 2026-07-24 — all three options confirmed real, incl. the interactive onboarding tour and a working Ctrl+K command palette", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Left-nav structure", STAT_WIDTHS[0]), bodyCell("Verified live", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Settings > Warehouses > Add Warehouse form", STAT_WIDTHS[0]), bodyCell("NEW, verified live 2026-08-12, all fields — Name is the only required field; Priority and \"Web fulfilment allowed\" confirmed; see Step 3", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Products list page", STAT_WIDTHS[0]), bodyCell("Verified live", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("\"Add Product\" form fields", STAT_WIDTHS[0]), bodyCell("Verified live — SKU and Product Name are required; Barcode, Purchase Price, Low Stock Threshold, Status, and Description are optional", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Create Location wizard (Zone/Aisle/Bay/Bin/Review)", STAT_WIDTHS[0]), bodyCell("Verified live end to end on a brand-new account with 0 locations — a real location was created and immediately usable for a Purchase Order", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Suppliers page + \"Add Supplier\" form fields", STAT_WIDTHS[0]), bodyCell("Verified live, all fields — Name is the only required field", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("New product has zero stock until a PO is received", STAT_WIDTHS[0]), bodyCell("Verified live", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Full chain works on a genuinely blank, newly-registered account", STAT_WIDTHS[0]), bodyCell("Verified live 2026-07-31 end to end: Location → Supplier → Product → Purchase Order → Receive → Order, tested on a fresh registration with zero prior data (not our seeded test account)", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("\"Getting Started\" tour completion tracking", STAT_WIDTHS[0]), bodyCell("Real bug found 2026-07-31 — shows 100% (10/10 steps) complete on a brand-new, zero-data account, even immediately after clicking \"Reset progress.\" Contradicts its own subtitle (\"Progress follows warehouse data\"). Not yet reported to the dev team.", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Cycle Count as an alternative to Purchase-Order receiving", STAT_WIDTHS[0]), bodyCell("Documented via the app's own onboarding tour; not yet walked through by us", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Orders & Fulfillment list page", STAT_WIDTHS[0]), bodyCell("Verified live, incl. the Packing column and (new, 2026-08-11) a Warehouse column", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("\"Create Order\" form fields (both steps)", STAT_WIDTHS[0]), bodyCell("Verified live — Customer Name and Email are required; Channel options are \"Direct to Consumer\"/\"Business to Business\" only (no \"Web\" option — confirmed expected, see Step 8); final action is \"Create Order\" (no separate \"Save Draft\")", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Create Order / Create Purchase Order: auto-filled Warehouse field", STAT_WIDTHS[0]), bodyCell("NEW, verified live 2026-08-11 — always disabled, pre-filled from the top-bar warehouse selector; see Steps 7a and 8", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Order \"Reallocate\" and \"Split\" actions", STAT_WIDTHS[0]), bodyCell("NEW, verified live 2026-08-13, both modals field by field; see Step 10", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Standalone \"Create a Customer\" (CRM & Suppliers)", STAT_WIDTHS[0]), bodyCell("Documented via the app's own onboarding tour; not yet walked through by us (we've only used inline customer creation during order creation)", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Order Items product search requires available stock", STAT_WIDTHS[0]), bodyCell("Verified live — a product search only returns products with received stock; a brand-new product does not appear", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Order row actions (View/Pick/Pack/Ship/Cancel)", STAT_WIDTHS[0]), bodyCell("Buttons confirmed present; the Picking/Packing/Shipping Tasks pages they open are described by the app's own tour but not yet walked through by us", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Purchase Orders: create, Record ASN, Release for receiving, Receiving scan flow", STAT_WIDTHS[0]), bodyCell("Verified live, end to end (Draft → Placed → Supplier shipped → Ready to receive → Partially received) — a product was confirmed orderable immediately after receiving", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Stock Transfers", STAT_WIDTHS[0]), bodyCell("NEW nav item confirmed live 2026-08-11 (Inventory Management > Stock Transfers) — moves stock between warehouses; not yet walked through by us", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Stock Movements ledger", STAT_WIDTHS[0]), bodyCell("Documented via the app's own onboarding tour (\"every receive, pick, ship, and count writes a movement\"); not yet walked through by us", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Warehouse location codes (Cyrillic homoglyph)", STAT_WIDTHS[0]), bodyCell("FIXED 2026-07-16 — all 8 affected locations corrected; verified across all locations", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("\"Select location manually\" dropdown", STAT_WIDTHS[0]), bodyCell("CORRECTED 2026-08-17 — works fine. Select an option, then press Enter (same pattern as the scan field) — fires the real receive request. A prior version of this guide wrongly called it broken; that check never pressed Enter after selecting.", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Duplicate warehouse naming", STAT_WIDTHS[0]), bodyCell("Real UX issue found 2026-08-11 on our seeded test account — multiple warehouses left at their default name all read \"Second warehouse\"; always set a distinct Name when creating one (see Step 3)", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("\"Web\" order channel / Hemi integration readiness", STAT_WIDTHS[0]), bodyCell("Confirmed live 2026-08-12 — not a Create Order channel today; readiness is the per-warehouse \"Web fulfilment allowed\" flag (Step 3), since Fridai isn't yet integrated with Hemi", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Inventory, Locations, Cycle Count Tasks", STAT_WIDTHS[0]), bodyCell("Reachable from the sidebar (confirmed); most contents not inspected in detail", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Settings (User Management, Integrations, Print stations)", STAT_WIDTHS[0]), bodyCell("Reachable from the sidebar (confirmed); contents not inspected", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("Returns", STAT_WIDTHS[0]), bodyCell("Documented only, not inspected", STAT_WIDTHS[1])] }),
    new TableRow({ children: [bodyCell("\"Forgot Password\" link", STAT_WIDTHS[0]), bodyCell("NOT found on the live login page, despite being described in the docs", STAT_WIDTHS[1])] }),
  ],
});

// ---- Document --------------------------------------------------------------

const doc = new Document({
  numbering: {
    config: [
      { reference: "step1-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step3-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step4-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step5-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step6-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step7a-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step7b-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step7c-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step7d-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step8-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step10a-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
      { reference: "step10b-numbering", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: "start" }] },
    ],
  },
  sections: [
    {
      properties: { page: { size: PAGE, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
      children: [
        title("Friday (Fridai WMS) — New User Getting Started Guide"),
        body("Reviewed instance: https://app.fridai.pro (test phase, no production environment yet). Covers the Aug 10, 2026 multi-warehouse release.", { italics: true }),

        h1("Summary of Changes"),
        summaryTable,

        h1("Before You Start"),
        bullet("You'll need a Fridai login — an email address and password provided by your administrator."),
        bullet("The app lives at https://app.fridai.pro — bookmark this rather than any deeper page URL for now (see the navigation tip in Step 2)."),
        bullet("Use a desktop browser (Chrome, Firefox, or Edge). Mobile has not been tested."),
        note("there is currently no confirmed self-service \"Forgot Password\" flow (see Step 1) — if you don't have credentials yet, ask your administrator directly."),
        note("Fridai has its own built-in, interactive onboarding tour — click \"Help\" (top right) once logged in, then \"Getting Started.\" It covers the exact same journey as this document, in two parts (Warehouse Setup, ~20 min; Order Fulfilment, ~25 min), with tooltips pointing at the real UI and progress tracking. This document is a companion reference, cross-checked against the live app — use the in-app tour for hands-on, click-by-click guidance, and this document for what's confirmed vs. still unverified."),
        note("as of the Aug 10, 2026 release, Fridai supports multiple warehouses per account. If you only ever use one warehouse, most of this still applies unchanged — Step 3 explains what's new and when it matters."),

        h1("Step-by-Step Guide"),

        h2("Step 1 — Log In  (Verified live)"),
        numberedStep("Go to https://app.fridai.pro", "step1-numbering"),
        numberedStep("Enter your email address in the \"Email address\" field", "step1-numbering"),
        numberedStep("Enter your password in the \"Password\" field", "step1-numbering"),
        numberedStep("Click \"Sign in\"", "step1-numbering"),
        note("older documentation mentions a \"Forgot Password\" link on this screen, but it was not found on the live login page as of 2026-07-16. If you're locked out, contact your administrator to reset your password directly."),

        h2("Step 2 — Get Oriented: Dashboard & Navigation  (Verified live)"),
        body("After logging in, you'll land on the Dashboard — a customizable widget board. This is different from what some older documentation describes (an \"Active Orders / Inventory Summary\" style overview) — the real Dashboard instead shows a mix of widgets you control, for example:"),
        bullet("Best Selling Products, Sales, and Returns — performance widgets with selectable time ranges"),
        bullet("Dead Stock and Low Stock Alerts — inventory-health widgets flagging products that need attention"),
        bullet("A \"+ Add Widget\" button to add, remove, or rearrange what you see"),
        body("Confirmed live 2026-08-12: \"+ Add Widget\" opens a categorized catalog, each with a live description and Width/Height size controls:"),
        bullet("General — Sales, Best Selling Products, Returns Report"),
        bullet("Operations — Low Stock Alerts, Dead Stock Tracker, Alert Overview, Fulfillment Backlog, Short-Allocated Orders, Receiving Pulse, Today's Throughput, Days of Supply"),
        bullet("Network (marked ADMIN) — Transfers In Flight, Inventory Imbalance — network-wide views across all your warehouses"),
        body("Confirmed live 2026-08-11 (the Aug 10 multi-warehouse release): a warehouse selector now sits in the top bar, to the left of the Help button. It defaults to one of your warehouses, and can be switched to any other one you have, or to \"All warehouses\" (visible to Administrators). Whichever you pick scopes almost everything else in the app — the Dashboard, Orders list, Purchase Orders, and more all show only that warehouse's data. If something you expect to see is missing, check this selector first.", { bold: false }),
        body("The left sidebar is your main navigation. It's organized as expandable sections — click a section name to expand it, then click the specific item you want:"),
        bullet("Dashboard  →  Dashboard Pulse"),
        bullet("Inventory Management  →  Products, Inventory, Stock Movements, Stock Transfers, Cycle Count Tasks, Purchase Orders, Receiving, Locations"),
        bullet("Orders & Fulfillment  →  Orders, Returns, Picking Tasks, Packing Tasks, Shipping Tasks"),
        bullet("CRM & Suppliers  →  Customers, Suppliers"),
        bullet("Settings  →  User Management, Integrations, Warehouses, Print stations"),
        body("In the top right, a \"Help\" button opens three confirmed options:"),
        bullet("Help for this page — context help for wherever you currently are"),
        bullet("Getting Started — the official interactive onboarding tour described above"),
        bullet("Command palette (Ctrl+K / Cmd+K) — confirmed working, not just documented; a quick way to jump anywhere in the system"),
        note("don't type page addresses directly into the browser's address bar for Orders specifically — a direct link to /orders currently leads to a broken page. Always reach Orders by expanding \"Orders & Fulfillment\" in the sidebar and clicking \"Orders\", which works correctly every time."),

        h2("Step 3 — Set Up & Understand Warehouses  (NEW — Verified live 2026-08-11/12)"),
        body("Since the Aug 10, 2026 release, a Fridai account can have more than one warehouse. Each warehouse has its own locations, its own stock, and its own view of orders/dashboards (via the top-bar selector from Step 2). If you only need one warehouse, you can skip straight to Step 4 — Fridai creates a default one for you. Read on if you need to add another, or want to understand what each warehouse setting actually does."),
        numberedStep("Expand \"Settings\" in the sidebar and click \"Warehouses\"", "step3-numbering"),
        numberedStep("Click \"+ Add Warehouse\"", "step3-numbering"),
        numberedStep("Fill in Name (required — pick something distinct; see the warning below) — Code is auto-generated if left blank", "step3-numbering"),
        numberedStep("Optionally fill in the address block: Address Line 1/2, City, State, Postal Code, Country, Phone", "step3-numbering"),
        numberedStep("Set Priority — a number where lower = higher priority. This decides which warehouse gets picked from first when more than one of your warehouses could fulfil the same order", "step3-numbering"),
        numberedStep("Choose a Warehouse Type (e.g. \"Distribution Center\")", "step3-numbering"),
        numberedStep("Check the 4 capability checkboxes as needed: \"Fulfillment enabled\", \"Receiving enabled\", and \"Active\" are checked by default; \"Web fulfilment allowed\" is unchecked by default (see note below); \"Default network fallback\" is also unchecked by default", "step3-numbering"),
        numberedStep("Click \"Create Warehouse\"", "step3-numbering"),
        note("\"Web fulfilment allowed\" is the setting that will matter once Fridai is integrated with Hemi. Only warehouses with this checked will be eligible to receive and fulfil orders from that future integration — combined with Priority, it decides which eligible warehouse is picked from first. As of this writing (test phase, pre-integration), checking it has no visible effect yet, but it's worth setting correctly now on whichever warehouse(s) should serve Hemi-sourced orders once that integration goes live. There is no \"Web\" channel option in Create Order (Step 8) — this warehouse-level flag is the real mechanism, not a Channel choice."),
        warning("real issue found live 2026-08-11: if you leave the Name field at whatever default the app suggests, multiple warehouses can end up all displaying as \"Second warehouse\" in the top-bar selector and everywhere else — indistinguishable from each other. Always type a distinct, meaningful Name (e.g. \"UK Fulfilment Center\", not \"Second warehouse\") when creating a warehouse."),

        h2("Step 4 — Create Your First Location  (Verified live end to end, incl. on a brand-new account)"),
        body("⚠ Do not skip this step. A brand-new account (or a brand-new warehouse) starts with ZERO locations. Without at least one, Step 7a (\"Create a Purchase Order\") will fail — its Receiving Location dropdown will be empty with nowhere to put incoming stock. This was confirmed live on a genuinely new registration: the guide broke here before this step existed.", { bold: false }),
        body("Fridai locations are a 5-level wizard: Zone → Aisle → Bay → Bin → Review. It sounds like a lot, but each level follows the exact same pattern."),
        numberedStep("Expand \"Inventory Management\" in the sidebar and click \"Locations\"", "step4-numbering"),
        numberedStep("Click \"Create Location\"", "step4-numbering"),
        numberedStep("Zone: click \"Create new\" and type a zone name (e.g. \"Main Zone\"), then click \"Next: Aisle\"", "step4-numbering"),
        numberedStep("Aisle: click \"Create new\" and type an aisle name (e.g. \"A1\"), then click \"Next: Bay\"", "step4-numbering"),
        numberedStep("Bay: click \"Create new\" and type a bay name (e.g. \"B1\"), then click \"Next: Bin\"", "step4-numbering"),
        numberedStep("Bin: enter a bin code/name (e.g. \"BIN01\") — a Location Code is auto-generated by combining Zone + Aisle + Bay + Bin (e.g. \"MainZoneA1B1BIN01\"); click \"Customize\" if you want to override it, otherwise click \"Next: Review\"", "step4-numbering"),
        numberedStep("Review shows your full path and the final location code — click \"Create location\" to finish", "step4-numbering"),
        note("if you already have zones/aisles/bays set up, each step offers a dropdown of existing ones instead of forcing you to create new — this wizard is only this long the very first time."),
        note("locations belong to whichever warehouse is active in the top-bar selector (Step 2) at the time you create them — double-check the selector first if you have more than one warehouse."),

        h2("Step 5 — Create a Supplier  (Verified live, incl. all form fields)"),
        body("Suppliers represent who you buy from. Fridai requires one to exist before you can raise a Purchase Order — confirmed both by our own testing and by the app's own official onboarding tour, which states this explicitly."),
        numberedStep("Expand \"CRM & Suppliers\" in the sidebar and click \"Suppliers\"", "step5-numbering"),
        numberedStep("Click \"Add Supplier\"", "step5-numbering"),
        numberedStep("Fill in Name (required) — Email, Phone, Contact person, Status (Active/Inactive/Preferred), a full address block, and Notes are all optional", "step5-numbering"),
        numberedStep("Click \"Create Supplier\"", "step5-numbering"),
        note("if you already have a supplier set up, you can skip straight to Step 6."),

        h2("Step 6 — Add Your First Product  (Verified live)"),
        numberedStep("Expand \"Inventory Management\" in the sidebar and click \"Products\"", "step6-numbering"),
        numberedStep("You'll see the Products page, with a search bar (\"Search by name, SKU, or barcode...\") and your product list", "step6-numbering"),
        numberedStep("Click \"Add Product\"", "step6-numbering"),
        numberedStep("Fill in SKU and Product Name (both required) — Barcode, Default Purchase Price, Low Stock Threshold, Status, and Description are all optional", "step6-numbering"),
        numberedStep("Click \"Create Product\"", "step6-numbering"),
        note("a brand-new product has ZERO stock. It will not show up when you try to add it to an order until you complete Step 7 below — this trips up new users, so don't skip it."),

        h2("Step 7 — Get Your Product Into Stock  (Required before Step 8 — Verified live end to end, incl. on a brand-new account)"),
        body("This is the step the documentation doesn't really explain, and it's the one that actually blocks new users: a Product record by itself has no stock. Confirmed live — a brand-new product's Inventory view literally says:"),
        body("“No inventory items — Inventory is created when you receive purchase orders. Create and receive a PO to get started.”", { italics: true }),
        body("The full chain has 4 parts. It sounds like a lot for \"add some stock,\" but each part is quick:"),

        h2("7a. Create a Purchase Order"),
        numberedStep("Expand \"Inventory Management\" and click \"Purchase Orders\"", "step7a-numbering"),
        numberedStep("Click \"Create Purchase Order\"", "step7a-numbering"),
        numberedStep("Choose your Supplier (from Step 5)", "step7a-numbering"),
        numberedStep("A Warehouse field appears next — confirmed live 2026-08-11, it's always disabled and automatically filled from whichever warehouse is active in the top-bar selector (Step 2). You can't change it here; switch the top-bar selector first if you need a different warehouse", "step7a-numbering"),
        numberedStep("Choose your Receiving Location (from Step 4, required)", "step7a-numbering"),
        numberedStep("Initial status: choose \"Placed\" (skips an extra Draft step). Expected Delivery Date and Notes are optional", "step7a-numbering"),
        numberedStep("Click \"Next,\" then search for your product by name or SKU, click it, enter a quantity, and click \"Add\"", "step7a-numbering"),
        numberedStep("Click \"Create Purchase Order\" to finish — note the PO number shown (e.g. PO-3-000004)", "step7a-numbering"),

        h2("7b. Record ASN (Advance Shipping Notice)"),
        body("This moves the PO from \"Placed\" to \"Supplier shipped.\""),
        numberedStep("Find your PO in the list and click \"Record ASN\"", "step7b-numbering"),
        numberedStep("Click \"Expected matches PO\" (skips a CSV upload) — this reveals a \"Confirm\" button", "step7b-numbering"),
        numberedStep("Click \"Confirm\"", "step7b-numbering"),

        h2("7c. Release for receiving"),
        body("This moves the PO from \"Supplier shipped\" to \"Ready to receive,\" and is what makes it appear in the Receiving queue."),
        numberedStep("On the same PO row, click \"Release for receiving\"", "step7c-numbering"),
        numberedStep("A small form appears for landed costs (Shipping / Taxes / Misc) — all optional, leave blank if not needed", "step7c-numbering"),
        numberedStep("Click \"Release for receiving\" again to confirm", "step7c-numbering"),

        h2("7d. Receive it"),
        numberedStep("Expand \"Inventory Management\" and click \"Receiving\" — your PO should be in the queue", "step7d-numbering"),
        numberedStep("Click \"Start receiving\"", "step7d-numbering"),
        numberedStep("Scan (or type) the product's SKU or barcode, then press Enter", "step7d-numbering"),
        numberedStep("Confirm the quantity — it defaults to the full remaining amount; just press Enter to accept it", "step7d-numbering"),
        numberedStep("Scan (or type) the put-away location, then press Enter", "step7d-numbering"),
        numberedStep("Once it reads \"Complete!\", click \"Finish receiving\"", "step7d-numbering"),
        note("no keyboard scanner handy? Use the dropdown labeled \"Or select location manually\" instead of typing a code — pick a location from the list, then press Enter to confirm, exactly like the scan field. (Corrected 2026-08-17 — this guide previously said this dropdown didn't work; it does, the earlier check just never pressed Enter after selecting.) Confirmed live 2026-08-11: a page-wide warehouse selector was added to the top bar around this same time — it's unrelated to this dropdown and doesn't affect it."),
        note("your product becomes orderable as soon as this finishes — even though the Purchase Order's own status at that point may still read \"Partially Received\" rather than \"Received.\""),

        h2("Alternative: Cycle Count"),
        body("If your stock is already physically in the warehouse and you just need to record it — rather than receiving new inbound goods — Fridai's own onboarding tour describes a simpler alternative: start a cycle count from Inventory, or open an existing cycle-count task, to record floor quantities directly. No Purchase Order is needed for this path.", { italics: true }),
        note("we haven't walked this path ourselves yet — treat it as a documented option worth trying, not a fully verified one."),

        h2("Step 8 — Create Your First Order  (Verified live)"),
        body("⚠ Prerequisite: you need at least one product with available stock (Steps 6 + 7) before this step will work — the Order Items search below only returns products that have received stock, with no way to add an unstocked product."),
        numberedStep("Expand \"Orders & Fulfillment\" in the sidebar and click \"Orders\" — you'll land on the Orders & Fulfillment page", "step8-numbering"),
        numberedStep("Click \"Create Order\"", "step8-numbering"),
        numberedStep("Fill in Customer Name and Email (both required); Phone and Address are optional", "step8-numbering"),
        numberedStep("Choose a Channel: \"Direct to Consumer\" or \"Business to Business\" — confirmed live 2026-08-12, there is still no \"Web\" channel option here, and that's expected: Fridai isn't yet integrated with Hemi, so it doesn't receive Hemi-sourced (\"web\") orders. See Step 3's \"Web fulfilment allowed\" flag for where that readiness actually lives", "step8-numbering"),
        numberedStep("A Warehouse field appears next — confirmed live 2026-08-11, same as Create Purchase Order: always disabled, pre-filled from the top-bar warehouse selector. Switch the selector beforehand if you need a different warehouse", "step8-numbering"),
        numberedStep("Optionally fill in a Shipping Address section (Recipient Name auto-fills from Customer Name if left blank)", "step8-numbering"),
        numberedStep("Click \"Next\" to move to Order Items", "step8-numbering"),
        numberedStep("In the product field, type your product's name, SKU, or scan its barcode, then click it from the results — it will show the live available stock (e.g. “RaliPN1 (RaliP1) — 997”)", "step8-numbering"),
        numberedStep("Enter a quantity and click \"Add\"", "step8-numbering"),
        numberedStep("Click \"Create Order\" to finish — Fridai allocates the available stock immediately (confirmed by the app's own tour: \"Fridai allocates on create\"). There is no separate \"Save Draft\" button in the real app, despite what some documentation says", "step8-numbering"),
        note("you can also create a customer ahead of time via CRM & Suppliers > Customers > Add Customer, instead of filling in customer details inline as shown above — confirmed as a real option by the app's own onboarding tour (\"Create the customer who will receive the sales order\"), though we haven't walked that standalone flow ourselves yet."),

        h1("Step 9 — Fulfil the Order: Pick, Pack, Ship"),
        body("(Confirmed via the app's own onboarding tour; not yet walked step-by-step by us)", { italics: true }),
        body("Back on the Orders & Fulfillment page, each order row has its own action buttons — all confirmed present: View, Pick, Pack, Ship, Cancel. Each opens a dedicated page for that stage of fulfilment:"),

        h2("9a. Pick"),
        body("Picking Tasks — create or open a picking task, then scan/confirm units from allocated locations. (description confirmed via the app's own tour)"),

        h2("9b. Pack"),
        body("Packing Tasks — pack picked units into boxes. Labels are optional until a courier integration is configured — this confirms that skipping the shipping label works fine when no carrier is set up yet, rather than being a bug."),

        h2("9c. Ship"),
        body("Shipping Tasks — confirm shipment to release the order and record the outbound stock movement."),

        body("The Orders & Fulfillment table also shows a Packing column separate from the order's Status column, so you can track packing progress independently of the overall order status (confirmed live), plus (new, confirmed live 2026-08-11) a Warehouse column showing which warehouse each order is assigned to. For multiple orders at once, use the \"Bulk Pick,\" \"Bulk Pack,\" and \"Bulk Ship\" buttons at the top of the page (confirmed present) after selecting orders with their checkboxes."),

        h1("Step 10 — Split & Reallocate Orders  (NEW — Verified live 2026-08-13)"),
        body("With multiple warehouses, an order's stock isn't guaranteed to all be in one place. Opening any order's detail view (click \"View\" on an order row) now shows an \"ORDER OPS\" section with two actions for handling this."),

        h2("10a. Reallocate Order — move the whole order to a different warehouse"),
        body("Use this when the entire order should simply be fulfilled from a different warehouse — for example, the wrong warehouse was assigned, or the current one can't fulfil it at all. Confirmed live: the app's own description is \"Move [order] to a different warehouse. Existing reservations will be released and stock re-allocated at the destination.\""),
        numberedStep("Open the order and click \"Reallocate\" under ORDER OPS", "step10a-numbering"),
        numberedStep("Choose a Target warehouse from the dropdown", "step10a-numbering"),
        numberedStep("Click \"Reallocate\"", "step10a-numbering"),
        note("this is all-or-nothing — every unit on the order moves together. There's no way to move only part of an order this way; that's what Split (below) is for."),

        h2("10b. Split Order — move part of an order into a new sibling order"),
        body("Use this when only some of an order's units should be handled differently — for example, one warehouse only has partial stock and you want to ship what's available now while the rest comes from elsewhere. Confirmed live: the app's own description is \"Move pending or allocated units from [order] into a new sibling order.\" Internally, each unit of a line item is tracked as its own \"sub-line\" (visible under the order's \"Items & Sub-lines\" tab) — Split works at this per-unit level, not just per line item."),
        numberedStep("Open the order and click \"Split\" under ORDER OPS", "step10b-numbering"),
        numberedStep("Optionally choose a Target warehouse for the split-off units — leave it as \"Same as parent order\" if you just want a separate order in the same warehouse", "step10b-numbering"),
        numberedStep("Enter how many units of each line item to move", "step10b-numbering"),
        numberedStep("Click \"Split order\"", "step10b-numbering"),
        note("after splitting, the parent order and the new sibling order each proceed independently through Pick/Pack/Ship — they no longer need to ship together."),

        h1("Step 11 — Review Stock Movements"),
        body("(Confirmed via the app's own onboarding tour; not yet walked step-by-step by us)", { italics: true }),
        body("Expand \"Inventory Management\" and click \"Stock Movements.\" Every receive, pick, ship, and count writes a movement here — use this ledger to audit what changed and when, across every product and location."),

        h1("Step 12 — Explore the Rest"),
        body("(Reachable; not yet walked through)", { italics: true }),
        bullet("Inventory Management  →  Stock Transfers (move stock between warehouses — new in the Aug 10, 2026 release; see Step 3 for the warehouse concepts behind it)"),
        bullet("CRM & Suppliers  →  Customers (standalone customer creation — Suppliers is covered in Step 5)"),
        bullet("Settings  →  User Management, Integrations, Print stations (Warehouses is covered in Step 3)"),
        bullet("Returns  →  under Orders & Fulfillment, for processing customer returns"),
        body("These sections are all reachable from the sidebar but haven't been inspected in detail yet."),

        h1("What's Confirmed vs. Not Yet Verified"),
        body("This guide is built from the original Fridai documentation, a live inspection of the app, the app's own built-in onboarding tour (v1.4), a full run-through on a genuinely new, zero-data registration (v1.5), and — as of version 1.6 — a live regression and feature pass following the Aug 10, 2026 multi-warehouse release. These don't always agree — this table is your quick reference for what to trust as-is versus what to double-check as you go."),
        statusTable,

        h1("Quick Reference"),
        bullet("Ctrl+K (Cmd+K on Mac) — Command palette, confirmed working live (see Step 2)"),
        bullet("Tab — move between fields (documented, not yet confirmed live)"),
        bullet("Enter — submit forms / confirm scans (confirmed live in the Receiving flow — see Step 7d)"),
        bullet("Escape — close modals (documented, not yet confirmed live)"),

        h1("Getting Help"),
        body("Confirmed live: click \"Help\" in the top right corner for \"Help for this page,\" the \"Getting Started\" interactive tour, or the Command palette. Beyond the app itself, contact your administrator, or email support@fridai.com (this last channel not yet confirmed live)."),
        body("Since Fridai is still in test phase, your fastest path to an answer for anything not covered by the in-app Help is likely your administrator or the Fridai team directly."),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  const out = "G:\\My Drive\\Rali\\Fridai\\outputs\\Friday\\Friday_New_User_Getting_Started_Guide.docx";
  fs.writeFileSync(out, buf);
  console.log("Wrote", out);
});
