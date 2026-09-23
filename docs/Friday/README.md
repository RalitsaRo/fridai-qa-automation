# Friday (Fridai WMS) — QA Documentation

Two generated deliverables for the Fridai QA effort, both cross-checked against the
live app at each revision.

## Getting Started Guide

`Friday_New_User_Getting_Started_Guide.docx` is the user-facing onboarding guide for
Fridai (see the doc's own "Summary of Changes" table for the full revision history).

Currently at **v1.10** (2026-09-18) — doc/UI gap re-pass (Dashboard widget board,
Orders `/orders-list` + PROGRESS column, no Reports, role-gated Settings/Stock
Transfers) on top of v1.9 Forgot password and the Aug 10 / Aug 19 feature coverage.

### Rebuilding

Generated from `build_friday_getting_started.js` (uses the `docx` npm package)
rather than hand-edited, so formatting stays consistent across revisions:

```bash
cd docs/Friday
npm install docx
node build_friday_getting_started.js
```

This writes the docx to:

`C:\Rali\Automation\fridai-qa-automation-main\output\Friday\`

(relative: `output/Friday/` at the repo root). The scripts under `docs/Friday/`
are the version-controlled source of truth; that `output/Friday/` folder holds
the distributable files for open/print/share.

To add a new revision: bump the version in `summaryTable`, add your changes in the
relevant step (register any new `numberedStep()` reference in the `numbering.config`
block up top, or docx-js throws), update `statusTable` if applicable, then rebuild
and visually verify before sharing.

## Test Case & Automation Coverage Tracker

`Friday_Test_Cases_and_Automation_Coverage.xlsx` lists every test case scenario
(automated and not-yet-automated) in one real Excel Table, with an "Automated?"
column and an "Automation Script" pointer to the real test file/function where one
exists. A "Summary" tab has live `COUNTIF`/`COUNTA` formulas for total/automated/
not-automated counts and a "% Automated" figure.

Currently at **48 test cases** (2026-09-18) — FRIDAI-TC-004 flipped from
"Forgot Password absent" gap to automated smoke coverage of the real reset UI
(`tests/smoke/test_forgot_password.py`). Still includes Aug 19 order-queue
coverage from the prior revision.

### Rebuilding

Generated from `build_test_case_workbook.py` (uses `openpyxl`) rather than
hand-edited:

```bash
cd docs/Friday
python build_test_case_workbook.py
```

This writes the xlsx to the same `output\Friday\` folder as the guide, then
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
