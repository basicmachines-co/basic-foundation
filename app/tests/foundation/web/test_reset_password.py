import pytest
from playwright.sync_api import Page, expect

from .urls import BASE_URL

pytestmark = pytest.mark.playwright


def assert_reset_password_page(page):
    # Verify the page URL and heading
    expect(page).to_have_url(f"{BASE_URL}/reset-password")
    expect(page.get_by_role("heading", name="Reset your password")).to_be_visible()
    # Verify the email input and submit button
    email_input = page.get_by_label("Email address")
    expect(email_input).to_be_visible()
    submit_button = page.get_by_role("button", name="Continue")
    expect(submit_button).to_be_visible()
    return email_input, submit_button


def test_reset_password(page: Page):
    pass
