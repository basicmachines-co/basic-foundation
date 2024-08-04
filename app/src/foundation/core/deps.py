from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from foundation.core.db import async_sessionmaker
from foundation.core.repository import Repository
from foundation.users.models import User


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    :return: An asynchronous generator that yields an AsyncSession object.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with async_sessionmaker() as session:
        yield session


def get_user_repository(
        async_session: AsyncSession = Depends(get_async_session),
) -> Repository[User]:
    return Repository(async_session, User)


UserRepositoryDep = Annotated[Repository[User], Depends(get_user_repository)]
