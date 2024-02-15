import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from basic_api.db import engine

# Create a new instance of the engine
AsyncTestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.yield_fixture(scope="session")
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
    6. Yields the session to run tests.
    7. Once the tests are done, rolls back the transaction and closes the session.

    :return: An asynchronous generator that yields the session.
    """

    # create a connection
    connection = await engine.connect()

    # begin a transaction
    transaction = await connection.begin()

    # start a SQLAlchemy session
    session = AsyncTestingSessionLocal(bind=connection)

    # begin a nested transaction
    nested = session.begin_nested()

    @event.listens_for(session.sync_session, "after_transaction_end")
    def end_savepoint(session, transaction):
        """
        listener to restart a nested transaction on commit
        https://github.com/sqlalchemy/sqlalchemy/issues/5811
        :param session:
        :param transaction:
        """
        nonlocal nested
        if not nested.is_active:
            nested = connection.sync_connection.begin_nested()

    # yield the session to run tests
    yield session

    # rollback and close
    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def session(async_db_session_rollback) -> AsyncGenerator[AsyncSession, None]:
    """
    Alias async_db_session_rollback fixture name for tests
    """
    yield async_db_session_rollback
