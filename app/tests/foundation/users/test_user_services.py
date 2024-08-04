import pytest

from foundation.api.routes.schemas import UserCreate
from foundation.core.security import verify_password
from foundation.users import services as user_service
from foundation.users.models import User
from utils import random_email, random_lower_string


# TODO add failure cases

@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, sample_user: User):
    user = await user_service.get_user_by_email(repository=user_repository, email=sample_user.email)
    assert user.full_name == sample_user.full_name


@pytest.mark.asyncio
async def test_authenticate(user_repository, sample_user: User, sample_user_password: str):
    authenticated_user = await user_service.authenticate(repository=user_repository, email=sample_user.email,
                                                         password=sample_user_password)
    assert authenticated_user is not None
    assert authenticated_user.email == sample_user.email


async def test_authenticate_fails(user_repository, sample_user: User, sample_user_password: str):
    authenticated_user = await user_service.authenticate(repository=user_repository, email=sample_user.email,
                                                         password="bad pass")
    assert authenticated_user is None


@pytest.mark.asyncio
async def test_create_user(user_repository):
    user_create = UserCreate.model_validate({
        "full_name": "John Doe",
        "email": random_email(),
        "password": random_lower_string(),
    })
    created_user = await user_service.create_user(repository=user_repository, user_create=user_create)

    assert created_user.id is not None
    assert created_user.full_name == user_create.full_name
    assert created_user.email == user_create.email
    assert created_user.is_active is False
    assert created_user.is_superuser is False
    assert verify_password(user_create.password, created_user.hashed_password)


@pytest.mark.asyncio
async def test_create_user_fails(user_repository, sample_user: User):
    user_create = UserCreate.model_validate({
        "full_name": "John Doe",
        "email": sample_user.email,
        "password": random_lower_string(),
    })
    created_user = await user_service.create_user(repository=user_repository, user_create=user_create)
    assert created_user is None
