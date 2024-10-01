import pytest
from foundation.core.users import StatusEnum, RoleEnum
from playwright.sync_api import Page, expect

from foundation.core.config import settings
from foundation.test.utils import random_email, random_lower_string
from foundation.test.web.utils import (
    URL_USERS_PAGE,
    assert_users_page,
    admin_email,
    admin_full_name,
    assert_user_form,
    User,
    strong_password,
)

pytestmark = pytest.mark.playwright


def assert_user_edit_modal(page, user):
    expect(page.get_by_role("heading", name="Edit User")).to_be_visible()

    (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        role_input,
    ) = assert_user_form(page)

    expect(fullname_input).to_have_value(user.full_name)
    expect(email_input).to_have_value(user.email)
    expect(role_input).to_have_value(user.role.value)

    # status is only on edit form
    page.get_by_text("Status", exact=True)
    status_input = page.get_by_label("Status")
    expect(status_input).to_have_value(user.status.value)

    return (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        role_input,
        status_input,
    )


def edit_user_in_modal(page, user):
    expect(page).to_have_url(f"{URL_USERS_PAGE}")
    # click the edit button on the row
    row_button = page.get_by_test_id(f"edit-delete-button-{user.email}")
    row_button.click(timeout=10000)

    # click edit link in menu
    menu_edit_link = page.get_by_role("link", name="Edit")
    menu_edit_link.click(timeout=10000)


def test_admin_user_list(do_admin_login: Page) -> None:
    page = do_admin_login

    page.goto(URL_USERS_PAGE)
    assert_users_page(page)

    # verify user in user list
    expect(page.get_by_role("cell", name=admin_full_name)).to_be_visible()
    expect(page.get_by_role("cell", name=admin_email, exact=True)).to_be_visible()

    status = page.get_by_test_id(f"status-{admin_email}")
    expect(status).to_be_visible()
    expect(status).to_contain_text(StatusEnum.ACTIVE.capitalize())

    role = page.get_by_test_id(f"role-{admin_email}")
    expect(role).to_be_visible()
    expect(role).to_contain_text(RoleEnum.ADMIN.capitalize())

    admin_user = User(
        full_name=admin_full_name,
        email=admin_email,
        password=settings.SUPERUSER_PASSWORD,
        status=StatusEnum.ACTIVE,
        role=RoleEnum.ADMIN,
    )
    edit_user_in_modal(page, admin_user)

    assert_user_edit_modal(page, admin_user)


def test_admin_user_modal_edit(create_user) -> None:
    page, user = create_user

    page.goto(URL_USERS_PAGE)
    assert_users_page(page)
    edit_user_in_modal(page, user)

    (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        role_input,
        status_input,
    ) = assert_user_edit_modal(page, user)

    updated_full_name = random_lower_string()
    updated_email = random_email()

    # update the name and email values
    fullname_input.fill(updated_full_name)
    email_input.fill(updated_email)
    role_input.select_option(value=RoleEnum.USER)
    status_input.select_option(value=StatusEnum.INACTIVE)

    # password values are not validated unless they have values

    save_button = page.get_by_role("button", name="Save")
    save_button.click()

    # verify user in user list
    expect(page.get_by_role("cell", name=updated_full_name)).to_be_visible()
    expect(page.get_by_role("cell", name=updated_email, exact=True)).to_be_visible()


def test_admin_user_modal_edit_password(create_user) -> None:
    page, user = create_user

    page.goto(URL_USERS_PAGE)
    assert_users_page(page)
    edit_user_in_modal(page, user)

    (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        admin_checkbox,
        active_checkbox,
    ) = assert_user_edit_modal(page, user)

    updated_password = strong_password

    # update the name and email values
    password_input.fill(updated_password)
    password2_input.fill(updated_password)

    save_button = page.get_by_role("button", name="Save")
    save_button.click()

    # verify user in user list
    expect(page.get_by_role("cell", name=user.full_name)).to_be_visible()
    expect(page.get_by_role("cell", name=user.email, exact=True)).to_be_visible()


def test_admin_user_modal_edit_cancel(create_user) -> None:
    page, user = create_user

    page.goto(URL_USERS_PAGE)
    assert_users_page(page)
    edit_user_in_modal(page, user)

    assert_user_edit_modal(page, user)

    cancel_button = page.get_by_role("button", name="Cancel")
    cancel_button.click()

    # verify user in user list
    expect(page.get_by_role("cell", name=user.full_name)).to_be_visible()
    expect(page.get_by_role("cell", name=user.email, exact=True)).to_be_visible()


def test_admin_user_modal_edit_delete(create_user) -> None:
    page, user = create_user

    page.goto(URL_USERS_PAGE)
    assert_users_page(page)

    # click the edit/delete button on the row
    row_button = page.get_by_test_id(f"edit-delete-button-{user.email}")
    row_button.click(timeout=10000)

    # click edit link in menu
    menu_delete_link = page.get_by_role("link", name="Delete")
    menu_delete_link.click(timeout=10000)

    # assert modal confirmation
    expect(page.get_by_role("heading", name="Delete user")).to_be_visible()
    expect(page.get_by_text("Are you sure you want to")).to_be_visible()

    expect(
        page.locator("#modal-content").get_by_role("button", name="Cancel")
    ).to_be_visible()
    page.get_by_role("button", name="Yes, Really").click()

    # verify user in user list
    expect(page.get_by_role("cell", name=user.full_name)).to_be_visible(visible=False)
    expect(page.get_by_role("cell", name=user.email, exact=True)).to_be_visible(
        visible=False
    )
