import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from basic_api.db import engine

# Create a new instance of the engine
AsyncTestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def async_db_session_rollback() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an async SQLAlchemy session that rolls back at the end of each test function.
    See: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    """

    # create a connection
    connection = await engine.connect()

    # begin a transaction
    transaction = await connection.begin()

    # start a SQLAlchemy session
    session = AsyncTestingSessionLocal(bind=connection)

    # begin a nested transaction
    nested = await session.begin_nested()

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
    """Alias fixture name for tests"""
    yield async_db_session_rollback
