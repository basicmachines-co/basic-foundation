import pytest
from foundation.core.users import StatusEnum, RoleEnum
from playwright.sync_api import expect

from foundation.web.web_test_utils import (
    URL_PROFILE_PAGE,
    assert_user_detail_view,
    BASE_URL,
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

    assert_user_detail_view(
        page,
        email=user.email,
        full_name=user.full_name,
        status=StatusEnum.ACTIVE,
        role=RoleEnum.USER,
    )


# def test_403(register_user) -> None:
#     page, user = register_user
#     login(page, user.email, user.password)
#
#     page.goto(f"{BASE_URL}/dashboard")
#
#     expect(page.get_by_text("403")).to_be_visible()
#     expect(page.get_by_role("heading",name="Forbidden")).to_be_visible()


def test_404(page):
    print(f"{BASE_URL}/some-page-does-not-exist")
    page.goto(f"{BASE_URL}/some-page-does-not-exist")

    expect(page.get_by_text("404")).to_be_visible()
    expect(page.get_by_role("heading", name="Page not found")).to_be_visible()
