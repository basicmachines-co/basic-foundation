from unittest.mock import Mock

import pytest
import pytest_asyncio
from sqlalchemy import select
from fastapi import Request
from foundation.users.deps import UserPagination
from foundation.users.models import User
from foundation.core.pagination import Paginator
from mockito import when, mock
from starlette import requests
from starlette.datastructures import URL

from foundation.core.repository import Repository

pytestmark = pytest.mark.asyncio


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
def mock_request():  # pyright: ignore
    request = mock(requests.Request)
    request.url = mock(URL)  # pyright: ignore [reportAttributeAccessIssue]
    when(request.url).include_query_params(page=2, page_size=1).thenReturn(mock(URL))
    when(request.url).include_query_params(page=1, page_size=1).thenReturn(mock(URL))
    when(requests).Request(scope="http").thenReturn(request)
    return request


async def test_user_pagination(user_repository):
    # Arrange
    query = select(User)
    request = Mock(spec=Request)
    order_by = "id"
    page_size = 20

    pagination = UserPagination(repository=user_repository)

    # Act
    paginator = pagination.paginate(
        request=request, query=query, order_by=order_by, asc=False, page_size=page_size
    )

    # Assert
    assert isinstance(paginator, Paginator)
    assert paginator.query == query
    assert paginator.page_size == page_size
    assert paginator.order_by == order_by
    assert paginator.ascending is False
    assert paginator.repository == user_repository
    assert paginator.request == request


async def test_total(mock_request, user_repository: Repository):
    user_count = await user_repository.count()
    pagination = Paginator(mock_request, user_repository, query=select(User))

    total = await pagination.total
    assert total == user_count


async def test_page_less_than_one(mock_request, user_repository: Repository):
    pagination = Paginator(mock_request, user_repository, query=select(User))

    page = await pagination.page(0)

    assert page.items == []
    assert page.page == 0
    assert page.page_size == 10
    assert page.total == await pagination.total


async def test_page_size_less_than_one(mock_request, user_repository: Repository):
    pagination = Paginator(
        mock_request, user_repository, query=select(User), page_size=-1
    )

    page = await pagination.page(1)

    assert page.items == []
    assert page.page == 1
    assert page.page_size == -1
    assert page.total == await pagination.total


async def test_page(
    mock_request, user_repository: Repository, sample_user, inactive_user
):
    users = await user_repository.find_all(limit=10)
    pagination = Paginator(
        mock_request, user_repository, query=select(User), page_size=1
    )

    page_1 = await pagination.page(1)

    assert page_1.items == [users[0]]
    assert page_1.page == 1
    assert page_1.page_size == 1
    assert page_1.start == 1
    assert page_1.end == 1
    assert page_1.total == await pagination.total
    assert page_1.has_previous is False
    assert page_1.has_next is True

    page_2 = await pagination.page(2)

    assert page_2.items == [users[1]]
    assert page_2.page == 2
    assert page_2.page_size == 1
    assert page_2.start == 2
    assert page_2.end == 2
    assert page_2.total == await pagination.total
    assert page_2.has_previous is True


async def test_page_query(
    mock_request, user_repository: Repository, sample_user, inactive_user
):
    query = select(User).filter(User.is_active == True)
    query_result = await user_repository.execute_query(query)
    users = query_result.scalars().all()
    assert len(users) >= 2

    pagination = Paginator(mock_request, user_repository, query=query, page_size=1)

    page_1 = await pagination.page(1)

    assert page_1.items == [users[0]]
    assert page_1.page == 1
    assert page_1.page_size == 1
    assert page_1.total == await pagination.total
    assert page_1.has_previous is False
    assert page_1.has_next is True
    assert page_1.next_page is not None

    page_2 = await pagination.page(2)
    assert page_2.items == [users[1]]
    assert page_2.page == 2
    assert page_2.page_size == 1
    assert page_2.total == await pagination.total

    assert page_2.has_previous is True
    assert page_2.previous_page is not None
