"""Smoke / regression: Forgot-password entry point and reset-request UI.

Verified live 2026-09-18 — the login page now exposes a "Forgot password?"
link to `/forgot-password`. These tests assert the UI surface only; they do
NOT submit a real reset email (to avoid spamming the shared test account).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.forgot_password_page import ForgotPasswordPage
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_forgot_password_link_opens_reset_page(page: Page, base_url: str) -> None:
    login = LoginPage(page)
    login.goto()

    expect(login.forgot_password_link()).to_be_visible()
    login.open_forgot_password()

    forgot = ForgotPasswordPage(page)
    forgot.wait_for_loaded()
    expect(page).to_have_url(f"{base_url}/forgot-password")
    expect(forgot.email_input()).to_be_visible()
    expect(forgot.send_reset_link_button()).to_be_visible()
    expect(forgot.send_reset_link_button()).to_be_disabled()
    expect(forgot.back_to_sign_in_link()).to_be_visible()


@pytest.mark.regression
def test_forgot_password_send_button_enables_after_email(page: Page) -> None:
    forgot = ForgotPasswordPage(page)
    forgot.goto()
    forgot.wait_for_loaded()

    expect(forgot.send_reset_link_button()).to_be_disabled()
    forgot.fill_email("automation-reset-check@friday-automation-test.com")
    expect(forgot.send_reset_link_button()).to_be_enabled()


@pytest.mark.smoke
def test_forgot_password_back_to_sign_in(page: Page, base_url: str) -> None:
    forgot = ForgotPasswordPage(page)
    forgot.goto()
    forgot.wait_for_loaded()
    forgot.go_back_to_sign_in()

    login = LoginPage(page)
    expect(page).to_have_url(f"{base_url}/login")
    expect(login.forgot_password_link()).to_be_visible()
    expect(login.by_role("button", "Sign in")).to_be_visible()
