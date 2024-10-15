from dataclasses import dataclass
from typing import Type, Any, Tuple, Sequence

from sqlalchemy import select, func, Select
from starlette.datastructures import URL
from fastapi import Request

from foundation.core.repository import Repository


@dataclass
class Page:
    """
    Represents a pageable collection of items with metadata and navigation.

    :param url: URL to the current page.
    :param items: Sequence of items on the current page.
    :param page: Current page number.
    :param page_size: Number of items per page.
    :param total: Total number of items.
    :param order_by: Field by which items are ordered, can be None.
    :param ascending: Boolean indicating ascending or descending order.

    :property pages: Total number of pages.
    :property start: Starting index of items on the current page.
    :property end: Ending index of items on the current page.
    :property has_previous: True if there is a previous page, False otherwise.
    :property has_next: True if there is a next page, False otherwise.
    :property previous_page: URL to the previous page.
    :property next_page: URL to the next page.

    Example usage:
        >>> page = Page(url, items, page=1, page_size=10, total=100, order_by=None, ascending=True)
        >>> print(page.pages)
        >>> print(page.start)
        >>> print(page.end)
        >>> print(page.has_previous)
        >>> print(page.has_next)
        >>> print(page.previous_page)
        >>> print(page.next_page)

    Handles cases where the current page is the first or last page in the set.
    """

    def __init__(
        self,
        url: URL,
        items: Sequence[Type[Any]],
        page: int,
        page_size: int,
        total: int,
        order_by: str | None,
        ascending: bool,
    ):
        self.url = url
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total = total
        self.order_by = order_by
        self.ascending = ascending

    @property
    def pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def start(self) -> int:
        return (self.page - 1) * self.page_size + 1

    @property
    def end(self) -> int:
        end = self.page * self.page_size
        return min(end, self.total)

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def previous_page(self) -> URL:
        page_num = self.page - 1 if self.has_previous else 1
        return self.url.include_query_params(
            page_num=page_num, page_size=self.page_size
        )

    @property
    def next_page(self) -> URL:
        page_num = self.page + 1 if self.has_next else self.pages
        return self.url.include_query_params(
            page_num=page_num, page_size=self.page_size
        )


class Paginator:
    """
    Paginator class for managing pagination of database query results.

    :param request: The current HTTP request
    :type request: Request
    :param repository: The repository to execute queries
    :type repository: Repository
    :param query: The SQL Alchemy Select query to paginate
    :type query: Select[Tuple[Any]]
    :param order_by: Optional column name to order results by
    :type order_by: str or None, optional
    :param ascending: Specifies if ordering should be ascending, defaults to True
    :type ascending: bool, optional
    :param page_size: Number of items per page, defaults to 10
    :type page_size: int, optional

    Example usage:

        paginator = Paginator(request, repository, query)
        page = await paginator.page(1)  # Fetches the first page

    Properties:
        total: The total number of items matching the query

    Methods:
        page(page): Fetches items for the given page number.

    Errors:
        Returns an empty list of items if page < 1 or page_size < 1.
    """

    def __init__(
        self,
        request: Request,
        repository: Repository,
        query: Select[Tuple[Any]],
        order_by: str | None = None,
        ascending: bool = True,
        page_size: int = 10,
    ):
        self.request = request
        self.repository = repository
        self.query = query
        self.page_size = page_size
        self.order_by = order_by
        self.ascending = ascending
        self._total = None

    @property
    async def total(self) -> int:
        if self._total is None:
            count_query = select(func.count()).select_from(self.query)  # pyright: ignore [reportArgumentType]
            self._total = await self.repository.count(count_query)
        return self._total

    async def page(self, page: int = 1) -> Page:
        if page < 1 or self.page_size < 1:
            items = []
        else:
            offset = (page - 1) * self.page_size
            result = await self.repository.execute_query(
                self.query.offset(offset).limit(self.page_size)
            )
            items = result.scalars().all()

        return Page(
            url=self.request.url,
            items=items,
            page=page,
            page_size=self.page_size,
            total=await self.total,
            order_by=self.order_by,
            ascending=self.ascending,
        )
