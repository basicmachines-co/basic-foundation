import re

from playwright.sync_api import Page, expect

USERNAME = "test@test.com"
PASSWORD = "test"


def test_login(page: Page):
    page.goto("http://localhost:8000/login")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Basic Machines: Login"))

    expect(page.get_by_role("heading", name="Sign in to your account")).to_be_visible()

    # login
    page.locator("#username").fill(USERNAME)
    page.locator("#password").fill(PASSWORD)

    # Navigate implicitly by clicking a link.
    page.get_by_role("button", name="Sign in").click()

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Basic Machines: Dashboard"))


def test_login_failed_invalid_password(page: Page):
    page.goto("http://localhost:8000/login")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Basic Machines: Login"))

    expect(page.get_by_role("heading", name="Sign in to your account")).to_be_visible()

    # login
    page.locator("#username").fill(USERNAME)
    page.locator("#password").fill("invalid")

    # Navigate implicitly by clicking a link.
    page.get_by_role("button", name="Sign in").click()

    page.locator("#errors")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Basic Machines: Dashboard"))
