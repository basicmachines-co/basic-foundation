from typing import Annotated

from fastapi import Depends
from fastapi import Security
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer

from foundation.core.config import settings
from foundation.users import get_current_user, validate_is_superuser
from foundation.users.deps import UserServiceDep
from foundation.users.models import User

# Read access token from bearer header
access_token_security_bearer = JwtAccessBearer(
    secret_key=settings.JWT_SECRET,
    auto_error=True,  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

# Read refresh token from bearer header only
refresh_token_security = JwtRefreshBearer(
    secret_key=settings.JWT_SECRET,
    auto_error=True,  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

JwtAuthorizationCredentialsDep = Annotated[
    JwtAuthorizationCredentials, Security(access_token_security_bearer)
]


async def get_current_api_user(
        user_service: UserServiceDep, credentials: JwtAuthorizationCredentialsDep
) -> User:
    return await get_current_user(user_service, credentials)


CurrentUserDep = Annotated[User, Depends(get_current_api_user)]


async def get_current_superuser(current_user: CurrentUserDep) -> User:
    return validate_is_superuser(current_user)
