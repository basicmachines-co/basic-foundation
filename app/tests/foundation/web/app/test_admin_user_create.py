import pytest
from playwright.sync_api import Page, expect

from utils import random_email
from ..web_test_utils import (
    admin_login, URL_USERS_PAGE, URL_USERS_CREATE_PAGE, strong_password, assert_users_page,
    create_user, assert_create_user_page
)

pytestmark = pytest.mark.playwright


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
