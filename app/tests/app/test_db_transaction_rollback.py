from typing import AsyncGenerator

import pytest
import pytest_asyncio
import sqlalchemy.orm
from app.db import engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession

Base = sqlalchemy.orm.declarative_base()


class ExampleModel(Base):
    __tablename__ = "example"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    __table_args__ = {"schema": "public"}


@pytest.mark.asyncio
async def test_async_session():
    """
    Reference for using SQLAlchemy async_session
    see: https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_sessionmaker() as sess:
        async with sess.begin():
            sess.add_all(
                [
                    ExampleModel(id=1, name="Test Name"),
                ]
            )

        stmt = select(ExampleModel)

        result = await sess.execute(stmt)

        for a1 in result.scalars():
            print(a1)
            print(f"created at: {a1.id}")

        result = await sess.execute(select(ExampleModel))

        a1 = result.scalars().first()

        a1.name = "new data"

        await sess.commit()

        # access attribute subsequent to commit; this is what
        # expire_on_commit=False allows
        print(a1.name)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def setup_database(event_loop) -> AsyncGenerator[AsyncSession, None]:
    # Create the tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Insert test data
    async with async_sessionmaker() as sess:
        async with sess.begin():
            test_instance = ExampleModel(id=1, name="Test Name")
            sess.add(test_instance)

        yield sess

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_example(session: AsyncSession):
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
