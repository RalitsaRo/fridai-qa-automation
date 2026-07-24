# `data/`

Static test data for the Fridai UI suite — JSON, CSV, or small Python modules
holding sample inputs.

Examples (once needed):
- `data/orders/sample_order.json` — canonical order payload used as a template.
- `data/users.json` — non-secret test user profiles (display name, role, etc.).

**Never** commit credentials or production data here — secrets go in `.env`
(gitignored), and production data should be anonymized before use.
