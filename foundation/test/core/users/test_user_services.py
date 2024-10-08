import uuid

import pytest
import pytest_asyncio

from foundation.core.security import verify_password
from foundation.core.users.models import User
from foundation.core.users.services import (
    UserNotFoundError,
    UserValueError,
    UserService,
    UserCreateError,
)
from foundation.test.utils import random_email, random_lower_string, mock_emails_send
from foundation.core.users import StatusEnum, RoleEnum

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def user_service(user_repository, unstub_mocks) -> UserService:
    mock_emails_send()

    return UserService(user_repository)


async def test_get_users(user_service, sample_user: User):
    count, users = await user_service.get_users(skip=0, limit=100)
    assert count > 0
    assert len(users) == count


async def test_get_user_by_id(user_service, sample_user: User):
    user = await user_service.get_user_by_id(user_id=sample_user.id)
    assert user == sample_user


async def test_get_user_by_id_not_found(user_service):
    user_id = uuid.uuid4()
    with pytest.raises(UserNotFoundError, match=f"user {user_id} does not exist"):
        await user_service.get_user_by_id(user_id=user_id)


async def test_get_user_by_email(user_service, sample_user: User):
    user = await user_service.get_user_by_email(email=sample_user.email)
    assert user.id == sample_user.id
    assert user.full_name == sample_user.full_name


async def test_get_user_by_email_not_found(user_service, sample_user: User):
    email = random_email()
    with pytest.raises(UserNotFoundError, match=f"user {email} does not exist"):
        await user_service.get_user_by_email(email=email)


async def test_authenticate(user_service, sample_user: User, sample_user_password: str):
    authenticated_user = await user_service.authenticate(
        email=sample_user.email, password=sample_user_password
    )
    assert authenticated_user is not None
    assert authenticated_user.email == sample_user.email


async def test_authenticate_user_not_found(
    user_service, sample_user: User, sample_user_password: str
):
    authenticated_user = await user_service.authenticate(
        email="not@real.email", password=sample_user_password
    )
    assert authenticated_user is None


async def test_authenticate_fails(
    user_service, sample_user: User, sample_user_password: str
):
    authenticated_user = await user_service.authenticate(
        email=sample_user.email, password="bad pass"
    )
    assert authenticated_user is None


async def test_create_user(user_service):
    user_create = {
        "full_name": "John Doe",
        "email": random_email(),
        "password": "kszd8t5Sg#NT",
    }
    created_user = await user_service.create_user(create_dict=user_create)

    assert created_user.id is not None
    assert created_user.full_name == user_create.get("full_name")
    assert created_user.email == user_create.get("email")
    assert created_user.status == StatusEnum.ACTIVE
    assert created_user.role == RoleEnum.USER
    assert created_user.is_active is True
    assert created_user.is_admin is False
    assert verify_password(user_create["password"], created_user.hashed_password)


async def test_create_user_fails(user_service, sample_user: User):
    user_create = {
        "full_name": "John Doe",
        "email": sample_user.email,
        "password": random_lower_string(),
    }
    with pytest.raises(
        UserCreateError,
        match=f"A user with email {user_create.get("email")} already exists",
    ):
        await user_service.create_user(create_dict=user_create)


async def test_update_user(user_service, sample_user: User):
    user_update = {
        "full_name": "New name",
        "email": random_email(),
        "status": StatusEnum.ACTIVE,
        "role": RoleEnum.ADMIN,
    }
    updated_user = await user_service.update_user(
        user_id=sample_user.id, update_dict=user_update
    )

    assert updated_user.id == sample_user.id
    assert updated_user.full_name == user_update.get("full_name")
    assert updated_user.email == user_update.get("email")
    assert updated_user.status == user_update.get("status")
    assert updated_user.role == user_update.get("role")

    assert updated_user.is_admin is True
    assert updated_user.is_admin is True


async def test_update_user_password(user_service, sample_user: User):
    new_password = "my voice is my password"
    user_update = {
        "password": new_password,
    }
    await user_service.update_user(user_id=sample_user.id, update_dict=user_update)

    user = await user_service.get_user_by_id(user_id=sample_user.id)
    assert verify_password(new_password, user.hashed_password)


async def test_update_user_fails(user_service, sample_user: User):
    user_create = {
        "full_name": "John Doe",
        "email": random_email(),
        "password": random_lower_string(),
    }
    created_user = await user_service.create_user(create_dict=user_create)
    assert created_user.id is not None

    # update the new user to have a conflicting email
    user_update = {
        "full_name": "New name",
        "email": sample_user.email,
        "password": random_lower_string(),
        "staus": StatusEnum.ACTIVE,
        "role": RoleEnum.ADMIN,
    }
    with pytest.raises(UserValueError, match="user can not be updated"):
        await user_service.update_user(user_id=created_user.id, update_dict=user_update)


async def test_delete_user(user_service, sample_user: User):
    await user_service.delete_user(user_id=sample_user.id)

    with pytest.raises(
        UserNotFoundError, match=f"user {sample_user.id} does not exist"
    ):
        assert await user_service.get_user_by_id(user_id=sample_user.id)


async def test_delete_user_not_found(user_service):
    user_id = uuid.uuid4()
    with pytest.raises(UserNotFoundError, match=f"user {user_id} does not exist"):
        assert await user_service.delete_user(user_id=user_id)


async def test_get_users_count(user_service):
    assert await user_service.get_users_count() > 0


async def test_get_active_users_count(user_service):
    assert await user_service.get_active_users_count() > 0


async def test_get_admin_users_count(user_service):
    assert await user_service.get_admin_users_count() > 0


async def test_recover_password(user_service, sample_user: User):
    # doesn't fail
    await user_service.recover_password(email=sample_user.email)
