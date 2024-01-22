import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from basic_api.db import engine
from .conftest import AsyncTestingSessionLocal

Base = declarative_base()


class ExampleModel(Base):
    __tablename__ = "example"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    # Create the tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Insert test data
        async with AsyncTestingSessionLocal() as session:
            test_instance = ExampleModel(id=1, name="Test Name")
            session.add(test_instance)
            await session.commit()

        yield

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
