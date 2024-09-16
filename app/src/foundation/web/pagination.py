from dataclasses import dataclass
from typing import Type, Any, List

from sqlalchemy import select, func
from sqlalchemy.orm import Query
from starlette.datastructures import URL
from starlette.requests import Request

from foundation.core.repository import Repository


@dataclass
class Page:
    def __init__(
            self, url: URL, items: List[Type[Any]], page: int, page_size: int, total: int, order_by: str,
            ascending: bool
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
        return self.url.include_query_params(page=page_num, page_size=self.page_size)

    @property
    def next_page(self) -> URL:
        page_num = self.page + 1 if self.has_next else self.pages
        return self.url.include_query_params(page=page_num, page_size=self.page_size)


class Paginator:
    def __init__(
            self,
            request: Request,
            repository: Repository,
            query: Query = None,
            page_size: int = 10,
            order_by: str = None,
            ascending: bool = True,
    ):
        self.request = request
        self.repository = repository
        self.query = query
        self.page_size = page_size
        self._total = None
        self.order_by = order_by
        self.ascending = ascending

    @property
    async def total(self) -> int:
        if self._total is None:
            count_query = select(func.count()).select_from(self.query)
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
            ascending=self.ascending
        )
