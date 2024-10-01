from unittest.mock import AsyncMock, Mock

import pytest
from foundation.core.users import (
    get_current_user,
    User,
    validate_role_is_admin,
    RoleEnum,
    StatusEnum,
)
from fastapi import HTTPException
from fastapi_jwt import JwtAuthorizationCredentials

from foundation.core.users.services import UserService, UserNotFoundError


@pytest.mark.asyncio
async def test_get_current_user_happy_path():
    # Arrange
    user_id = "some-uuid"
    subject = {"id": user_id}

    credentials = Mock(JwtAuthorizationCredentials)
    credentials.subject = subject

    user = Mock(User)
    user.status = StatusEnum.ACTIVE

    user_service = Mock(UserService)
    user_service.get_user_by_id = AsyncMock(return_value=user)

    # Act
    result = await get_current_user(user_service=user_service, credentials=credentials)

    # Assert
    user_service.get_user_by_id.assert_awaited_once_with(user_id=user_id)
    assert result is user


@pytest.mark.asyncio
async def test_get_current_user_no_id_found():
    # Arrange
    user_service = Mock(spec=UserService)

    creds_mock = Mock(spec=JwtAuthorizationCredentials)
    # missing 'id' key
    creds_mock.subject = {"name": "some guy"}

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(user_service=user_service, credentials=creds_mock)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "No id found in authorization token"


@pytest.mark.asyncio
async def test_get_current_user_raises_user_not_found():
    # Arrange
    user_service = Mock(spec=UserService)
    user_service.get_user_by_id = AsyncMock(side_effect=UserNotFoundError("fake-id"))

    creds_mock = Mock(spec=JwtAuthorizationCredentials)
    creds_mock.subject = {"id": "fake-id"}

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(user_service=user_service, credentials=creds_mock)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_current_user_raises_inactive_user():
    # Arrange
    user = Mock(spec=User, id="foo", status=StatusEnum.INACTIVE)

    user_service = Mock(spec=UserService)
    user_service.get_user_by_id = AsyncMock(return_value=user)

    creds_mock = Mock(spec=JwtAuthorizationCredentials)
    creds_mock.subject = {"id": user.id}

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(user_service=user_service, credentials=creds_mock)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Inactive user"


def test_validate_role_is_admin_true():
    # Arrange
    user = Mock()
    user.role = RoleEnum.ADMIN

    # Act
    result = validate_role_is_admin(user)

    # Assert
    assert result is user


def test_validate_role_is_admin_false():
    # Arrange
    user = Mock()
    user.role = RoleEnum.USER
    user.id = "user-id"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        validate_role_is_admin(user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == f"The user {user.id} doesn't have enough privileges"
