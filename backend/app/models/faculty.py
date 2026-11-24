"""Faculty (college) within a university."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.university import University


class Faculty(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "faculties"
    __table_args__ = (UniqueConstraint("university_id", "name", name="uq_faculty_uni_name"),)

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    university_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    university: Mapped["University"] = relationship(back_populates="faculties")
    departments: Mapped[list["Department"]] = relationship(back_populates="faculty", cascade="all,delete-orphan")
