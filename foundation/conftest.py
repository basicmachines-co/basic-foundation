import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from foundation.core import security
from foundation.core.db import engine
from foundation.core.repository import Repository
from foundation.users.models import User
from foundation.test_utils import (
    random_email,
)


@pytest.fixture
def unstub_mocks():
    """
    Fixture for unstubbing mocked methods

    To use, add the following to a pytest file:

    pytestmark = pytest.mark.usefixtures("unstub_mocks")

    :return:
    """
    from mockito import unstub

    yield
    unstub()


# Create a new instance of the engine
AsyncTestingSessionLocal = sessionmaker(  # pyright: ignore [reportCallIssue]
    engine,  # pyright: ignore [reportArgumentType]
    class_=AsyncSession,
    expire_on_commit=False,  # pyright: ignore [reportArgumentType]
)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    # see https://github.com/pytest-dev/pytest-asyncio/issues/38
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_db_session_rollback(event_loop) -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a database session with rollback functionality.

    This method:
    1. Creates a connection to the database.
    2. Begins a transaction.
    3. Starts a SQLAlchemy session using the created connection.
    4. Begins a nested transaction within the session using the connection.
    5. Registers a listener to restart the nested transaction on commit.
    6. Yields the session to run a test.
    7. Once a test is done, rolls back the transaction and closes the session.

    :return: An asynchronous generator that yields the session.
    """
    print(f"Using event loop {event_loop}")

    # create a connection
    connection = await engine.connect()

    # begin a transaction
    transaction = await connection.begin()

    # start a SQLAlchemy session
    async_session = AsyncTestingSessionLocal(bind=connection)

    # begin a nested transaction
    nested = await async_session.begin_nested()  # pyright: ignore [reportGeneralTypeIssues]

    @event.listens_for(async_session.sync_session, "after_transaction_end")  # pyright: ignore [reportAttributeAccessIssue]
    def end_savepoint(session, transaction):
        """
        listener to restart a nested transaction on commit
        https://github.com/sqlalchemy/sqlalchemy/issues/5811
        :param session:
        :param transaction:
        """
        nonlocal nested
        if not nested.is_active:
            nested = connection.sync_connection.begin_nested()  # pyright: ignore [reportOptionalMemberAccess]

    print("Yielding test rollback session...")

    # yield the session to run tests
    yield async_session  # pyright: ignore [reportReturnType]

    # rollback and close
    await async_session.close()  # pyright: ignore [reportGeneralTypeIssues]
    await transaction.rollback()
    await connection.close()

    print("test session closed")


@pytest_asyncio.fixture
async def session(async_db_session_rollback) -> AsyncGenerator[AsyncSession, None]:
    """
    Alias async_db_session_rollback fixture name for tests
    """
    yield async_db_session_rollback


@pytest_asyncio.fixture
async def user_repository(session) -> Repository[User]:
    return Repository[User](session, User)


@pytest_asyncio.fixture
async def sample_user_password() -> str:
    return "password"


@pytest_asyncio.fixture
async def sample_user(user_repository: Repository[User], sample_user_password: str):
    sample_user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": random_email(),
            "hashed_password": security.get_password_hash(sample_user_password),
            "is_active": True,
        }
    )
    return sample_user


@pytest_asyncio.fixture
async def inactive_user(user_repository: Repository[User], sample_user_password: str):
    sample_user = await user_repository.create(
        {
            "full_name": "Lazy John Doe",
            "email": random_email(),
            "hashed_password": security.get_password_hash(sample_user_password),
            "is_active": False,
        }
    )
    return sample_user
