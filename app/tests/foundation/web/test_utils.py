from playwright.sync_api import expect

from utils import random_email

BASE_URL = "http://localhost:8000"
URL_LOGIN_PAGE = f"{BASE_URL}/login"
URL_DASHBOARD_PAGE = f"{BASE_URL}/dashboard"
URL_PROFILE_PAGE = f"{BASE_URL}/profile"
URL_REGISTER_PAGE = f"{BASE_URL}/register"
URL_FORGOT_PASSWORD_PAGE = f"{BASE_URL}/forgot-password"


def register_user(page) -> (str, str):
    page.goto(URL_REGISTER_PAGE)
    email = random_email()
    password = "@&ZhfLyCxyca2T"

    fullname_input = page.get_by_label("Full Name")
    email_input = page.get_by_label("Email address")
    password_input = page.get_by_label("Password", exact=True)
    password2_input = page.get_by_label("Repeat Password")
    register_button = page.get_by_role("button", name="Register")

    fullname_input.fill(f"User {email}")
    email_input.fill(email)
    password_input.fill(password)
    password2_input.fill(password)
    register_button.click()
    expect(page).to_have_url(URL_PROFILE_PAGE)
    return email, password
