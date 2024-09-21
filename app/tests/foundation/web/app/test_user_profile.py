from playwright.sync_api import Page, expect

from ..test_utils import (
    URL_REGISTER_PAGE, register_user, URL_PROFILE_PAGE, login,
)


def test_user_login(page: Page) -> None:
    # register a user so we can use their email
    page.goto(URL_REGISTER_PAGE)
    email, password = register_user(page)

    login(page, email, password)

    # assert we are on the user profile page
    expect(page).to_have_url(URL_PROFILE_PAGE)

    # nav
    expect(page.get_by_role("link", name="Dashboard")).to_be_visible(visible=False)
    expect(page.get_by_role("link", name="Users")).to_be_visible(visible=False)


def test_user_login_profile(page: Page) -> None:
    # register a user so we can use their email
    page.goto(URL_REGISTER_PAGE)
    email, password = register_user(page)
    full_name = f"User {email}"

    login(page, email, password)

    # assert we are on the profile page
    expect(page).to_have_url(URL_PROFILE_PAGE)

    # full name is displayed in heading
    expect(page.get_by_role("heading", name=full_name)).to_be_visible()

    # details
    expect(page.get_by_text("Full name")).to_be_visible()
    expect(page.locator("#full_name")).to_contain_text(full_name)

    expect(page.get_by_text("Email address")).to_be_visible()
    expect(page.locator("#email")).to_contain_text(email)

    # status values
    expect(page.get_by_text("Status")).to_be_visible()

    expect(page.get_by_text("Active", exact=True)).to_be_visible()
    expect(page.get_by_label("Active")).to_be_checked(checked=True)

    expect(page.get_by_text("Admin", exact=True)).to_be_visible()
    expect(page.get_by_label("Admin")).to_be_checked(checked=False)
