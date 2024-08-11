from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi import Security
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer

from foundation.core.config import settings
from foundation.users.deps import UserServiceDep
from foundation.users.models import User
from foundation.users.services import UserNotFoundError

# Read access token from bearer header and cookie (bearer priority)
access_token_security = JwtAccessBearer(
    secret_key=settings.JWT_SECRET,
    auto_error=True  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

# Read refresh token from bearer header only
refresh_token_security = JwtRefreshBearer(
    secret_key=settings.JWT_SECRET,
    auto_error=True  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

JwtAuthorizationCredentialsDep = Annotated[JwtAuthorizationCredentials, Security(access_token_security)]


async def get_current_user(user_service: UserServiceDep, credentials: JwtAuthorizationCredentialsDep) -> User:
    # Notes
    # the jwt contains the id PK for the user in a dict format,
    # e.g. {"id": "<primary-key-uuid>"}
    # the subject (sub) field of the jwt is called "subject"
    # https://github.com/k4black/fastapi-jwt/issues/13
    subject = credentials.subject
    user_id = subject.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="No id found in authorization token")

    try:
        user: User | None = await user_service.get_user_by_id(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_superuser(current_user: CurrentUser) -> User:
    return validate_is_superuser(current_user)


def validate_is_superuser(user):
    if not user.is_superuser:
        raise HTTPException(
            status_code=403, detail=f"The user {user.id} doesn't have enough privileges"
        )
    return user
