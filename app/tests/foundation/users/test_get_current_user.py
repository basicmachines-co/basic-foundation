import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from fastapi_jwt import JwtAuthorizationCredentials
from foundation.users import get_current_user, User
from foundation.users.services import UserService, UserNotFoundError


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
    user = Mock(spec=User, id="foo", is_active=False)

    user_service = Mock(spec=UserService)
    user_service.get_user_by_id = AsyncMock(return_value=user)

    creds_mock = Mock(spec=JwtAuthorizationCredentials)
    creds_mock.subject = {"id": user.id}

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(user_service=user_service, credentials=creds_mock)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Inactive user"
