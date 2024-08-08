import random
import string

from httpx import AsyncClient

from foundation.core.config import settings


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


async def get_auth_token_headers(client: AsyncClient, login_data: dict[str, str]) -> dict[str, str]:
    r = await client.post(f"/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
