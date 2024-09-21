import uuid
from dataclasses import dataclass

import pytest
from playwright.sync_api import Page, expect, Locator

from foundation.core.config import settings
from utils import random_email
from ..web_test_utils import (
    admin_login, URL_USERS_PAGE, URL_USERS_CREATE_PAGE, assert_user_detail_view, strong_password,
)

email = settings.SUPERUSER_EMAIL
full_name = settings.SUPERUSER_NAME

pytestmark = pytest.mark.playwright


def assert_users_page(page) -> Locator:
    # assert we are on the users page
    expect(page).to_have_url(URL_USERS_PAGE)
    # heading
    expect(page.get_by_role("heading", name="Users")).to_be_visible()

    create_user_button = page.get_by_role("link", name="Create user")
    expect(create_user_button).to_be_visible()

    return create_user_button


def assert_create_user_page(page):
    expect(page).to_have_url(URL_USERS_CREATE_PAGE)

    fullname_input, email_input, password_input, password2_input, admin_checkbox = assert_user_form(page)

    cancel_button = page.get_by_role("button", name="Cancel")
    expect(cancel_button).to_be_visible()

    save_button = page.get_by_role("button", name="Save")
    expect(save_button).to_be_visible()

    return fullname_input, email_input, password_input, password2_input, admin_checkbox, cancel_button, save_button


def assert_user_form(page):
    fullname = page.get_by_text("Full Name")
    fullname_input = page.get_by_label("Full Name")
    expect(fullname).to_be_visible()
    expect(fullname_input).to_be_visible()
    email = page.get_by_text("Email address")
    email_input = page.get_by_label("Email address")
    expect(email).to_be_visible()
    expect(email_input).to_be_visible()
    password = page.get_by_text("Password", exact=True)
    password_input = page.get_by_label("Password", exact=True)
    expect(password).to_be_visible()
    expect(password_input).to_be_visible()
    password2 = page.get_by_text("Repeat Password")
    password2_input = page.get_by_label("Repeat Password")
    expect(password2).to_be_visible()
    expect(password2_input).to_be_visible()
    admin = page.get_by_text("Admin", exact=True)
    admin_checkbox = page.get_by_label("Admin")
    expect(admin).to_be_visible()
    expect(admin_checkbox).to_be_visible()
    return fullname_input, email_input, password_input, password2_input, admin_checkbox


@dataclass
class User:
    id: str
    full_name: str
    email: str
    password: str
    is_active: bool
    is_admin: bool


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def create_user(page) -> (Page, User):
    page.goto(URL_USERS_PAGE)
    create_user_button = assert_users_page(page)

    # click create user button
    create_user_button.click()

    fullname_input, email_input, password_input, password2_input, admin_checkbox, cancel_button, save_button = assert_create_user_page(
        page)

    email = random_email()
    password = "@&ZhfLyCxyca2T"

    # submit the form
    user_name = f"User {email}"
    fullname_input.fill(user_name)
    email_input.fill(email)
    password_input.fill(password)
    password2_input.fill(password)

    with page.expect_navigation():
        save_button.click()

    user_id = page.url.split('/')[-1]
    assert is_valid_uuid(user_id)

    return page, User(id=user_id, full_name=user_name, email=email, password=password, is_active=True,
                      is_admin=False)


def test_admin_user_list(page: Page) -> None:
    admin_login(page)

    page.goto(URL_USERS_PAGE)
    assert_users_page(page)

    # verify user in user list
    expect(page.get_by_role("cell", name=full_name)).to_be_visible()
    expect(page.get_by_role("cell", name=email)).to_be_visible()

    is_active = page.get_by_test_id(f"is-active-{email}")
    expect(is_active).to_be_visible()
    expect(is_active).to_be_checked(checked=True)

    is_superuser = page.get_by_test_id(f"is-superuser-{email}")
    expect(is_superuser).to_be_visible()
    expect(is_superuser).to_be_checked(checked=True)

    # click the edit button on the row
    row_button = page.get_by_test_id(f"edit-delete-button-{email}")
    row_button.click()

    # click edit link in menu
    menu_edit_link = page.get_by_role("link", name="Edit")
    menu_edit_link.click()

    # modal title
    expect(page.get_by_role("heading", name="Edit User")).to_be_visible()
    expect(page.get_by_label("Full name")).to_have_value(full_name)


def test_admin_create_user(page: Page) -> None:
    admin_login(page)
    page, user = create_user(page)

    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")


def test_admin_create_user_validate_full_name(page: Page) -> None:
    admin_login(page)

    page.goto(URL_USERS_PAGE)
    create_user_button = assert_users_page(page)

    # click create user button
    create_user_button.click()

    fullname_input, email_input, password_input, password2_input, admin_checkbox, cancel_button, save_button = assert_create_user_page(
        page)

    email = random_email()
    password = "@&ZhfLyCxyca2T"

    # submit the form
    user_name = f"A"  # username too short
    fullname_input.fill(user_name)
    email_input.fill(email)
    password_input.fill(password)
    password2_input.fill(password)
    save_button.click()

    # assert we are still on the user create page
    expect(page).to_have_url(URL_USERS_CREATE_PAGE)
    expect(page.get_by_text("Field must be between")).to_be_visible()


def test_admin_create_user_validate_email(page: Page) -> None:
    admin_login(page)

    page.goto(URL_USERS_PAGE)
    create_user_button = assert_users_page(page)

    # click create user button
    create_user_button.click()

    fullname_input, email_input, password_input, password2_input, admin_checkbox, cancel_button, save_button = assert_create_user_page(
        page)

    email = random_email()
    password = "@&ZhfLyCxyca2T"

    # submit the form
    user_name = f"User {email}"
    fullname_input.fill(user_name)
    email_input.fill("bad@email")  # invalid email
    password_input.fill(password)
    password2_input.fill(password)
    save_button.click()

    # assert we are still on the user create page
    expect(page).to_have_url(URL_USERS_CREATE_PAGE)
    expect(page.get_by_text("Invalid email address")).to_be_visible()


def test_admin_create_user_validate_password_required(page: Page) -> None:
    admin_login(page)

    page.goto(URL_USERS_PAGE)
    create_user_button = assert_users_page(page)

    # click create user button
    create_user_button.click()

    fullname_input, email_input, password_input, password2_input, admin_checkbox, cancel_button, save_button = assert_create_user_page(
        page)

    email = random_email()

    # submit the form
    user_name = f"User {email}"
    fullname_input.fill(user_name)
    email_input.fill(email)
    save_button.click()

    # assert we are still on the user create page
    expect(page).to_have_url(URL_USERS_CREATE_PAGE)
    expect(page.get_by_text("This field is required").first).to_be_visible()
    expect(page.get_by_text("This field is required").nth(1)).to_be_visible()


def test_admin_create_user_validate_password_strong(page: Page) -> None:
    admin_login(page)

    page.goto(URL_USERS_PAGE)
    create_user_button = assert_users_page(page)

    # click create user button
    create_user_button.click()

    fullname_input, email_input, password_input, password2_input, admin_checkbox, cancel_button, save_button = assert_create_user_page(
        page)

    email = random_email()
    password = "weak"

    # submit the form
    user_name = f"User {email}"
    fullname_input.fill(user_name)
    email_input.fill(email)
    password_input.fill(password)
    password2_input.fill(password)
    save_button.click()

    # assert we are still on the user create page
    expect(page).to_have_url(URL_USERS_CREATE_PAGE)
    expect(page.get_by_text("Password must be").first).to_be_visible()
    expect(page.get_by_text("Password must be").nth(1)).to_be_visible()


def test_admin_create_user_validate_passwords_match(page: Page) -> None:
    admin_login(page)

    page.goto(URL_USERS_PAGE)
    create_user_button = assert_users_page(page)

    # click create user button
    create_user_button.click()

    fullname_input, email_input, password_input, password2_input, admin_checkbox, cancel_button, save_button = assert_create_user_page(
        page)

    email = random_email()
    password = strong_password

    # submit the form
    user_name = f"User {email}"
    fullname_input.fill(user_name)
    email_input.fill(email)
    password_input.fill(password)
    password2_input.fill(f"{password}ddd")
    save_button.click()

    # assert we are still on the user create page
    expect(page).to_have_url(URL_USERS_CREATE_PAGE)
    expect(page.get_by_text("Passwords do not match").first).to_be_visible()
    expect(page.get_by_text("Passwords do not match").nth(1)).to_be_visible()


def test_admin_user_detail_view(page: Page) -> None:
    admin_login(page)

    # create the user
    page, user = create_user(page)
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    assert_user_detail_view(page, full_name=user.full_name, email=user.email)


def test_admin_user_detail_edit(page: Page) -> None:
    admin_login(page)

    # create the user
    page, user = create_user(page)
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    edit_button = page.get_by_text("Edit")
    edit_button.click()

    fullname_input, email_input, password_input, password2_input, admin_checkbox = assert_user_form(page)

    # active checkbox is only on edit form
    active = page.get_by_text("Active", exact=True)
    active_checkbox = page.get_by_label("Active")

    expect(fullname_input).to_have_value(user.full_name)
    expect(email_input).to_have_value(user.email)
    expect(admin_checkbox).to_be_checked(checked=False)

    updated_full_name = "updated name"
    updated_email = random_email()

    # update the name and email values
    fullname_input.fill(updated_full_name)
    email_input.fill(updated_email)
    admin_checkbox.check()
    active_checkbox.uncheck()

    # password values are not validated unless they have values

    save_button = page.get_by_role("button", name="Save")
    save_button.click()

    assert_user_detail_view(page, full_name=updated_full_name, email=updated_email, admin=True, active=False)


def test_admin_user_detail_edit_password(page: Page) -> None:
    admin_login(page)

    # create the user
    page, user = create_user(page)
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    edit_button = page.get_by_text("Edit")
    edit_button.click()

    fullname_input, email_input, password_input, password2_input, admin_checkbox = assert_user_form(page)

    updated_password = strong_password

    # update the name and email values
    password_input.fill(updated_password)
    password2_input.fill(updated_password)

    save_button = page.get_by_role("button", name="Save")
    save_button.click()

    assert_user_detail_view(page, full_name=user.full_name, email=user.email)


def test_admin_user_detail_edit_cancel(page: Page) -> None:
    admin_login(page)

    # create the user
    page, user = create_user(page)

    user_page_url = f"{URL_USERS_PAGE}/{user.id}"
    expect(page).to_have_url(user_page_url)

    edit_button = page.get_by_text("Edit")
    edit_button.click()

    cancel_button = page.get_by_role("button", name="Cancel")
    cancel_button.click()

    # on user detail page
    expect(page).to_have_url(user_page_url)


def test_admin_user_detail_delete(page: Page) -> None:
    admin_login(page)

    # create the user
    page, user = create_user(page)
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    edit_button = page.get_by_text("Edit")
    edit_button.click()

    delete_button = page.get_by_role("button", name="Delete")
    delete_button.click()

    # assert modal confirmation
    expect(page.get_by_role("heading", name="Delete user")).to_be_visible()
    expect(page.get_by_text("Are you sure you want to")).to_be_visible()

    expect(page.locator("#modal-content").get_by_role("button", name="Cancel")).to_be_visible()
    page.get_by_role("button", name="Yes, Really").click()

    # on users page
    expect(page).to_have_url(URL_USERS_PAGE)
