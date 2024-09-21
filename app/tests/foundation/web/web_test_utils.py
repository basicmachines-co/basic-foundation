import uuid
from dataclasses import dataclass

from playwright.sync_api import expect, Page

from foundation.core.config import settings
from utils import random_email

BASE_URL = "http://localhost:8000"
URL_DASHBOARD_PAGE = f"{BASE_URL}/dashboard"
URL_FORGOT_PASSWORD_PAGE = f"{BASE_URL}/forgot-password"
URL_LOGIN_PAGE = f"{BASE_URL}/login"
URL_PROFILE_PAGE = f"{BASE_URL}/profile"
URL_REGISTER_PAGE = f"{BASE_URL}/register"
URL_USERS_PAGE = f"{BASE_URL}/users"
URL_USERS_CREATE_PAGE = f"{BASE_URL}/users/create"

strong_password = "@&ZhfLyCxyca2T"


@dataclass
class User:
    id: str
    full_name: str
    email: str
    password: str
    is_active: bool
    is_admin: bool


admin_email = settings.SUPERUSER_EMAIL
admin_full_name = settings.SUPERUSER_NAME


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


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


def assert_users_page(page):
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

    return page, User(id=user_id, full_name=user_name, email=email, password=password, is_active=True, is_admin=False)


def register_user(page) -> (str, str):
    page.goto(URL_REGISTER_PAGE)
    email = random_email()

    fullname_input = page.get_by_label("Full Name")
    email_input = page.get_by_label("Email address")
    password_input = page.get_by_label("Password", exact=True)
    password2_input = page.get_by_label("Repeat Password")
    register_button = page.get_by_role("button", name="Register")

    fullname_input.fill(f"User {email}")
    email_input.fill(email)
    password_input.fill(strong_password)
    password2_input.fill(strong_password)
    register_button.click()
    expect(page).to_have_url(URL_PROFILE_PAGE)
    return email, strong_password


def admin_login(page):
    login(page,
          email=settings.SUPERUSER_EMAIL,
          password=settings.SUPERUSER_PASSWORD)

    expect(page).to_have_url(URL_DASHBOARD_PAGE)


def login(page, email, password):
    page.goto(URL_LOGIN_PAGE)

    # login
    username_input = page.get_by_label("Email address")
    password_input = page.get_by_label("Password")
    username_input.fill(email)
    password_input.fill(password)
    login_button = page.get_by_role("button", name="Log in")
    login_button.click()


def assert_user_detail_view(page, full_name=None, email=None, active=True, admin=False):
    # full name is displayed in heading
    expect(page.get_by_role("heading", name=full_name)).to_be_visible()
    # details
    expect(page.get_by_text("Full name")).to_be_visible()
    expect(page.locator("#full_name")).to_contain_text(full_name)
    expect(page.get_by_text("Email address")).to_be_visible()
    expect(page.locator("#email")).to_contain_text(email)
    # status values
    expect(page.get_by_text("Status")).to_be_visible()
    expect(page.get_by_text("Active", exact=True)).to_be_visible()
    expect(page.get_by_label("Active")).to_be_checked(checked=active)
    expect(page.get_by_text("Admin", exact=True)).to_be_visible()
    expect(page.get_by_label("Admin")).to_be_checked(checked=admin)
