# Friday (Fridai WMS) — New User Getting Started Guide

`Friday_New_User_Getting_Started_Guide.docx` is the user-facing onboarding guide for
Fridai, cross-checked against the live app at each revision (see the doc's own
"Summary of Changes" table for the full history).

Currently at **v1.6** (2026-08-14) — covers the Aug 10, 2026 multi-warehouse release:
warehouse setup (Priority, "Web fulfilment allowed"), the new auto-filled Warehouse
field in Create Purchase Order / Create Order, and the Split / Reallocate order
operations.

## Rebuilding

The docx is generated from `build_friday_getting_started.js` (uses the `docx` npm
package) rather than hand-edited, so formatting stays consistent across revisions:

```bash
npm install docx
node build_friday_getting_started.js
```

This writes the docx to `G:\My Drive\Rali\Fridai\outputs\Friday\` (the Google-Drive-
synced deliverables folder) — update the `out` path at the bottom of the script if
that location ever changes. The copy in this `docs/Friday/` folder is the
version-controlled source of truth for the script; the Drive folder holds the
distributable file for whoever needs to open/print/share it.

To add a new revision: bump the version in `summaryTable`, add your changes in the
relevant step, update `statusTable` if applicable, then rebuild and visually verify
(convert to PDF via LibreOffice headless + render page images with PyMuPDF) before
sharing.
