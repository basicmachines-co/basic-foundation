from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from foundation.core.deps import get_async_session
from foundation.core.repository import Repository
from foundation.users.models import User
from foundation.users.services import UserService, UserPagination


def get_user_repository(
    async_session: AsyncSession = Depends(get_async_session),
) -> Repository[User]:  # pragma: no cover
    return Repository(async_session, User)


UserRepositoryDep = Annotated[Repository[User], Depends(get_user_repository)]


def get_user_service(repository: UserRepositoryDep) -> UserService:  # pragma: no cover
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_user_pagination(
    repository: UserRepositoryDep,
) -> UserPagination:  # pragma: no cover
    return UserPagination(repository)


UserPaginationDep = Annotated[UserPagination, Depends(get_user_pagination)]
