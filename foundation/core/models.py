from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models with automated timestamping.

    Attributes:
        created_at: Timestamp when the record was created, with default automation.
        updated_at: Timestamp when the record was last updated, with default automation.

    Example:
        To create a new model inheriting these properties:

            class User(Base):
                __tablename__ = 'users'
                id: Mapped[int] = mapped_column(primary_key=True)
                username: Mapped[str] = mapped_column(unique=True)
    """

    __abstract__ = True
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())


class UUIDPrimaryKey:
    """
    Represents an entity with a primary key of type UUID.

    Attributes:
        id: Unique identifier for the entity, automatically generated as a UUID.

    Usage:
        class SomeEntity(UUIDPrimaryKey, Base):
            __tablename__ = 'some_entity'
            name: Mapped[str] = mapped_column()

    Example:
        To define a table with a UUID primary key:

        class User(UUIDPrimaryKey, Base):
            __tablename__ = 'user'
            email: Mapped[str] = mapped_column()

    Note:
        The primary key 'id' is automatically assigned using the PostgreSQL
        `gen_random_uuid()` function.
    """

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )


class BaseWithId(Base, UUIDPrimaryKey):
    """
    Defines a base class that combines an abstract SQLAlchemy Base model with a UUID primary key.

    Classes:
        BaseWithId: Abstract base class with a UUID primary key.

    Usage example:
        class MyModel(BaseWithId):
            __tablename__ = 'my_model'
            # additional fields here

    This design enforces that any subclass of BaseWithId will have a UUID as its primary key.
    """

    __abstract__ = True
    pass
