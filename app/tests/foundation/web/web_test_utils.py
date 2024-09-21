from playwright.sync_api import expect

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
