import pytest
from httpx import AsyncClient

from foundation.core.security import generate_password_reset_token
from foundation.users.models import User
from foundation.users.schemas import UserPublic, Message, NewPassword
from test_utils import get_auth_token, mock_emails_send, random_lower_string

pytestmark = pytest.mark.asyncio


async def test_login_access_token(
    client: AsyncClient, sample_user: User, sample_user_password: str
):
    login_data = {
        "username": sample_user.email,
        "password": sample_user_password,
    }
    auth_token = await get_auth_token(client, login_data)

    assert auth_token.access_token is not None
    r = await client.post(
        f"/api/auth/login/test-token",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert r.status_code == 200
    user = UserPublic.model_validate(r.json())
    assert user.email == login_data["username"]


async def test_login_access_token_invalid_email(
    client: AsyncClient,
    sample_user: User,
):
    login_data = {
        "username": "bademail@test.com",
        "password": "bad-password",
    }
    r = await client.post(f"/api/auth/login/access-token", data=login_data)
    assert r.status_code == 400
    content = r.json()
    assert content["detail"] == "Incorrect email or password"


async def test_login_access_token_invalid_password(
    client: AsyncClient, sample_user: User
):
    login_data = {
        "username": sample_user.email,
        "password": "bad-password",
    }
    r = await client.post(f"/api/auth/login/access-token", data=login_data)
    assert r.status_code == 400


async def test_login_access_token_inactive_user(
    client: AsyncClient, inactive_user: User, sample_user_password: str
):
    login_data = {
        "username": inactive_user.email,
        "password": sample_user_password,
    }
    r = await client.post(f"/api/auth/login/access-token", data=login_data)
    assert r.status_code == 400


async def test_recover_password(
    client: AsyncClient, sample_user: User, sample_user_password: str, unstub_mocks
):
    # mock sending an email
    mock_emails_send()
    r = await client.post(f"/api/auth/password-recovery/{sample_user.email}")
    assert r.status_code == 200

    message = Message.model_validate(r.json())
    assert message.message is not None


async def test_recover_password_invalid_email_404(
    client: AsyncClient, sample_user: User
):
    r = await client.post("/api/auth/password-recovery/invalid@email.com")
    assert r.status_code == 404


async def test_reset_password(
    client: AsyncClient, sample_user: User, sample_user_password: str
):
    new_password = NewPassword.model_validate(
        {
            "token": generate_password_reset_token(email=sample_user.email),
            "new_password": random_lower_string(),
        }
    )
    r = await client.post("/api/auth/password-reset/", json=new_password.model_dump())
    assert r.status_code == 200

    message = Message.model_validate(r.json())
    assert message.message is not None


async def test_reset_password_invalid_email_404(client: AsyncClient):
    invalid_email = "invalid-email@test.com"
    new_password = NewPassword.model_validate(
        {
            "token": generate_password_reset_token(email=invalid_email),
            "new_password": random_lower_string(),
        }
    )
    r = await client.post("/api/auth/password-reset/", json=new_password.model_dump())
    assert r.status_code == 404
    content = r.json()
    assert content["detail"] == f"The user {invalid_email} does not exist"


async def test_reset_password_invalid_token(client: AsyncClient):
    new_password = NewPassword.model_validate(
        {
            "token": "invalid-token",
            "new_password": random_lower_string(),
        }
    )
    r = await client.post("/api/auth/password-reset/", json=new_password.model_dump())
    assert r.status_code == 400
    content = r.json()
    assert content["detail"] == "Invalid token"


async def test_reset_password_inactive_user_400(
    client: AsyncClient, inactive_user: User
):
    new_password = NewPassword.model_validate(
        {
            "token": generate_password_reset_token(email=inactive_user.email),
            "new_password": random_lower_string(),
        }
    )
    r = await client.post("/api/auth/password-reset/", json=new_password.model_dump())
    assert r.status_code == 400
