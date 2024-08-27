# Read access token from bearer header and cookie (bearer priority)
from typing import Annotated

from fastapi import Security, HTTPException, Depends
from fastapi_jwt import JwtAccessCookie, JwtAuthorizationCredentials

from foundation.core.config import settings
from foundation.users.deps import UserServiceDep
from foundation.users.models import User
from foundation.users.services import UserNotFoundError

access_token_security = JwtAccessCookie(
    secret_key=settings.JWT_SECRET, auto_error=False
)

JwtAuthorizationCredentialsDep = Annotated[
    JwtAuthorizationCredentials, Security(access_token_security)
]


async def get_current_user(
        user_service: UserServiceDep, credentials: JwtAuthorizationCredentialsDep
) -> User:
    if not credentials:
        raise HTTPException(status_code=307, headers={"Location": "/login"})

    subject = credentials.subject
    user_id = subject.get("id")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="No id found in authorization token"
        )

    try:
        user: User | None = await user_service.get_user_by_id(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=307, headers={"Location": "/login"})

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


LoginRequired = Depends(get_current_user)

CurrentUserDep = Annotated[User, LoginRequired]
