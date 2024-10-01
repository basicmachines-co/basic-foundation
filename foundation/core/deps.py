from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from foundation.core.db import async_sessionmaker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:  # pragma: no cover
    """
    :return: An asynchronous generator yielding database sessions.

    This function provides an asynchronous database session generator using
    SQLAlchemy. It ensures that the session is closed after use. In the
    event of a SQLAlchemy exception, it raises an HTTP 500 error with a
    "Database error occurred" message.

    Example:
        async for session in get_async_session():
            # Use `session` here
            pass

    Error Cases:
        Raises an HTTP 500 exception if an SQLAlchemy specific error occurs.

    """
    async with async_sessionmaker() as session:
        try:
            yield session
        except SQLAlchemyError:
            # Handle SQLAlchemy specific exceptions
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred.",
            )
        finally:
            # close the session
            await session.close()
