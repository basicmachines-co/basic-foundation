from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from foundation.core.db import async_sessionmaker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:  # pragma: no cover
    """
    :return: An asynchronous generator that yields an AsyncSession object.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with async_sessionmaker() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            # Handle SQLAlchemy specific exceptions
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred.",
            )
        finally:
            # close the session
            await session.close()
