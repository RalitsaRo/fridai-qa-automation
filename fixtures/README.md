# `fixtures/`

Shared setup / teardown helpers that don't fit cleanly inside `tests/conftest.py`.

Currently empty — there are no confirmed backend access points for Fridai yet
(no DB connection, no SSH, no seeding API). Once those exist, mirror the
pattern in `../automation_ui/fixtures/` (`db.py`, `ssh.py`) here, and wire
them into `tests/conftest.py` as session-scoped fixtures.

Keep raw `data-testid` selectors out of this folder — selectors belong inside
Page Objects under `pages/`.
