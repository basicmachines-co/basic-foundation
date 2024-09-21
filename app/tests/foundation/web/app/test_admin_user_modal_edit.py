import pytest
from playwright.sync_api import Page, expect

from ..web_test_utils import (
    admin_login, URL_USERS_PAGE, assert_users_page,
    admin_email, admin_full_name
)

pytestmark = pytest.mark.playwright


def test_admin_user_list(page: Page) -> None:
    admin_login(page)

    page.goto(URL_USERS_PAGE)
    assert_users_page(page)

    # verify user in user list
    expect(page.get_by_role("cell", name=admin_full_name)).to_be_visible()
    expect(page.get_by_role("cell", name=admin_email)).to_be_visible()

    is_active = page.get_by_test_id(f"is-active-{admin_email}")
    expect(is_active).to_be_visible()
    expect(is_active).to_be_checked(checked=True)

    is_superuser = page.get_by_test_id(f"is-superuser-{admin_email}")
    expect(is_superuser).to_be_visible()
    expect(is_superuser).to_be_checked(checked=True)

    # click the edit button on the row
    row_button = page.get_by_test_id(f"edit-delete-button-{admin_email}")
    row_button.click()

    # click edit link in menu
    menu_edit_link = page.get_by_role("link", name="Edit")
    menu_edit_link.click()

    # modal title
    expect(page.get_by_role("heading", name="Edit User")).to_be_visible()
    expect(page.get_by_label("Full name")).to_have_value(admin_full_name)
