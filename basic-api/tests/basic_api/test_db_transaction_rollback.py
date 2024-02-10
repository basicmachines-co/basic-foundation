import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from basic_api.db import engine, async_session

Base = declarative_base()


class ExampleModel(Base):
    __tablename__ = "example"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    __table_args__ = {"schema": "public"}


@pytest.mark.asyncio
async def test_sync_session():
    """
    Reference for using SQLAlchemy async_session
    see: https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    ExampleModel(id=1, name="Test Name"),
                ]
            )

        stmt = select(ExampleModel)

        result = await session.execute(stmt)

        for a1 in result.scalars():
            print(a1)
            print(f"created at: {a1.id}")

        result = await session.execute(select(ExampleModel))

        a1 = result.scalars().first()

        a1.name = "new data"

        await session.commit()

        # access attribute subsequent to commit; this is what
        # expire_on_commit=False allows
        print(a1.name)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    # see https://github.com/pytest-dev/pytest-asyncio/issues/38
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database(event_loop) -> AsyncGenerator[AsyncSession, None]:
    # Create the tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Insert test data
    async with async_session() as session:
        async with session.begin():
            test_instance = ExampleModel(id=1, name="Test Name")
            session.add(test_instance)

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_example(session: AsyncSession, setup_database):
    # Assume there's an entry in ExampleModel with id 1
    test_id = 1
    new_name = "Updated Name"

    # Fetch the entry
    result = await session.execute(
        select(ExampleModel).where(ExampleModel.id == test_id)
    )
    record = result.scalar_one()

    # Update the entry
    record.name = new_name
    await session.commit()

    # Verify the update
    result = await session.execute(
        select(ExampleModel).where(ExampleModel.id == test_id)
    )
    updated_record = result.scalar_one()
    assert updated_record.name == new_name

    # After this test, the changes will be rolled back automatically by the fixture
