"""Custom company role with a per-permission set (dynamic role system)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(300))
    # List of permission keys from app.core.permissions.PERMISSION_CATALOG.
    permissions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # System roles (CEO, the seeded titles) can be edited but not deleted.
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    members: Mapped[list["User"]] = relationship(back_populates="company_role")
