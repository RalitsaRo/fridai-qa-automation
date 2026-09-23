"""Page Object for the Fridai Forgot-password screen (`/forgot-password`).

VERIFIED live 2026-09-18 against https://app.fridai.pro:
- H2 "Forgot password"
- Helper copy: "Enter your account email and we'll send a reset link if it exists."
- Email input: placeholder "Email address" (required)
- Primary button: "Send reset link" (disabled until the email field has a value)
- "Back to sign in" link → `/login`

This Page Object covers the UI surface only. Submitting a real reset email is
left to an explicit test that opts in — do not fire reset emails from shared
fixtures by default.
"""

from __future__ import annotations

from pages.base_page import BasePage


class ForgotPasswordPage(BasePage):
    """The self-service password-reset request screen."""

    path = "/forgot-password"

    def wait_for_loaded(self, timeout: int = 10_000) -> None:
        self.by_role("heading", "Forgot password").wait_for(
            state="visible", timeout=timeout
        )

    def email_input(self):
        return self.by_placeholder("Email address")

    def send_reset_link_button(self):
        return self.by_role("button", "Send reset link")

    def back_to_sign_in_link(self):
        return self.by_role("link", "Back to sign in")

    def fill_email(self, email: str) -> None:
        self.email_input().fill(email)

    def submit_reset_request(self) -> None:
        """Click \"Send reset link\". Caller must have filled a non-empty email."""
        self.send_reset_link_button().click()

    def go_back_to_sign_in(self) -> None:
        self.back_to_sign_in_link().click()
