import pytest
from playwright.sync_api import Page, expect

from foundation.core.security import generate_password_reset_token
from foundation.test.web.utils import BASE_URL

pytestmark = pytest.mark.playwright


def assert_reset_password_page(page, token):
    # Verify the page URL and heading
    expect(page).to_have_url(f"{BASE_URL}/reset-password?token={token}")
    expect(page.get_by_role("heading", name="Reset your password")).to_be_visible()

    # Verify the pasword inputs and submit button
    new_password_input = page.get_by_label("New Password")
    expect(new_password_input).to_be_visible()

    repeat_password_input = page.get_by_label("Repeat Password")
    expect(repeat_password_input).to_be_visible()

    submit_button = page.get_by_role("button", name="Reset")
    expect(submit_button).to_be_visible()
    return new_password_input, repeat_password_input, submit_button


def test_reset_password(register_user):
    page, user = register_user

    password_reset_token = generate_password_reset_token(email=user.email)
    page.goto(f"{BASE_URL}/reset-password?token={password_reset_token}")

    (
        new_password_input,
        repeat_password_input,
        submit_button,
    ) = assert_reset_password_page(page, password_reset_token)

    new_password = "u$tsUwfy#i9tKm"
    new_password_input.fill(new_password)
    repeat_password_input.fill(new_password)
    submit_button.click()

    # verify success message
    success_message = page.locator("#success")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Your password has been updated!")


def test_reset_password_invalid_form(register_user) -> None:
    page, user = register_user

    password_reset_token = generate_password_reset_token(email=user.email)
    page.goto(f"{BASE_URL}/reset-password?token={password_reset_token}")

    (
        new_password_input,
        repeat_password_input,
        submit_button,
    ) = assert_reset_password_page(page, password_reset_token)

    # login with an invalid email
    new_password_input.fill("foo")
    repeat_password_input.fill("foo")
    submit_button.click()

    expect(page.locator("#password-error")).to_be_visible()

    expect(page.locator("#password_2-error")).to_be_visible()

    # still on page
    page.goto(f"{BASE_URL}/reset-password?token={password_reset_token}")


def test_reset_password_invalid_token(register_user):
    page, user = register_user

    password_reset_token = "not-a-real-token"
    page.goto(f"{BASE_URL}/reset-password?token={password_reset_token}")

    # verify error message is displayed
    error_message = page.locator("#error")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("Invalid token")


def test_reset_password_user_not_found(page: Page):
    email = "some-fake@email.com"
    password_reset_token = generate_password_reset_token(email=email)
    page.goto(f"{BASE_URL}/reset-password?token={password_reset_token}")

    (
        new_password_input,
        repeat_password_input,
        submit_button,
    ) = assert_reset_password_page(page, password_reset_token)

    password = "u$tsUwfy#i9tKm"
    new_password_input.fill(password)
    repeat_password_input.fill(password)
    submit_button.click()

    # verify error message is displayed
    error_message = page.locator("#error")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text(f"The user {email} does not exist")
