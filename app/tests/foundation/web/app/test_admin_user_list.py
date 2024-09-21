from playwright.sync_api import Page, expect

from ..test_utils import (
    admin_login, URL_USERS_PAGE,
)


def test_admin_user_list(page: Page) -> None:
    admin_login(page)

    page.goto(URL_USERS_PAGE)

    # assert we are on the users page
    expect(page).to_have_url(URL_USERS_PAGE)

    # heading
    expect(page.get_by_role("heading", name="Users")).to_be_visible()

    # user list
