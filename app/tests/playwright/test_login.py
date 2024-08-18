import re

from playwright.sync_api import Page, expect

from foundation.core.config import settings

USERNAME = settings.SUPERUSER_EMAIL
PASSWORD = settings.SUPERUSER_PASSWORD

BASE_URL = "http://localhost:8000"
URL_LOGIN_PAGE = f"{BASE_URL}/login"
URL_DASHBOARD_PAGE = f"{BASE_URL}/dashboard"


def assert_login_page_content(page):
    # assert we are on the expected page
    expect(page).to_have_url(URL_LOGIN_PAGE)
    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Basic Machines: Login"))
    expect(page.get_by_role("heading", name="Log in to your account")).to_be_visible()


def test_login(page: Page):
    page.goto(URL_LOGIN_PAGE)

    assert_login_page_content(page)

    # login
    page.locator("#username").fill(USERNAME)
    page.locator("#password").fill(PASSWORD)

    # submit login
    page.locator("#login-button").click()

    # assert we are on dashboard page
    expect(page).to_have_url(URL_DASHBOARD_PAGE)
    expect(page).to_have_title(re.compile("Basic Machines: Dashboard"))


def test_login_failed_invalid_password(page: Page):
    page.goto(URL_LOGIN_PAGE)

    assert_login_page_content(page)

    # login
    page.locator("#username").fill(USERNAME)
    page.locator("#password").fill("invalid")

    # submit login
    page.locator("#login-button").click()

    expect(page.locator("#errors")).to_contain_text("Incorrect Username or Password")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Basic Machines: Login"))
