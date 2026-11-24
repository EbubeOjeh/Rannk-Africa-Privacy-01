"""Identified voluntary exit review, kept separate from discovery consent."""
from sqlalchemy import ForeignKey,String,JSON,Text
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base,TimestampMixin
class ExitFeedback(Base,TimestampMixin):
    __tablename__='classroom_exit_feedback'
    user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),primary_key=True)
    participant_id:Mapped[str]=mapped_column(String(30),nullable=False)
    respondent_name:Mapped[str]=mapped_column(String(180),nullable=False)
    student_identifier:Mapped[str]=mapped_column(String(100),nullable=False)
    answers:Mapped[list]=mapped_column(JSON,nullable=False)
    general_review:Mapped[str]=mapped_column(Text,default='',nullable=False)
    consent_text:Mapped[str]=mapped_column(Text,nullable=False)
    email_status:Mapped[str]=mapped_column(String(30),default='not_configured',nullable=False)
