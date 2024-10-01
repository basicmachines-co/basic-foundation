from enum import Enum
from typing import Optional, Sequence, Iterable
from uuid import UUID

from sqlalchemy import func, String
from sqlalchemy.orm import Mapped, mapped_column

from foundation.core.models import BaseWithId


class StatusEnum(str, Enum):
    """
    Enum class representing status values for a User.

    :Example:

    >>> StatusEnum.values()
    ['active', 'inactive', 'pending']
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

    @classmethod
    def values(cls):
        return [v.value for v in cls]


class RoleEnum(str, Enum):
    """
    Enum for user roles in the system.

    class RoleEnum(str, Enum):

    ADMIN
        Admin role with elevated permissions.

    USER
        Standard user role.

    @classmethod
    def values(cls) -> list[str]
        Returns a list of all role values.

        Example:
            roles = RoleEnum.values()
            # roles => ["admin", "user"]
    """

    ADMIN = "admin"
    USER = "user"

    @classmethod
    def values(cls) -> list[str]:
        return [v.value for v in cls]


class User(BaseWithId):
    """
    Represents a user entity mapped to 'user' table with a public schema.

    Attributes:
        id (UUID): Primary key, generated using a random UUID.
        full_name (str, optional): Full name of the user.
        email (str): Email address of the user, not nullable.
        hashed_password (str): Hashed password of the user.
        status (StatusEnum): Status of the user, default is PENDING.
        role (RoleEnum): Role of the user, default is USER.

    Properties:
        is_admin: Checks if the user's role is ADMIN.
        is_active: Checks if the user's status is ACTIVE.

    Example usage:
        user = User(email='example@example.com', hashed_password='hashed_pw')
        if user.is_admin:
            print("User is an admin")
        if user.is_active:
            print("User is active")

    Error cases:
        - Accessing properties may raise AttributeError if corresponding attributes are not set.
    """

    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    full_name: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(String())
    hashed_password: Mapped[str] = mapped_column(String())
    status: Mapped[StatusEnum] = mapped_column(
        String(), nullable=False, default=StatusEnum.PENDING
    )
    role: Mapped[RoleEnum] = mapped_column(
        String(), nullable=False, default=RoleEnum.USER
    )

    @property
    def is_admin(self):
        return self.role == RoleEnum.ADMIN

    @property
    def is_active(self):
        return self.status == StatusEnum.ACTIVE
