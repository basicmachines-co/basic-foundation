import random
import string

import emails
from emails.backend.response import SMTPResponse
from httpx import AsyncClient
from mockito import when, mock

from foundation.core.config import settings
from foundation.users.schemas import AuthToken


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


async def get_superuser_auth_token_headers(client: AsyncClient) -> dict[str, str]:
    login_data = {
        "username": settings.SUPERUSER_EMAIL,
        "password": settings.SUPERUSER_PASSWORD,
    }
    return await get_auth_token_headers(client, login_data)


async def get_auth_token(client: AsyncClient, login_data: dict[str, str]) -> AuthToken:
    r = await client.post(f"/api/auth/login/access-token", data=login_data)
    assert r.status_code == 200, r.text
    return AuthToken.model_validate(r.json())


async def get_auth_token_headers(client: AsyncClient, login_data: dict[str, str]) -> dict[str, str]:
    auth_token = await get_auth_token(client, login_data)
    headers = {"Authorization": f"Bearer {auth_token.access_token}"}
    return headers


def mock_emails_send():
    response = mock({
        'status_code': 250,
        '_finished': True
    }, spec=SMTPResponse)
    when(emails.Message).send(...).thenReturn(response)
