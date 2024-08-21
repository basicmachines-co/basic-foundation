import pytest
from sqlalchemy import select

from foundation.core.pagination import Pagination
from foundation.core.repository import Repository
from foundation.users.models import User

pytestmark = pytest.mark.asyncio


async def test_total(user_repository: Repository):
    user_count = await user_repository.count()
    pagination = Pagination(user_repository, query=select(User))

    total = await pagination.total
    assert total == user_count


async def test_page_less_than_one(user_repository: Repository):
    pagination = Pagination(user_repository, query=select(User))

    page = await pagination.page(0)

    assert page.items == []
    assert page.page == 0
    assert page.page_size == 10
    assert page.total == await pagination.total


async def test_page_size_less_than_one(user_repository: Repository):
    pagination = Pagination(user_repository, query=select(User), page_size=-1)

    page = await pagination.page(1)

    assert page.items == []
    assert page.page == 1
    assert page.page_size == -1
    assert page.total == await pagination.total


async def test_page(user_repository: Repository):
    users = await user_repository.find_all(limit=10)
    pagination = Pagination(user_repository, query=select(User), page_size=1)

    page_1 = await pagination.page(1)

    assert page_1.items == [users[0]]
    assert page_1.page == 1
    assert page_1.page_size == 1
    assert page_1.start == 1
    assert page_1.end == 1
    assert page_1.total == await pagination.total
    assert page_1.has_previous() is False
    assert page_1.has_next() is True

    page_2 = await pagination.page(2)

    assert page_2.items == [users[1]]
    assert page_2.page == 2
    assert page_2.page_size == 1
    assert page_2.start == 2
    assert page_2.end == 2
    assert page_2.total == await pagination.total
    assert page_2.has_previous() is True


async def test_page_query(user_repository: Repository):
    query = select(User).filter(True == User.is_active)
    query_result = await user_repository.execute_query(query)
    users = query_result.scalars().all()
    assert len(users) >= 2

    pagination = Pagination(user_repository, query=query, page_size=1)

    page_1 = await pagination.page(1)

    assert page_1.items == [users[0]]
    assert page_1.page == 1
    assert page_1.page_size == 1
    assert page_1.total == await pagination.total

    page_2 = await pagination.page(2)

    assert page_2.items == [users[1]]
    assert page_2.page == 2
    assert page_2.page_size == 1
    assert page_2.total == await pagination.total
