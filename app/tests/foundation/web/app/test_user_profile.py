import pytest
from playwright.sync_api import Page, expect

from ..web_test_utils import (
    URL_REGISTER_PAGE, register_user, URL_PROFILE_PAGE, login, assert_user_detail_view,
)

pytestmark = pytest.mark.playwright


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
    assert_user_detail_view(page, email=email, full_name=full_name, active=True, admin=False)
