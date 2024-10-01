from typing import Type, Optional, Any, Sequence
from uuid import UUID

from sqlalchemy import select, func, Select, Executable, inspect, Result, Column
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from foundation.core.models import BaseWithId


class Repository[T: BaseWithId]:
    """
    Generic repository pattern implementation for handling database operations.

    Provides basic CRUD operations with an async session.

    :param session: Async database session from SQLAlchemy.
    :param Model: Database model class.

    Example usage:
        async with AsyncSession(engine) as session:
            my_repo = Repository(session, MyModel)
            await my_repo.create({'name': 'Item 1'})
    """

    def __init__(self, session: AsyncSession, Model: Type[T]):
        self.session = session
        self.Model = Model
        self.primary_key: Column[Any] = inspect(self.Model).mapper.primary_key[0]
        self.valid_columns = [column.key for column in inspect(self.Model).columns]

    async def find_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        """
        Fetches records from the database with pagination.

        :param skip: Number of records to skip.
        :param limit: Maximum number of records to fetch.
        :return: List containing the fetched records.
        """
        result = await self.session.execute(
            select(self.Model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """
        Fetches an entity by its unique identifier asynchronously.

        :param entity_id: Unique identifier of the entity
        :return: The entity if found, otherwise None

        Example:
            entity = await repository.find_by_id(some_uuid)

        Error cases:
            - Returns None if no entity with the given id is found
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
        Creates a new entity in the database from the provided data dictionary.

        :param entity_data: A dictionary containing data to be inserted into the database. Only keys present in `self.valid_columns` will be used.
        :return: The created entity object of type `T`.

        Example:
            >>> entity_data = {'name': 'John Doe', 'age': 30, 'extra_field': 'ignored'}
            >>> new_entity = await repo.create(entity_data)
            >>> print(new_entity.name)
            John Doe

        Errors/Exceptions:
            Raises potential `IntegrityError` if there are constraints on the database for the provided data.
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
        Updates an entity with given entity_id using the provided entity_data.

        :param entity_id: UUID of the entity to update
        :param entity_data: Dictionary containing the data to update in the entity
        :return: The updated entity or None if no entity was found

        Example:
            updated_entity = await repository.update(UUID("123e4567-e89b-12d3-a456-426614174000"), {"name": "New Name"})

            if updated_entity is None:
                print("Entity not found")
        """
        id_column: Mapped[UUID] = self.Model.id  # pyright: ignore [reportAssignmentType]
        try:
            result = await self.session.execute(
                select(self.Model).filter(id_column == entity_id)
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
        Deletes an entity from the database.

        :param entity_id: UUID of the entity to delete
        :return: Boolean indicating if the entity was deleted (True) or not found (False)

        Example:
            success = await delete(some_uuid)

        Raises `sqlalchemy.exc.NoResultFound` if the entity does not exist in the database.
        """
        try:
            result = await self.session.execute(
                select(self.Model).filter(self.primary_key == entity_id)
            )
            entity = result.scalars().one()
            await self.session.delete(entity)
            await self.session.commit()
            return True
        except NoResultFound:
            return False

    async def count(self, query: Executable | None = None) -> int:
        """
        Counts entities in the database table represented by `self.Model`.

        :param query: Optional SQL query to modify the count operation. If not provided, counts all entities.
        :type query: Executable or None
        :return: Number of entities that match the query.
        :rtype: int

        Example usage:
            count = await repository.count()
            # This will count all entities in the repository

            custom_query = select(func.count()).select_from(CustomModel).where(CustomModel.active == True)
            active_count = await repository.count(custom_query)
            # This will count all active entities in the CustomModel table

        Error cases:
            - If the query execution fails, an exception will be raised from the session's execute method.
            - Returns 0 if scalar result is None.
        """
        if query is None:
            query = select(func.count()).select_from(self.Model)
        result = await self.session.execute(query)
        scalar = result.scalar()
        return scalar if scalar is not None else 0

    async def execute_query(self, query: Executable) -> Result[Any]:
        """
        Executes the given query asynchronously using the session.

        :param query: An executable query instance.
        :return: Returns the result of the executed query.
        """
        result = await self.session.execute(query)
        return result

    async def find_one(self, query: Select[tuple[T]]) -> Optional[T]:
        """
        Executes a query and retrieves a single record.

        :param query: The query to be executed
        :return: The single record found or None if no record matches the query
        :raises sqlalchemy.exc.SQLAlchemyError: For database errors
        :raises sqlalchemy.exc.NoResultFound: If no record is found but an exception is to be raised

        Example usage:
            result = await find_one(query)
            if result:
                # process the result
            else:
                # handle the case where no record was found
        """
        result = await self.execute_query(query)
        return result.scalars().one_or_none()
