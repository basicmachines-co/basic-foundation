from typing import Annotated, Tuple, Any

from fastapi import Security, HTTPException, Depends, status, Request
from fastapi_jwt import JwtAccessCookie, JwtAuthorizationCredentials
from sqlalchemy import Select

from foundation.core.config import settings
from foundation.core.repository import Repository
from foundation.users import validate_is_superuser, get_current_user, User
from foundation.users.deps import UserServiceDep, UserRepositoryDep
from foundation.users.schemas import UserPublic
from modules.foundation.web.pagination import Paginator

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

class UserPagination:
    repository: Repository[User]

    def __init__(self, repository: Repository[User]):
        self.repository = repository

    def paginate(
            self,
            request: Request,
            query: Select[Tuple[Any]],
            order_by: str,
            asc: bool = True,
            page_size: int = 10,
    ):
        return Paginator(
            request,
            self.repository,
            query,
            page_size=page_size,
            order_by=order_by,
            ascending=asc,
        )


def get_user_pagination(
        repository: UserRepositoryDep,
) -> UserPagination:  # pragma: no cover
    return UserPagination(repository)


UserPaginationDep = Annotated[UserPagination, Depends(get_user_pagination)]
