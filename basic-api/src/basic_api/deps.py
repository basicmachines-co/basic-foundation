from typing import AsyncGenerator

from fastapi import Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from basic_api.db import async_session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def log_request(request: Request):
    """
    Log all requst info. Can be added to a router or a route
    `dependencies=[Depends(log_request)]`
    """
    logger.debug(f"{request.method} {request.url}")
    logger.debug("Params:")
    for name, value in request.path_params.items():
        logger.debug(f"\t{name}: {value}")
    logger.debug("Headers:")
    for name, value in request.headers.items():
        logger.debug(f"\t{name}: {value}")
