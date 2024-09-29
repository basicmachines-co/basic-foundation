from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import func, String
from sqlalchemy.orm import Mapped, mapped_column

from foundation.core.models import BaseWithId


class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class RoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(BaseWithId):
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
