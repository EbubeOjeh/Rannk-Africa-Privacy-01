"""Open classroom enrolment. Template IDs are not invitation/access codes."""
from sqlalchemy import ForeignKey,String,JSON,Text
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base,TimestampMixin
class ClassroomEnrollment(Base,TimestampMixin):
    __tablename__='classroom_enrollments'
    user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),primary_key=True)
    participant_id:Mapped[str]=mapped_column(String(30),unique=True,nullable=False)
    template_id:Mapped[str]=mapped_column(String(10),nullable=False)
    academic_record:Mapped[dict]=mapped_column(JSON,nullable=False)
class ClassroomFeedback(Base,TimestampMixin):
    __tablename__='classroom_feedback'
    user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),primary_key=True)
    participant_id:Mapped[str]=mapped_column(String(30),unique=True,nullable=False)
    answers:Mapped[list]=mapped_column(JSON,nullable=False)
    general_review:Mapped[str]=mapped_column(Text,default='',nullable=False)

class ClassroomIdentity(Base,TimestampMixin):
    __tablename__='classroom_identities'
    user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),primary_key=True)
    full_name:Mapped[str]=mapped_column(String(180),nullable=False)
    student_identifier:Mapped[str]=mapped_column(String(100),nullable=False)
