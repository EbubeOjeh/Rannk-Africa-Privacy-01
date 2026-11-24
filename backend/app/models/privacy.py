"""Independent consent and immutable recipient-specific application disclosure."""
from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDPKMixin, TimestampMixin

class StudentConsent(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'student_consents'
    student_id: Mapped[str] = mapped_column(ForeignKey('students.id'), unique=True, nullable=False)
    choices: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

class PrivacyEvent(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'privacy_events'
    student_id: Mapped[str] = mapped_column(ForeignKey('students.id'), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

class ApplicationDisclosure(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'application_disclosures'
    application_id: Mapped[str] = mapped_column(ForeignKey('opportunity_applications.id'), unique=True, nullable=False)
    student_id: Mapped[str] = mapped_column(ForeignKey('students.id'), index=True, nullable=False)
    recipient_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(200), nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
