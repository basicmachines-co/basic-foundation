from typing import Annotated

from foundation.core.users import validate_role_is_admin, get_current_user
from fastapi import Security, HTTPException, Depends, status
from fastapi_jwt import JwtAccessCookie, JwtAuthorizationCredentials

from foundation.core.config import settings
from foundation.core.users.deps import UserServiceDep
from foundation.core.users.schemas import UserPublic

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
    return validate_role_is_admin(current_user)


AdminRequired = Depends(get_current_superuser)
