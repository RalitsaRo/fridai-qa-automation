# Friday (Fridai WMS) — QA Documentation

Two generated deliverables for the Fridai QA effort, both cross-checked against the
live app at each revision.

## Getting Started Guide

`Friday_New_User_Getting_Started_Guide.docx` is the user-facing onboarding guide for
Fridai (see the doc's own "Summary of Changes" table for the full revision history).

Currently at **v1.8** (2026-08-20) — covers the Aug 10, 2026 multi-warehouse release
(warehouse setup, the auto-filled Warehouse field, Split/Reallocate) and the Aug 19,
2026 order-queue visual rework (Work Queues, the PROGRESS column, minimized
next-action + "More actions" menu, the full partial-pick flow including the
leave-unpicked vs. cancel-the-rest distinction and multi-line picks, warehouse-gated
bulk actions, and Combine).

### Rebuilding

Generated from `build_friday_getting_started.js` (uses the `docx` npm package)
rather than hand-edited, so formatting stays consistent across revisions:

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
relevant step (register any new `numberedStep()` reference in the `numbering.config`
block up top, or docx-js throws), update `statusTable` if applicable, then rebuild
and visually verify (convert to PDF via LibreOffice headless + render page images
with PyMuPDF) before sharing.

## Test Case & Automation Coverage Tracker

`Friday_Test_Cases_and_Automation_Coverage.xlsx` lists every test case scenario
(automated and not-yet-automated) in one real Excel Table, with an "Automated?"
column and an "Automation Script" pointer to the real test file/function where one
exists. A "Summary" tab has live `COUNTIF`/`COUNTA` formulas for total/automated/
not-automated counts and a "% Automated" figure.

Currently at **48 test cases, ~52% automated** (2026-08-20) — includes coverage for
the Aug 19 order-queue rework: Work Queues, the PROGRESS column, next-action +
kebab menu, warehouse-gated bulk actions, all three partial-pick outcomes, and
Combine (precondition + end-to-end).

### Rebuilding

Generated from `build_test_case_workbook.py` (uses `openpyxl`) rather than
hand-edited:

```bash
python build_test_case_workbook.py
```

This writes the xlsx to the same `outputs\Friday\` Drive folder as the guide, then
**must be recalculated** before sharing — `openpyxl` writes formulas without cached
values, so the Summary tab would show blanks otherwise. Recalculate via a
convert-to-self round trip through LibreOffice headless:

```bash
soffice --headless --calc --convert-to xlsx --outdir <tmp_dir> <path_to_xlsx>
```

then copy the recalculated file back over the original and verify with `openpyxl`
(`data_only=True`) that the Summary numbers look right and no cell reads `#NAME?`/
`#REF!` before sharing. The blank pre-formatted rows already inside the Excel Table
(after the real data) are meant for new scenarios — fill them in directly rather
than adding unformatted rows below the table.
