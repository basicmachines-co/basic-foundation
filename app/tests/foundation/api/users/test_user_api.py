import uuid

import pytest
from httpx import AsyncClient

from foundation.api.routes.schemas import UserCreate, UserUpdate
from foundation.core.repository import Repository
from foundation.users.models import User
from utils import random_email, random_lower_string


@pytest.mark.asyncio
async def test_get_users(
        client: AsyncClient, superuser_token_headers: dict[str, str], user_repository: Repository[User]
) -> None:
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


@pytest.mark.asyncio
async def test_get_users_401(client: AsyncClient) -> None:
    r = await client.get(f"users/", headers=None)
    assert r.is_error
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_user(
        client: AsyncClient, superuser_token_headers: dict[str, str], user_repository: Repository[User]
) -> None:
    user_create = UserCreate.model_validate({
        "full_name": "John Doe",
        "email": random_email(),
        "password": random_lower_string(),
    })
    r = await client.post(f"users/", headers=superuser_token_headers, json=user_create.model_dump())
    assert r.status_code == 201
    user_created = r.json()
    user_id = user_created["id"]

    user = await user_repository.find_by_id(user_id)
    assert user is not None
    assert user.full_name == user_create.full_name
    assert user.email == user_create.email


@pytest.mark.asyncio
async def test_create_user_400(
        client: AsyncClient, superuser_token_headers: dict[str, str], user_repository: Repository[User]
) -> None:
    user_in = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )

    user_create = UserCreate.model_validate({
        "full_name": "John Doe",
        "email": user_in.email,
        "password": user_in.hashed_password,
    })

    r = await client.post(f"users/", headers=superuser_token_headers, json=user_create.model_dump())
    assert r.is_error
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_create_user_401(client: AsyncClient) -> None:
    user_create = UserCreate.model_validate({
        "full_name": "John Doe",
        "email": random_email(),
        "password": random_lower_string(),
    })
    r = await client.post(f"users/", headers=None, json=user_create.model_dump())
    assert r.is_error
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_update_user(
        client: AsyncClient, superuser_token_headers: dict[str, str], user_repository: Repository[User]
) -> None:
    user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    user_update = UserUpdate.model_validate({
        "full_name": "John Doe",
        "email": random_email(),
        "password": random_lower_string(),
    })
    r = await client.patch(f"users/{user.id}", headers=superuser_token_headers, json=user_update.model_dump())
    assert r.status_code == 200
    user_updated = r.json()

    user = await user_repository.find_by_id(user.id)
    assert user is not None
    assert user.full_name == user_updated.get("full_name")
    assert user.email == user_updated.get("email")


@pytest.mark.asyncio
async def test_update_user_404(
        client: AsyncClient, superuser_token_headers: dict[str, str], user_repository: Repository[User]
) -> None:
    user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    user_update = UserUpdate.model_validate({
        "full_name": "John Doe",
        "email": random_email(),
        "password": random_lower_string(),
    })
    # use a random UUID
    r = await client.patch(f"users/{uuid.uuid4()}", headers=superuser_token_headers, json=user_update.model_dump())
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_user_400(
        client: AsyncClient, superuser_token_headers: dict[str, str], user_repository: Repository[User]
) -> None:
    user1 = await user_repository.create(
        {
            "full_name": "User1",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    user2 = await user_repository.create(
        {
            "full_name": "User2",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    # conflicting update
    user_update = UserUpdate.model_validate({
        "full_name": "User2 - bad",
        "email": user1.email,
        "password": random_lower_string(),
    })
    r = await client.patch(f"users/{user2.id}", headers=superuser_token_headers, json=user_update.model_dump())
    assert r.status_code == 400
