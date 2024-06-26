from typing import AsyncGenerator

from app.db import async_sessionmaker
from app.repository import Repository
from app.users.models import User
from fastapi import Request, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    :return: An asynchronous generator that yields an AsyncSession object.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with async_sessionmaker() as session:
        yield session


async def log_request(request: Request):
    """
    Log all request info. Can be added to a router or a route
    `dependencies=[Depends(log_request)]`
    """
    logger.debug(f"{request.method} {request.url}")
    logger.debug("Params:")
    for name, value in request.path_params.items():
        logger.debug(f"\t{name}: {value}")
    logger.debug("Headers:")
    for name, value in request.headers.items():
        logger.debug(f"\t{name}: {value}")


def get_user_repository(
        async_session: AsyncSession = Depends(get_async_session),
) -> Repository[User]:
    return Repository(async_session, User)
