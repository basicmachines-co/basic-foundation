import uuid

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
    CookieTransport,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app import config
from app.deps import get_async_session
from app.users.managers import UserManager
from app.users.models import User

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(
    cookie_max_age=3600, cookie_name="basic-api", cookie_secure=False
)


def get_jwt_strategy() -> JWTStrategy:
    """
    Returns a JWTStrategy object with the specified secret and lifetime.

    :return: The JWTStrategy object.
    :rtype: JWTStrategy
    """
    return JWTStrategy(secret=config.settings.jwt_secret, lifetime_seconds=3600)


jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


async def get_cookie_backend():
    """
    Returns the cookie backend.

    :return: A generator that yields the cookie backend.
    """
    yield cookie_backend


async def get_user_db(session: AsyncSession = Depends(get_async_session)) -> AsyncSession:
    """
    Retrieve the user database.

    :param session: The async session to connect to the database.
    :return: The user database object.
    """
    return SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """
    Return an instance of the UserManager using the provided user database.

    :param user_db: The user database to be used by the UserManager.
    :type user_db: SQLAlchemyUserDatabase
    :return: An instance of the UserManager.
    :rtype: UserManager
    """
    return UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [jwt_backend, cookie_backend]
)

current_active_user = fastapi_users.current_user(active=True)
current_optional_user = fastapi_users.current_user(optional=True)
