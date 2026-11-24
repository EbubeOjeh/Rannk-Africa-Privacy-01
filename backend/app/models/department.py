"""Department within a faculty."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.faculty import Faculty
    from app.models.field import Field
    from app.models.student import Student
    from app.models.university import University


class Department(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("university_id", "name", name="uq_dept_uni_name"),)

    name: Mapped[str] = mapped_column(String(160), nullable=False)

    university_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    faculty_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("faculties.id", ondelete="SET NULL"), nullable=True, index=True
    )
    field_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("fields.id", ondelete="SET NULL"), nullable=True, index=True
    )

    avg_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    university: Mapped["University"] = relationship(back_populates="departments")
    faculty: Mapped["Faculty | None"] = relationship(back_populates="departments")
    field: Mapped["Field | None"] = relationship(back_populates="departments")
    students: Mapped[list["Student"]] = relationship(back_populates="department")
