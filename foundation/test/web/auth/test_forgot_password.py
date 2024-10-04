# test_forgot_password_page.py
import pytest
from playwright.sync_api import Page, expect

from foundation.core.config import settings
from foundation.test.web.utils import BASE_URL

pytestmark = pytest.mark.playwright


def assert_forgot_password_page(page):
    # Verify the page URL and heading
    expect(page).to_have_url(f"{BASE_URL}/forgot-password")
    expect(page.get_by_role("heading", name="Forgot your password?")).to_be_visible()
    # Verify the email input and submit button
    email_input = page.get_by_label("Email address")
    expect(email_input).to_be_visible()
    submit_button = page.get_by_role("button", name="Continue")
    expect(submit_button).to_be_visible()
    return email_input, submit_button


def test_forgot_password_page_email_sent(page: Page):
    """
    Verify password recovery email is sent
    :param page: /forgot-password
    """
    # Navigate to the forgot password page
    page.goto(f"{BASE_URL}/forgot-password")

    email_input, submit_button = assert_forgot_password_page(page)

    # Fill out the form with an example email and submit
    email_input.fill(settings.SUPERUSER_EMAIL)
    submit_button.click()

    # Verify success message
    success_message = page.locator("#notification-message")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text(
        f"An email was sent to {settings.SUPERUSER_EMAIL}"
    )


def test_forgot_password_invalid_form(page: Page) -> None:
    page.goto(f"{BASE_URL}/forgot-password")

    email_input, submit_button = assert_forgot_password_page(page)

    # login with an invalid email
    email_input.fill("foo@c")
    submit_button.click()

    expect(page.get_by_text("Invalid email address.")).to_be_visible()

    # still on login page
    page.goto(f"{BASE_URL}/forgot-password")


def test_forgot_password_page_email_not_found(page: Page):
    """
    Verify password recovery email is sent
    :param page: /forgot-password
    """
    # Navigate to the forgot password page
    page.goto(f"{BASE_URL}/forgot-password")

    email_input, submit_button = assert_forgot_password_page(page)

    email = "not@email.com"
    # Fill out the form with an example email and submit
    email_input.fill(email)
    submit_button.click()

    # Verify success message after form submission (if applicable)
    success_message = page.locator("#notification-message")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text(f"The user {email} does not exist")
