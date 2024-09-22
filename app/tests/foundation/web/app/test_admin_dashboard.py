import pytest
from playwright.sync_api import Page, expect

from web_test_utils import (
    URL_DASHBOARD_PAGE, URL_PROFILE_PAGE, URL_LOGIN_PAGE,
)

pytestmark = pytest.mark.playwright


def test_admin_login_dashboard(do_admin_login: Page) -> None:
    page = do_admin_login

    # assert we are on the dashboard page
    expect(page).to_have_url(URL_DASHBOARD_PAGE)

    # nav
    expect(page.get_by_role("link", name="Dashboard")).to_be_visible()
    expect(page.get_by_role("link", name="Users")).to_be_visible()

    # heading
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

    # stats
    expect(page.get_by_text("Total Users")).to_be_visible()

    user_count_stat = page.locator("#user-count")
    expect(user_count_stat).to_be_visible()
    expect(user_count_stat).not_to_be_empty()

    active_user_count_stat = page.locator("#active-user-count")
    expect(active_user_count_stat).to_be_visible()
    expect(active_user_count_stat).not_to_be_empty()

    admin_user_count_stat = page.locator("#admin-user-count")
    expect(admin_user_count_stat).to_be_visible()
    expect(admin_user_count_stat).not_to_be_empty()


def test_admin_profile(do_admin_login: Page) -> None:
    page = do_admin_login

    # assert we are on the dashboard page
    expect(page).to_have_url(URL_DASHBOARD_PAGE)

    # click the profile menu
    profile_menu_button = page.locator("#profile-menu")
    profile_menu_button.click()

    # click the profile button
    profile_menu_link = page.get_by_role("link", name="Your Profile")
    profile_menu_link.click()

    # go to register page
    expect(page).to_have_url(URL_PROFILE_PAGE)


def test_admin_logout(do_admin_login: Page) -> None:
    page = do_admin_login

    # assert we are on the dashboard page
    expect(page).to_have_url(URL_DASHBOARD_PAGE)

    # click the profile menu
    profile_menu_button = page.locator("#profile-menu")
    profile_menu_button.click()

    # click the log out button
    profile_menu_link = page.get_by_role("link", name="Log out")
    profile_menu_link.click()

    # go to register page
    expect(page).to_have_url(URL_LOGIN_PAGE)
