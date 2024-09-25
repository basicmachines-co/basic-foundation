from typing import Annotated, Tuple, Any

from fastapi import Security, HTTPException, Depends, status, Request
from fastapi_jwt import JwtAccessCookie, JwtAuthorizationCredentials
from sqlalchemy import Select

from foundation.core.config import settings
from foundation.core.repository import Repository
from foundation.users import validate_is_superuser, get_current_user, User
from foundation.users.deps import UserServiceDep, UserRepositoryDep
from foundation.users.schemas import UserPublic
from foundation.core.pagination import Paginator

access_token_security = JwtAccessCookie(
    secret_key=settings.JWT_SECRET, auto_error=False
)

JwtAuthorizationCredentialsDep = Annotated[
    JwtAuthorizationCredentials, Security(access_token_security)
]


async def get_current_web_user(
    user_service: UserServiceDep, credentials: JwtAuthorizationCredentialsDep
) -> UserPublic:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"},
        )
    user = await get_current_user(user_service, credentials)
    return UserPublic.model_validate(user)


LoginRequired = Depends(get_current_web_user)

CurrentUserDep = Annotated[UserPublic, LoginRequired]


async def get_current_superuser(current_user: CurrentUserDep) -> UserPublic:
    return validate_is_superuser(current_user)


AdminRequired = Depends(get_current_superuser)
