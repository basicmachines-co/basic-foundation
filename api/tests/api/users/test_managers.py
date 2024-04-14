from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from api.users.managers import InvalidPasswordException, UserManager
from api.users.models import User


@pytest_asyncio.fixture
async def user_db(session) -> AsyncGenerator[UserManager, None]:
    yield SQLAlchemyUserDatabase(session, User)


@pytest_asyncio.fixture
async def user_manager(user_db) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


@pytest.mark.asyncio
async def test_validate_password(user_manager: UserManager):
    # Test with invalid password
    with pytest.raises(InvalidPasswordException):
        await user_manager.validate_password("12", None)

    # Test with valid password
    assert await user_manager.validate_password("1234", None) is None
