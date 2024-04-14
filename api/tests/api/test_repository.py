import pytest
import pytest_asyncio

from api.repository import Repository
from api.users.models import User


@pytest_asyncio.fixture
def user_repository(session):
    return Repository[User](session, User)


@pytest_asyncio.fixture
async def sample_user(session):
    user = User(
        first_name="John",
        last_name="Doe",
        email="johndoe@sample.test",
        hashed_password="hash",
    )
    session.add(user)
    await session.commit()
    return user


@pytest.mark.asyncio
async def test_create_user(user_repository, session):
    new_user = await user_repository.create(
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "john@smith.com",
            "hashed_password": "hash",
        }
    )
    found_user = await user_repository.find_by_id(new_user.id)
    assert found_user.first_name == "Jane"
    assert found_user.last_name == "Smith"


@pytest.mark.asyncio
async def test_find_user_by_id(user_repository, sample_user):
    found_user = await user_repository.find_by_id(sample_user.id)
    assert found_user is not None
    assert found_user.id == sample_user.id
    assert found_user.first_name == sample_user.first_name
    assert found_user.last_name == sample_user.last_name


@pytest.mark.asyncio
async def test_update_user(user_repository, sample_user, session):
    await user_repository.update(sample_user.id, {"last_name": "Updated"})
    await session.refresh(sample_user)  # Refresh to get updated data
    assert sample_user.last_name == "Updated"


@pytest.mark.asyncio
async def test_delete_user(user_repository, sample_user, session):
    await user_repository.delete(sample_user.id)
    deleted_user = await session.get(User, sample_user.id)
    assert deleted_user is None
