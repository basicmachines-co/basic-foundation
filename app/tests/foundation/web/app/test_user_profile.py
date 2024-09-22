import pytest
from playwright.sync_api import expect

from web_test_utils import (
    URL_PROFILE_PAGE, assert_user_detail_view,
)
from ..conftest import login

pytestmark = pytest.mark.playwright


def test_user_login(register_user) -> None:
    page, user = register_user
    login(page, user.email, user.password)

    # assert we are on the user profile page
    expect(page).to_have_url(URL_PROFILE_PAGE)

    # nav should not contain the admin only links
    expect(page.get_by_role("link", name="Dashboard")).to_be_visible(visible=False)
    expect(page.get_by_role("link", name="Users")).to_be_visible(visible=False)


def test_user_profile(register_user) -> None:
    page, user = register_user
    login(page, user.email, user.password)

    # assert we are on the profile page
    expect(page).to_have_url(URL_PROFILE_PAGE)

    assert_user_detail_view(page, email=user.email, full_name=user.full_name, active=True, admin=False)
