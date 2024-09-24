import uuid

import pytest
from sqlalchemy import select

from foundation.users.models import User


@pytest.mark.asyncio
async def test_create_user(user_repository, session):
    new_user = await user_repository.create(
        {
            "full_name": "John Doe",
            "email": "john@smith.com",
            "hashed_password": "hash",
        }
    )
    found_user = await user_repository.find_by_id(new_user.id)
    assert found_user.full_name == "John Doe"


@pytest.mark.asyncio
async def test_find_user_by_id(user_repository, sample_user):
    found_user = await user_repository.find_by_id(sample_user.id)
    assert found_user is not None
    assert found_user.id == sample_user.id
    assert found_user.full_name == sample_user.full_name


@pytest.mark.asyncio
async def test_find_all_users(user_repository, sample_user):
    found_users = await user_repository.find_all(limit=1)
    assert found_users is not None
    assert len(found_users) == 1


@pytest.mark.asyncio
async def test_update_user(user_repository, sample_user, session):
    updated_at_orig = sample_user.updated_at
    await user_repository.update(sample_user.id, {"full_name": "Updated"})
    await session.refresh(sample_user)  # Refresh to get updated data
    assert sample_user.full_name == "Updated"
    # assert updated_at is also changed
    assert updated_at_orig <= sample_user.updated_at


@pytest.mark.asyncio
async def test_update_user_not_found(user_repository, sample_user, session):
    updated = await user_repository.update(uuid.uuid4(), {"full_name": "Updated?"})
    assert updated is None


@pytest.mark.asyncio
async def test_delete_user(user_repository, sample_user, session):
    await user_repository.delete(sample_user.id)
    deleted_user = await session.get(User, sample_user.id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_user_not_found(user_repository, sample_user, session):
    result = await user_repository.delete(uuid.uuid4())
    assert result is False


@pytest.mark.asyncio
async def test_count_user(user_repository, sample_user, session):
    count = await user_repository.count()
    assert count > 0


@pytest.mark.asyncio
async def test_find_one(user_repository, sample_user, session):
    stmt = select(User).where(sample_user.email == User.email)
    found_user = await user_repository.find_one(stmt)
    assert found_user is not None
    assert found_user.id == sample_user.id
    assert found_user.full_name == sample_user.full_name


@pytest.mark.asyncio
async def test_find_one_not_found(user_repository, sample_user, session):
    stmt = select(User).where(sample_user.email == "bad@email.com")
    found_user = await user_repository.find_one(stmt)
    assert found_user is None


@pytest.mark.asyncio
async def test_execute_query(user_repository, sample_user, session):
    stmt = select(User).where(sample_user.email == User.email)
    result = await user_repository.execute_query(stmt)
    found_users = result.fetchall()
    assert found_users is not None
    assert len(found_users) == 1
    found_user = found_users[0][0]
    assert found_user.id == sample_user.id
    assert found_user.full_name == sample_user.full_name
