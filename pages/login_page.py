"""Page Object for the Fridai login screen.

Locators VERIFIED 2026-07-16 against the live app (https://app.fridai.pro):
- Email input: <input type="email" id="email" placeholder="Email address">
- Password input: <input type="password" id="password" placeholder="Password">
- Submit button: <button type="submit">Sign in</button>
- No CAPTCHA / bot-protection observed.
- No "Forgot Password" link found on the login page at all — the flow
  described in docs/getting-started.md § "Forgot Password" does not appear
  to exist in the current app. Flagged in MEMORY.md as a doc-vs-reality gap;
  `start_forgot_password()` below is commented out until/unless that link
  is confirmed to exist somewhere (e.g. behind a different entry point).
"""

from __future__ import annotations

from pages.base_page import BasePage


class LoginPage(BasePage):
    """The Fridai login screen."""

    path = "/login"

    def login(self, email: str, password: str) -> None:
        """Fill credentials and submit the login form."""
        self.by_placeholder("Email address").fill(email)
        self.by_placeholder("Password").fill(password)
        self.by_role("button", "Sign in").click()

    # def start_forgot_password(self, email: str) -> None:
    #     """NOT IMPLEMENTED — no "Forgot Password" link was found on the
    #     real login page (verified 2026-07-16). docs/getting-started.md
    #     describes this flow but it doesn't appear to be built, or lives
    #     somewhere else in the app. Re-enable once located."""
    #     raise NotImplementedError
