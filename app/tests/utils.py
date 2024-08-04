import random
import string

from fastapi.testclient import TestClient

from foundation.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


async def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.SUPERUSER_EMAIL,
        "password": settings.SUPERUSER_PASSWORD,
    }
    r = await client.post(f"/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
