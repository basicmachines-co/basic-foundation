from typing import Any

import pytest
from playwright.sync_api import Page, expect

from utils import random_email
from ..web_test_utils import URL_REGISTER_PAGE

pytestmark = pytest.mark.playwright


def assert_register_page(page: Page) -> dict[str, Any]:
    expect(page).to_have_url(URL_REGISTER_PAGE)
    expect(page.get_by_role("heading", name="Register", exact=True)).to_be_visible()

    fullname_input = page.get_by_label("Full Name")
    expect(fullname_input).to_be_visible()

    email_input = page.get_by_label("Email address")
    expect(email_input).to_be_visible()

    password_input = page.get_by_label("Password", exact=True)
    expect(password_input).to_be_visible()

    password2_input = page.get_by_label("Repeat Password")
    expect(password2_input).to_be_visible()

    register_button = page.get_by_role("button", name="Register")
    expect(register_button).to_be_visible()

    login_link = page.get_by_role("link", name="Login")
    expect(login_link).to_be_visible()

    return locals()


def test_register_page(page: Page) -> None:
    page.goto(URL_REGISTER_PAGE)
    assert_register_page(page)


def test_register_full_name_required(page: Page) -> None:
    page.goto(URL_REGISTER_PAGE)

    register_page = assert_register_page(page)
    register_page["register_button"].click()

    expect(page).to_have_url(URL_REGISTER_PAGE)
    expect(register_page["fullname_input"]).to_be_empty()


def test_register_email_required(page: Page) -> None:
    page.goto(URL_REGISTER_PAGE)

    register_page = assert_register_page(page)

    register_page["fullname_input"].fill(f"User {random_email()}")
    register_page["register_button"].click()

    expect(page).to_have_url(URL_REGISTER_PAGE)
    expect(register_page["email_input"]).to_be_empty()


def test_register_email_valid(page: Page) -> None:
    page.goto(URL_REGISTER_PAGE)

    register_page = assert_register_page(page)

    full_name = f"User {random_email()}"
    email = "not an email"

    register_page["fullname_input"].fill(full_name)
    register_page["email_input"].fill(email)
    register_page["register_button"].click()

    expect(page).to_have_url(URL_REGISTER_PAGE)

    # assert form values
    expect(register_page["fullname_input"]).to_have_value(full_name)
    expect(register_page["email_input"]).to_have_value(email)


def test_register_password_valid(page: Page) -> None:
    page.goto(URL_REGISTER_PAGE)

    register_page = assert_register_page(page)

    email = random_email()
    full_name = f"User {email}"

    register_page["fullname_input"].fill(full_name)
    register_page["email_input"].fill(email)
    register_page["password_input"].fill("weak password")
    register_page["register_button"].click()

    expect(page).to_have_url(URL_REGISTER_PAGE)

    # assert form values
    expect(register_page["fullname_input"]).to_have_value(full_name)
    expect(register_page["email_input"]).to_have_value(email)
    expect(register_page["password_input"]).to_have_value("")


def test_register_passwords_must_match(page: Page) -> None:
    page.goto(URL_REGISTER_PAGE)

    # Ensure the registration page loads correctly
    register_page = assert_register_page(page)

    email = random_email()
    password = "qbFa&WyQio#85L"
    mismatched_password = f"{password}_2"

    # Fill in the registration form
    register_page["fullname_input"].fill(f"User {email}")
    register_page["email_input"].fill(email)
    register_page["password_input"].fill(password)
    register_page["password2_input"].fill(mismatched_password)

    # Submit the form
    register_page["register_button"].click()

    # Expect an error message that passwords do not match
    expect(page.locator("#password-error")).to_have_text("Passwords do not match.")
