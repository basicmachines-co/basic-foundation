import pytest
from foundation.core.users import RoleEnum
from playwright.sync_api import expect

from foundation.test.utils import random_email
from foundation.test.web.utils import (
    URL_USERS_PAGE,
    assert_user_detail_view,
    strong_password,
    assert_user_form,
)

pytestmark = pytest.mark.playwright


def test_admin_user_detail_view(create_user) -> None:
    page, user = create_user
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    assert_user_detail_view(page, full_name=user.full_name, email=user.email)


def test_admin_user_detail_edit(create_user) -> None:
    page, user = create_user
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    edit_button = page.get_by_text("Edit")
    edit_button.click()

    (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        role_input,
    ) = assert_user_form(page)

    expect(fullname_input).to_have_value(user.full_name)
    expect(email_input).to_have_value(user.email)
    expect(role_input).to_have_value("user")

    updated_full_name = "updated name"
    updated_email = random_email()

    # update the name and email values
    fullname_input.fill(updated_full_name)
    email_input.fill(updated_email)
    role_input.select_option(value="admin")

    # password values are not validated unless they have values

    save_button = page.get_by_role("button", name="Save")
    save_button.click()

    from foundation.core.users import StatusEnum

    assert_user_detail_view(
        page,
        full_name=updated_full_name,
        email=updated_email,
        role=RoleEnum.ADMIN,
        status=StatusEnum.ACTIVE,
    )


def test_admin_user_detail_edit_password(create_user) -> None:
    page, user = create_user
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    edit_button = page.get_by_text("Edit")
    edit_button.click()

    (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        role_input,
    ) = assert_user_form(page)

    updated_password = strong_password

    # update the name and email values
    password_input.fill(updated_password)
    password2_input.fill(updated_password)

    save_button = page.get_by_role("button", name="Save")
    save_button.click()

    assert_user_detail_view(page, full_name=user.full_name, email=user.email)


def test_admin_user_detail_edit_cancel(create_user) -> None:
    page, user = create_user

    user_page_url = f"{URL_USERS_PAGE}/{user.id}"
    expect(page).to_have_url(user_page_url)

    edit_button = page.get_by_text("Edit")
    edit_button.click()

    cancel_button = page.get_by_role("button", name="Cancel")
    cancel_button.click()

    # on user detail page
    expect(page).to_have_url(user_page_url)


def test_admin_user_detail_delete(create_user) -> None:
    page, user = create_user
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    edit_button = page.get_by_text("Edit")
    edit_button.click()

    delete_button = page.get_by_role("button", name="Delete")
    delete_button.click(timeout=10000)

    # assert modal confirmation
    page.wait_for_timeout(1)
    # expect(page.locator("#modal")).to_be_visible()
    expect(page.get_by_role("heading", name="Delete User")).to_be_visible()
    expect(page.get_by_text("Are you sure you want to")).to_be_visible()

    expect(page.locator("#modal").get_by_role("button", name="Cancel")).to_be_visible()
    page.get_by_role("button", name="Yes, Really").click()

    # on users page
    expect(page).to_have_url(URL_USERS_PAGE)
