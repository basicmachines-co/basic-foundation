import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient

from foundation.core.repository import Repository
from foundation.users import User
from foundation.users.schemas import UserCreate, UserUpdate, UserPublic
from foundation.test_utils import (
    random_email,
    random_lower_string,
    get_auth_token_headers,
)
from users import RoleEnum

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def sample_user_auth_token_headers(
    client: AsyncClient, sample_user: User, sample_user_password: str
) -> dict[str, str]:
    login_data = {
        "username": sample_user.email,
        "password": sample_user_password,
    }
    return await get_auth_token_headers(client, login_data)


async def test_get_user(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    user_in = await user_repository.create(
        {
            "full_name": "New user",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )

    r = await client.get(
        f"/api/users/{user_in.id}", headers=superuser_auth_token_headers
    )
    assert r.status_code == 200
    user = UserPublic.model_validate(r.json())
    assert user.id is not None
    assert user.full_name == user_in.full_name
    assert user.email == user_in.email


async def test_get_user_unauthorized_401(client: AsyncClient) -> None:
    r = await client.get(f"/api/users/{uuid.uuid4()}", headers=None)
    assert r.is_error
    assert r.status_code == 401


async def test_get_user_not_found_404(
    client: AsyncClient, superuser_auth_token_headers
) -> None:
    r = await client.get(
        f"/api/users/{uuid.uuid4()}", headers=superuser_auth_token_headers
    )
    assert r.is_error
    assert r.status_code == 404


async def test_get_user_by_email(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    user_email = random_email()
    user_in = await user_repository.create(
        {
            "full_name": "New user",
            "email": user_email,
            "hashed_password": random_lower_string(),
        }
    )

    r = await client.get(
        f"/api/users/email/{user_email}", headers=superuser_auth_token_headers
    )
    assert r.status_code == 200
    user = UserPublic.model_validate(r.json())
    assert user.id is not None
    assert user.full_name == user_in.full_name
    assert user.email == user_in.email


async def test_get_user_by_email_unauthorized_401(client: AsyncClient) -> None:
    r = await client.get("/api/users/email/somme@email.com", headers=None)
    assert r.is_error
    assert r.status_code == 401


async def test_get_user_by_email_not_found_404(
    client: AsyncClient, superuser_auth_token_headers
) -> None:
    r = await client.get(
        "/api/users/email/email@doesnot.exist", headers=superuser_auth_token_headers
    )
    assert r.is_error
    assert r.status_code == 404


async def test_get_user_current_user(
    client: AsyncClient, sample_user: User, sample_user_auth_token_headers
) -> None:
    r = await client.get(
        f"/api/users/{sample_user.id}", headers=sample_user_auth_token_headers
    )
    assert r.status_code == 200
    user = UserPublic.model_validate(r.json())
    assert user.id == sample_user.id
    assert user.full_name == sample_user.full_name
    assert user.email == sample_user.email


async def test_get_users(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    user_in = await user_repository.create(
        {
            "full_name": "New user",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )

    r = await client.get("/api/users/", headers=superuser_auth_token_headers)
    all_users = r.json()

    assert len(all_users["data"]) > 1
    assert "count" in all_users

    new_user_found = False
    for item in all_users["data"]:
        assert "email" in item
        if item["email"] == user_in.email:
            new_user_found = True
    assert new_user_found


async def test_get_users_401(client: AsyncClient) -> None:
    r = await client.get("/api/users/", headers=None)
    assert r.is_error
    assert r.status_code == 401


async def test_get_users_403(
    client: AsyncClient, sample_user_auth_token_headers: dict[str, str]
) -> None:
    r = await client.get("/api/users/", headers=sample_user_auth_token_headers)
    assert r.is_error
    assert r.status_code == 403


async def test_create_user(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    user_create = UserCreate.model_validate(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "password": "kszd8t5Sg#NT",
        }
    )
    r = await client.post(
        "/api/users/",
        headers=superuser_auth_token_headers,
        json=user_create.model_dump(),
    )
    assert r.status_code == 201
    user_created = UserPublic.model_validate(r.json())

    assert user_created.id is not None
    assert user_create.full_name == user_created.full_name
    assert user_create.email == user_created.email


async def test_create_user_400(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    user_in = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": "kszd8t5Sg#NT",
        }
    )

    user_create = UserCreate.model_validate(
        {
            "full_name": "John Doe",
            "email": user_in.email,
            "password": user_in.hashed_password,
        }
    )

    r = await client.post(
        "/api/users/",
        headers=superuser_auth_token_headers,
        json=user_create.model_dump(),
    )
    assert r.is_error
    assert r.status_code == 400


async def test_create_user_401(client: AsyncClient) -> None:
    user_create = UserCreate.model_validate(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "password": "kszd8t5Sg#NT",
        }
    )
    r = await client.post("/api/users/", headers=None, json=user_create.model_dump())
    assert r.is_error
    assert r.status_code == 401


async def test_create_user_403(
    client: AsyncClient, sample_user_auth_token_headers: dict[str, str]
) -> None:
    user_create = UserCreate.model_validate(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "password": "kszd8t5Sg#NT",
        }
    )
    r = await client.post(
        "/api/users/",
        headers=sample_user_auth_token_headers,
        json=user_create.model_dump(),
    )
    assert r.is_error
    assert r.status_code == 403


async def test_update_user(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    user_update = UserUpdate.model_validate(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "password": random_lower_string(),
        }
    )
    r = await client.patch(
        f"/api/users/{user.id}",
        headers=superuser_auth_token_headers,
        json=user_update.model_dump(),
    )
    assert r.status_code == 200
    user_updated = r.json()

    user = await user_repository.find_by_id(user.id)
    assert user is not None
    assert user.full_name == user_updated.get("full_name")
    assert user.email == user_updated.get("email")


async def test_update_user_404(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    user_update = UserUpdate.model_validate(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "password": random_lower_string(),
        }
    )
    # use a random UUID
    r = await client.patch(
        f"/api/users/{uuid.uuid4()}",
        headers=superuser_auth_token_headers,
        json=user_update.model_dump(),
    )
    assert r.status_code == 404


async def test_update_user_400(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    """
    the `users/id` update endpoint returns a 400 status code because there is already a user with the supplied email
    """
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
    user_update = UserUpdate.model_validate(
        {
            "full_name": "User2 - bad",
            "email": user1.email,
            "password": random_lower_string(),
        }
    )
    r = await client.patch(
        f"/api/users/{user2.id}",
        headers=superuser_auth_token_headers,
        json=user_update.model_dump(),
    )
    assert r.status_code == 400


async def test_update_user_401(
    client: AsyncClient, user_repository: Repository[User]
) -> None:
    """
    the `users/id` update endpoint returns a 401 status code because no auth header is passed in the request.
    """
    user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    user_update = UserUpdate.model_validate(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "password": random_lower_string(),
        }
    )
    r = await client.patch(
        f"/api/users/{user.id}", headers=None, json=user_update.model_dump()
    )
    assert r.status_code == 401


async def test_update_user_403(
    client: AsyncClient,
    sample_user_auth_token_headers: dict[str, str],
    user_repository: Repository[User],
) -> None:
    """
    the `users/id` update endpoint returns a 403 status code because the user is not a superuser.
    """

    user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    user_update = UserUpdate.model_validate(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "password": random_lower_string(),
        }
    )
    r = await client.patch(
        f"/api/users/{user.id}",
        headers=sample_user_auth_token_headers,
        json=user_update.model_dump(),
    )
    assert r.status_code == 403


async def test_update_user_current_user(
    client: AsyncClient,
    sample_user: User,
    sample_user_auth_token_headers: dict[str, str],
    user_repository: Repository[User],
) -> None:
    """
    the `users/id` update endpoint is successful because the current_user is updating their own user.
    """
    user_update = UserUpdate.model_validate(
        {
            "full_name": "New Name",
            "email": random_email(),
            "password": random_lower_string(),
        }
    )
    r = await client.patch(
        f"/api/users/{sample_user.id}",
        headers=sample_user_auth_token_headers,
        json=user_update.model_dump(),
    )
    assert r.status_code == 200
    user_updated = UserPublic.model_validate(r.json())
    assert user_updated.full_name == user_update.full_name
    assert user_updated.email == user_update.email


async def test_delete_user(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    r = await client.delete(
        f"/api/users/{user.id}", headers=superuser_auth_token_headers
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("message") is not None


async def test_delete_user_404(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    r = await client.delete(
        f"/api/users/{uuid.uuid4()}", headers=superuser_auth_token_headers
    )
    assert r.status_code == 404


async def test_delete_user_401(
    client: AsyncClient, user_repository: Repository[User]
) -> None:
    r = await client.delete(f"/api/users/{uuid.uuid4()}", headers=None)
    assert r.status_code == 401


async def test_delete_user_403(
    client: AsyncClient,
    sample_user_auth_token_headers: dict[str, str],
    user_repository: Repository[User],
) -> None:
    user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": random_lower_string(),
        }
    )
    r = await client.delete(
        f"/api/users/{user.id}", headers=sample_user_auth_token_headers
    )
    assert r.status_code == 403


async def test_delete_user_current_user(
    client: AsyncClient,
    sample_user: User,
    sample_user_auth_token_headers: dict[str, str],
    user_repository: Repository[User],
) -> None:
    r = await client.delete(
        f"/api/users/{sample_user.id}", headers=sample_user_auth_token_headers
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("message") is not None


async def test_superuser_cannot_delete_self(
    client: AsyncClient, superuser_auth_token_headers, user_repository: Repository[User]
) -> None:
    from users import StatusEnum

    new_superuser = UserCreate.model_validate(
        {
            "full_name": "new superuser",
            "email": random_email(),
            "password": "kszd8t5Sg#NT",
            "status": StatusEnum.ACTIVE,
            "rol": RoleEnum.ADMIN,
        }
    )
    r = await client.post(
        "/api/users/",
        headers=superuser_auth_token_headers,
        json=new_superuser.model_dump(),
    )
    assert r.status_code == 201
    user_created = UserPublic.model_validate(r.json())

    auth_headers = await get_auth_token_headers(
        client, {"username": new_superuser.email, "password": new_superuser.password}
    )
    r = await client.delete(f"/api/users/{user_created.id}", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data.get("message") is not None
