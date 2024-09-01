# Read access token from bearer header and cookie (bearer priority)
from typing import Annotated

from fastapi import Security, HTTPException, Depends, status
from fastapi_jwt import JwtAccessCookie, JwtAuthorizationCredentials

from foundation.core.config import settings
from foundation.users.deps import UserServiceDep
from foundation.users.models import User
from foundation.users.schemas import UserPublic
from foundation.users.services import UserNotFoundError

access_token_security = JwtAccessCookie(
    secret_key=settings.JWT_SECRET, auto_error=False
)

JwtAuthorizationCredentialsDep = Annotated[
    JwtAuthorizationCredentials, Security(access_token_security)
]


async def get_current_user(
        user_service: UserServiceDep, credentials: JwtAuthorizationCredentialsDep
) -> UserPublic:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/login"})

    subject = credentials.subject
    user_id = subject.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No id found in authorization token"
        )

    try:
        user: User | None = await user_service.get_user_by_id(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/login"})

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return UserPublic.model_validate(user)


LoginRequired = Depends(get_current_user)

CurrentUserDep = Annotated[UserPublic, LoginRequired]
