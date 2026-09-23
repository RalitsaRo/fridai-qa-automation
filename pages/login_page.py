"""Page Object for the Fridai login screen.

Locators VERIFIED 2026-07-16 against the live app (https://app.fridai.pro),
re-checked 2026-09-18 for the Forgot-password entry point:
- Email input: <input type="email" id="email" placeholder="Email address">
- Password input: <input type="password" id="password" placeholder="Password">
- Submit button: <button type="submit">Sign in</button>
- "Forgot password?" link → `/forgot-password` (added ~2026-09; confirmed live)
- No CAPTCHA / bot-protection observed.
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

    def forgot_password_link(self):
        """The self-service password-reset entry point on the login form."""
        return self.by_role("link", "Forgot password?")

    def open_forgot_password(self) -> None:
        """Click \"Forgot password?\" and leave the caller on `/forgot-password`."""
        self.forgot_password_link().click()
