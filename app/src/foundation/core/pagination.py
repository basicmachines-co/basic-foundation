from dataclasses import dataclass
from typing import Type, Any, List

from sqlalchemy import select, func
from sqlalchemy.orm import Query

from foundation.core.repository import Repository


@dataclass
class Page:
    def __init__(self, items: List[Type[Any]], page: int, page_size: int, total: int):
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total = total

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
    def previous_page(self) -> int:
        return self.page - 1 if self.has_previous else 1

    @property
    def next_page(self) -> int:
        return self.page + 1 if self.has_next else self.pages


class Pagination:
    def __init__(self, repository: Repository, query: Query = None, page_size: int = 10):
        self.repository = repository
        self.query = query
        self.page_size = page_size
        self._total = None

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
            result = await self.repository.execute_query(self.query.offset(offset).limit(self.page_size))
            items = result.scalars().all()

        return Page(
            items=items,
            page=page,
            page_size=self.page_size,
            total=await self.total
        )
