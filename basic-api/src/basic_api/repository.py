from typing import Type, TypeVar, Generic, List, Optional, Any

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Define a generic type variable for the entity/model
T = TypeVar("T", bound=declarative_base())


class Repository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Repository is supposed to work with your entity objects.
        :param session: SQLAlchemy session
        :param model: SQLAlchemy model class
        """
        self.session = session
        self.model = model

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Finds entities that match given options.
        """
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def find_by_id(self, id: Any) -> Optional[T]:
        """
        Finds first entity that matches given id.
        If entity was not found in the database - returns None.
        """
        try:
            result = await self.session.execute(
                select(self.model).filter(self.model.id == id)
            )
            return result.scalars().one()
        except NoResultFound:
            return None

    async def create(self, entity_data: dict) -> T:
        """
        Creates a new entity instance and adds it to the database.
        """
        entity = self.model(**entity_data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, id: Any, entity_data: dict) -> Optional[T]:
        """
        Updates an entity by id with the provided data.
        """
        try:
            result = await self.session.execute(
                select(self.model).filter(self.model.id == id)
            )
            entity = result.scalars().one()
            for key, value in entity_data.items():
                setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except NoResultFound:
            return None

    async def delete(self, id: Any) -> Optional[T]:
        """
        Deletes an entity by id.
        """
        try:
            result = await self.session.execute(
                select(self.model).filter(self.model.id == id)
            )
            entity = result.scalars().one()
            await self.session.delete(entity)
            await self.session.commit()
            return entity
        except NoResultFound:
            return None
