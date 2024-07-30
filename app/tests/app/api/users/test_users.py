import pytest
from httpx import AsyncClient

from app.models import User
from app.repository import Repository
from utils import random_email, random_lower_string


@pytest.mark.asyncio
async def test_retrieve_users(
        client: AsyncClient, superuser_token_headers: dict[str, str], user_repository: Repository[User]
) -> None:
    print(f"test_retrieve_users: user_repository: {user_repository}")
    user_in = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )

    r = await client.get(f"users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users["data"]) > 1
    assert "count" in all_users
    for item in all_users["data"]:
        assert "email" in item
