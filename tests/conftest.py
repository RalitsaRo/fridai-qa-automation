"""Shared pytest fixtures for the Fridai UI automation suite.

Simpler than the sister `../automation_ui/` (Hemi) conftest: no DB/SSH
fixtures here, because we don't have confirmed backend access for Fridai
yet. Add those back (mirroring `../automation_ui/fixtures/db.py` and
`ssh.py`) once that infra exists.

Configuration approach (Python Playwright):
- `pytest.ini` carries markers, default browser, and artifact retention rules.
- This `conftest.py` carries fixtures: env loading, base URL wiring, and
  a real (non-CAPTCHA) login fixture via `LoginPage`.
- Per-test browser context comes from the `pytest-playwright` plugin
  (`page`, `context`, `browser` fixtures are provided automatically).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Make the repo root importable so tests can do `from pages import ...`
# without packaging gymnastics.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Load .env at conftest-import time so EVERY fixture sees the env vars.
_ENV_FILE = _REPO_ROOT / ".env"
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)

from pages.login_page import LoginPage  # noqa: E402


# ---- Env loading -----------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def _load_env() -> None:
    """Load environment variables from a local `.env` file if it exists.

    `.env` is gitignored. CI should inject real env vars directly.
    """
    repo_root = Path(__file__).resolve().parents[1]
    env_file = repo_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)


# ---- Configuration --------------------------------------------------------


@pytest.fixture(scope="session")
def base_url() -> str:
    url = os.getenv("BASE_URL")
    if not url:
        raise RuntimeError(
            "BASE_URL is not set. Copy .env.example to .env and fill in "
            "the real Fridai test-environment URL once one exists."
        )
    return url.rstrip("/")


@pytest.fixture(scope="session")
def test_credentials() -> tuple[str, str]:
    user = os.getenv("FRIDAI_TEST_USER")
    password = os.getenv("FRIDAI_TEST_PASSWORD")
    if not user or not password:
        raise RuntimeError(
            "FRIDAI_TEST_USER and FRIDAI_TEST_PASSWORD must be set in the "
            "environment (copy .env.example to .env)."
        )
    return user, password


# ---- Playwright context overrides -----------------------------------------


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, base_url):  # noqa: ANN001
    """Inject base_url + viewport into every browser context."""
    return {
        **browser_context_args,
        "base_url": base_url,
        "viewport": {"width": 1440, "height": 900},
    }


# ---- Auth -------------------------------------------------------------------


@pytest.fixture
def authenticated_page(page, test_credentials):  # noqa: ANN001
    """Returns a `page` that has been logged into Fridai via a real login flow.

    Unlike Hemi's `authenticated_page` (which loads a pre-captured storage
    state to route around hCaptcha), this performs an actual login through
    `LoginPage` — the Fridai docs don't mention any bot-protection on login.

    If that assumption turns out to be wrong once we can see the real app,
    switch this fixture to the saved-auth-state pattern used in
    `../automation_ui/tests/conftest.py`.

    Observed live 2026-08-14: running the FULL suite in one `pytest`
    invocation (~12 tests, each doing a fresh login here) occasionally
    produces a handful of "Dashboard heading" timeouts clustered at the
    END of the run — re-running those same tests individually or in a
    smaller batch immediately afterward passes cleanly every time. This
    looks like a login rate-limit/throttle on the shared live instance
    after ~9-10 logins within a couple of minutes, not a bug in the tests
    or Page Objects. If this becomes a recurring problem, switching to
    the saved-auth-state pattern mentioned above (one login, reused via
    storage state) would sidestep it entirely — tracked as a follow-up,
    not done here.

    IMPORTANT: waits for the post-login redirect to the Dashboard (heading
    "Dashboard" visible) before returning. Without this, a test that
    immediately hard-navigates elsewhere (e.g. `OrdersPage.goto()`) can race
    the login redirect — confirmed 2026-07-16: direct `goto()` right after
    `login()` intermittently lands on an unauthenticated/blank state, while
    the same navigation succeeds once the caller has waited for Dashboard
    to render first.
    """
    user, password = test_credentials
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(user, password)
    page.get_by_role("heading", name="Dashboard").wait_for(state="visible", timeout=10_000)
    return page
