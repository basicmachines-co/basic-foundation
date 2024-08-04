from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi import Security
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer
from sqlalchemy.ext.asyncio import AsyncSession

from foundation.core.config import settings
from foundation.core.deps import get_async_session
from foundation.users.models import User

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

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

JwtAuthorizationCredentialsDep = Annotated[JwtAuthorizationCredentials, Security(access_token_security)]


async def get_current_user(session: SessionDep, credentials: JwtAuthorizationCredentialsDep) -> User:
    # the "subject" (sub) field of the jwt contains the id PK for the user
    # https://github.com/k4black/fastapi-jwt/issues/13
    user: User | None = await session.get(User, credentials.subject)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
