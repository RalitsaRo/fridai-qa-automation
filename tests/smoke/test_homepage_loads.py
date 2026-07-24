"""Smoke test: confirm the Fridai test environment is reachable.

This is the simplest possible end-to-end check. It does NOT log in, click,
or inspect specific UI content. It only proves:

  1. Playwright can launch a browser on this machine.
  2. The .env file is being loaded (BASE_URL is picked up).
  3. The configured Fridai environment is reachable from here.
  4. The pytest discovery + fixture wiring all work.

Requires a real BASE_URL in `.env` — there is no Fridai test instance
confirmed yet, so this test will fail with a clear RuntimeError from the
`base_url` fixture until one is configured.

How to run:
    Headed (browser window visible):  poetry run pytest tests/smoke -m smoke --headed
    Headless (no window, faster):     poetry run pytest tests/smoke -m smoke
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


@pytest.mark.smoke
def test_homepage_loads(page: Page, base_url: str) -> None:
    """Navigate to BASE_URL and confirm the page came back successfully."""
    response = page.goto(base_url)

    assert response is not None, "page.goto() returned no response"
    assert response.ok, (
        f"Unexpected HTTP {response.status} when loading {base_url}"
    )

    title = page.title()
    assert title, "Page returned successfully but has no <title> tag"

    print(f"\n  Loaded page title: {title!r}")
