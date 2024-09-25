import httpx
import pytest
from playwright.sync_api import expect

from foundation.core.config import settings
from foundation.test_utils import random_email
from foundation.users.schemas import AuthToken
from modules.foundation.web.web_test_utils import (
    URL_LOGIN_PAGE,
    URL_DASHBOARD_PAGE,
    User,
    URL_USERS_PAGE,
    assert_users_page,
    assert_create_user_page,
    is_valid_uuid,
    BASE_URL,
    URL_REGISTER_PAGE,
    strong_password,
    URL_PROFILE_PAGE,
)


@pytest.fixture
def do_admin_login(page):
    login(page, email=settings.SUPERUSER_EMAIL, password=settings.SUPERUSER_PASSWORD)

    expect(page).to_have_url(URL_DASHBOARD_PAGE)
    return page


def login(page, email, password):
    page.goto(URL_LOGIN_PAGE)

    # login
    username_input = page.get_by_label("Email address")
    password_input = page.get_by_label("Password")
    username_input.fill(email)
    password_input.fill(password)
    login_button = page.get_by_role("button", name="Log in")
    login_button.click()


@pytest.fixture
def register_user(page):
    page.goto(URL_REGISTER_PAGE)
    email = random_email()

    fullname_input = page.get_by_label("Full Name")
    email_input = page.get_by_label("Email address")
    password_input = page.get_by_label("Password", exact=True)
    password2_input = page.get_by_label("Repeat Password")
    register_button = page.get_by_role("button", name="Register")

    full_name = f"User {email}"
    fullname_input.fill(full_name)
    email_input.fill(email)
    password_input.fill(strong_password)
    password2_input.fill(strong_password)
    register_button.click()

    expect(page).to_have_url(URL_PROFILE_PAGE)

    user = User(
        full_name=full_name,
        email=email,
        password=strong_password,
        is_active=True,
        is_admin=False,
    )
    yield page, user

    # delete the user
    get_user_response = httpx.get(
        f"{BASE_URL}/api/users/email/{email}",
        headers=get_superuser_auth_token_headers(),
    )
    u = get_user_response.json()

    # TODO response returns `is_superuser`
    user = User(
        id=u["id"],
        full_name=u["full_name"],
        email=u["email"],
        password=strong_password,
        is_active=u["is_active"],
        is_admin=False,
    )
    delete_api_url = f"{BASE_URL}/api/users/{user.id}"
    httpx.delete(delete_api_url, headers=get_superuser_auth_token_headers())


@pytest.fixture
def create_user(do_admin_login):
    page = do_admin_login
    page.goto(URL_USERS_PAGE)
    create_user_button = assert_users_page(page)

    # click create user button
    create_user_button.click()

    (
        fullname_input,
        email_input,
        password_input,
        password2_input,
        admin_checkbox,
        cancel_button,
        save_button,
    ) = assert_create_user_page(page)

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

    user_id = page.url.split("/")[-1]
    assert is_valid_uuid(user_id)

    user = User(
        id=user_id,
        full_name=user_name,
        email=email,
        password=password,
        is_active=True,
        is_admin=False,
    )
    expect(page).to_have_url(f"{URL_USERS_PAGE}/{user.id}")

    yield page, user

    # delete the user
    delete_api_url = f"{BASE_URL}/api/users/{user.id}"
    httpx.delete(delete_api_url, headers=get_superuser_auth_token_headers())


def get_superuser_auth_token_headers() -> dict[str, str]:
    login_data = {
        "username": settings.SUPERUSER_EMAIL,
        "password": settings.SUPERUSER_PASSWORD,
    }
    return get_auth_token_headers(login_data)


def get_auth_token_headers(login_data: dict[str, str]) -> dict[str, str]:
    auth_token = get_auth_token(login_data)
    headers = {"Authorization": f"Bearer {auth_token.access_token}"}
    return headers


def get_auth_token(login_data: dict[str, str]) -> AuthToken:
    r = httpx.post(f"{BASE_URL}/api/auth/login/access-token", data=login_data)
    assert r.status_code == 200, r.text
    return AuthToken.model_validate(r.json())
