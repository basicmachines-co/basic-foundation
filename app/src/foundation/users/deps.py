from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from foundation.core.deps import get_async_session
from foundation.core.repository import Repository
from foundation.users.models import User
from foundation.users.services import UserService


def get_user_repository(
        async_session: AsyncSession = Depends(get_async_session),
) -> Repository[User]:
    return Repository(async_session, User)


UserRepositoryDep = Annotated[Repository[User], Depends(get_user_repository)]


def get_user_service(repository: UserRepositoryDep) -> UserService:
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
