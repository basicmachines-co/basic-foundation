import uuid
from dataclasses import dataclass
from typing import Optional

from foundation.core.users import StatusEnum, RoleEnum
from playwright.sync_api import expect

from foundation.core.config import settings

BASE_URL = settings.API_URL
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
    full_name: str
    email: str
    password: str
    status: StatusEnum
    role: RoleEnum
    id: Optional[str] = None


admin_email = settings.SUPERUSER_EMAIL
admin_full_name = settings.SUPERUSER_NAME


def is_valid_uuid(value):  # pragma: no cover
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

    role_input = page.get_by_label("Role")
    expect(role_input).to_be_visible()

    return fullname_input, email_input, password_input, password2_input, role_input


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

    (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        role_input,
    ) = assert_user_form(page)

    cancel_button = page.get_by_role("button", name="Cancel")
    expect(cancel_button).to_be_visible()

    save_button = page.get_by_role("button", name="Save")
    expect(save_button).to_be_visible()

    return (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        role_input,
        cancel_button,
        save_button,
    )


def assert_user_detail_view(
    page, full_name=None, email=None, status=StatusEnum.ACTIVE, role=RoleEnum.USER
):
    # full name is displayed in heading
    expect(page.get_by_role("heading", name=full_name)).to_be_visible()
    # details
    expect(page.get_by_text("Full name")).to_be_visible()
    expect(page.locator("#full_name")).to_contain_text(full_name)
    expect(page.get_by_text("Email address")).to_be_visible()
    expect(page.locator("#email")).to_contain_text(email)
    # status values
    expect(page.get_by_text("Status", exact=True)).to_be_visible()
    expect(page.get_by_text(status.capitalize())).to_be_visible()
    expect(page.get_by_text("Role", exact=True)).to_be_visible()
    expect(page.get_by_text(role.capitalize(), exact=True)).to_be_visible()
