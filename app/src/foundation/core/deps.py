from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from foundation.core.db import async_sessionmaker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    :return: An asynchronous generator that yields an AsyncSession object.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with async_sessionmaker() as session:
        yield session
