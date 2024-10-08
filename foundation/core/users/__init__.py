from fastapi import HTTPException
from fastapi_jwt import JwtAuthorizationCredentials

from foundation.core.users.models import User, StatusEnum, RoleEnum
from foundation.core.users.services import UserService, UserNotFoundError


async def get_current_user(
    user_service: UserService, credentials: JwtAuthorizationCredentials
) -> User:  # pragma: no cover
    """
    The jwt contains the id PK for the user in a dict format from schemas.AuthTokenPayload
    e.g. {"id": "<primary-key-uuid>"}
    the subject (sub) field of the jwt is called "subject"
    https://github.com/k4black/fastapi-jwt/issues/13

    :param user_service:
    :param credentials:
    :return:
    """
    subject = credentials.subject
    user_id = subject.get("id")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="No id found in authorization token"
        )

    try:
        user: User = await user_service.get_user_by_id(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.status == StatusEnum.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def validate_role_is_admin(user):
    if not user.role == RoleEnum.ADMIN:
        raise HTTPException(
            status_code=403, detail=f"The user {user.id} doesn't have enough privileges"
        )
    return user
