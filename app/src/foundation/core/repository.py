from typing import Type, Optional, Any, Sequence
from uuid import UUID

from sqlalchemy import select, func, Select, Executable, inspect, Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base


class Repository[T: (declarative_base())]:
    def __init__(self, session: AsyncSession, Model: Type[T]):
        """
        Repository is supposed to work with your entity objects.
        :param session: SQLAlchemy session
        :param Model: SQLAlchemy model class
        """
        self.session = session
        self.Model = Model
        self.primary_key = inspect(self.Model).mapper.primary_key[0]
        self.valid_columns = [column.key for column in inspect(self.Model).columns]

    async def find_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        """
        Finds entities that match given options.
        """
        result = await self.session.execute(
            select(self.Model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """
        Finds first entity that matches given id.
        If entity was not found in the database - returns None.
        """
        try:
            result = await self.session.execute(
                select(self.Model).filter(self.primary_key == entity_id)
            )
            return result.scalars().one()
        except NoResultFound:
            return None

    async def create(self, entity_data: dict) -> T:
        """
        Creates a new entity instance and adds it to the database.
        """

        # filter out extra columns not in model
        model_data = {k: v for k, v in entity_data.items() if k in self.valid_columns}
        entity = self.Model(**model_data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity_id: UUID, entity_data: dict) -> Optional[T]:
        """
        Updates an entity by id with the provided data.
        """
        try:
            result = await self.session.execute(
                select(self.Model).filter(self.Model.id == entity_id)
            )
            entity = result.scalars().one()
            for key, value in entity_data.items():
                setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except NoResultFound:
            return None

    async def delete(self, entity_id: UUID) -> bool:
        """
        Deletes an entity by id.
        """
        try:
            result = await self.session.execute(
                select(self.Model).filter(entity_id == self.primary_key)
            )
            entity = result.scalars().one()
            await self.session.delete(entity)
            await self.session.commit()
            return True
        except NoResultFound as e:
            return False

    async def count(self) -> int:
        """
        Return the count of entities in the database.
        """
        count_stmt = select(func.count()).select_from(self.Model)
        result = await self.session.execute(count_stmt)
        return result.scalar()

    async def execute_query(self, query: Executable) -> Result[Any]:
        """
        Executes a custom SQL query and returns the result.
        """
        result = await self.session.execute(query)
        return result

    async def find_one(self, query: Select[tuple[T]]) -> Optional[T]:
        """
        Executes a custom SQL query and returns the result for one entity
        """
        result = await self.execute_query(query)
        return result.scalars().one_or_none()
