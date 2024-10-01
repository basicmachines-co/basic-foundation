from typing import Annotated

from fastapi import Depends
from fastapi import Security
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer

from foundation.core.config import settings
from foundation.users import get_current_user, validate_role_is_admin
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
    """
    Gets ths User associated with the supplied JWT credentials

    :param user_service: Dependency injection of the UserService
    :param credentials: Dependency injection of the JwtAuthorizationCredentials
    :return: A User object representing the current authenticated user

    Usage example:
        current_user = await get_current_api_user(user_service, credentials)

    Raises:
        Any exceptions from `get_current_user` function
    """
    return await get_current_user(user_service, credentials)


CurrentUserDep = Annotated[User, Depends(get_current_api_user)]


async def get_current_superuser(current_user: CurrentUserDep) -> User:
    """
    Check if the current user has admin privileges

    :param current_user: The user making the request
    :return: Admin user if valid, raises exception if not

    Example usage:

        admin_user = await get_current_superuser(current_user)
    """
    return validate_role_is_admin(current_user)


AdminRequired = Depends(get_current_superuser)
