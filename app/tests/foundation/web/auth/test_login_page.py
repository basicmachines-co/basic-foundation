from typing import Any

import pytest
from playwright.sync_api import Page, expect

from foundation.core.config import settings
from web_test_utils import (
    URL_LOGIN_PAGE,
    URL_DASHBOARD_PAGE,
    URL_REGISTER_PAGE,
    URL_FORGOT_PASSWORD_PAGE,
)

USERNAME = settings.SUPERUSER_EMAIL
PASSWORD = settings.SUPERUSER_PASSWORD

pytestmark = pytest.mark.playwright


def assert_login_page(page: Page) -> dict[str, Any]:
    expect(page).to_have_url(URL_LOGIN_PAGE)
    expect(page.get_by_role("heading", name="Log in", exact=True)).to_be_visible()

    username_input = page.get_by_label("Email address")
    expect(username_input).to_be_visible()

    password_input = page.get_by_label("Password")
    expect(password_input).to_be_visible()

    forgot_password_link = page.get_by_role("link", name="Forgot password?")
    expect(forgot_password_link).to_be_visible()

    login_button = page.get_by_role("button", name="Log in")
    expect(login_button).to_be_visible()

    register_link = page.get_by_role("link", name="Register")
    expect(register_link).to_be_visible()

    return locals()


def test_login_success_admin(page: Page) -> None:
    page.goto(URL_LOGIN_PAGE)

    login_page = assert_login_page(page)

    # login
    login_page["username_input"].fill(USERNAME)
    login_page["password_input"].fill(PASSWORD)

    # submit login
    login_page["login_button"].click()

    # assert we are on dashboard page
    expect(page).to_have_url(URL_DASHBOARD_PAGE)


def test_login_failed_invalid_password(page: Page) -> None:
    page.goto(URL_LOGIN_PAGE)

    login_page = assert_login_page(page)

    # login
    login_page["username_input"].fill(USERNAME)
    login_page["password_input"].fill("invalid-password")

    # submit login
    login_page["login_button"].click()

    expect(page.locator("#notification-message")).to_contain_text(
        "Incorrect email or password"
    )

    # still on login page
    expect(page).to_have_url(URL_LOGIN_PAGE)


def test_login_register_link(page: Page):
    page.goto(URL_LOGIN_PAGE)

    login_page = assert_login_page(page)

    login_page["register_link"].click()

    # go to register page
    expect(page).to_have_url(URL_REGISTER_PAGE)


def test_login_forgot_password_link(page: Page):
    page.goto(URL_LOGIN_PAGE)

    login_page = assert_login_page(page)

    login_page["forgot_password_link"].click()

    # go to register page
    expect(page).to_have_url(URL_FORGOT_PASSWORD_PAGE)
