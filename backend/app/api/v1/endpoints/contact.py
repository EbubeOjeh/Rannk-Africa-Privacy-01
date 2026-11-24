"""Contact Student — employer/recruiter → student email relay (keeps email private)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_contact_access, require_school_admin
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.contact_message import ContactMessage
from app.models.student import Student
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.contact import ContactMessageOut, ContactSubmit
from app.services import contact_service

router = APIRouter()


@router.post(
    "/students/{student_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def contact_student(
    student_id: str,
    payload: ContactSubmit,
    db: Session = Depends(get_db),
    sender: User = Depends(require_contact_access),
) -> MessageResponse:
    """Recruiter/staff endpoint — an approved recruiter (or staff) submits an
    inquiry. The student's email is never returned in the response. The
    platform persists the message and forwards it via SMTP when configured.
    """
    student = (
        db.query(Student)
        .filter(Student.id == student_id, Student.is_publicly_visible.is_(True))
        .first()
    )
    if not student:
        raise NotFoundError("Student profile not found or not public.")

    record = contact_service.relay_message(
        db,
        student=student,
        sender_name=payload.sender_name,
        sender_email=payload.sender_email,
        sender_organization=payload.sender_organization,
        sender_role=payload.sender_role,
        subject=payload.subject,
        message=payload.message,
    )
    db.commit()
    if record.status.value == "failed":
        return MessageResponse(message="Message recorded but delivery failed; the team will follow up.")
    return MessageResponse(message="Message sent. The student will receive it at their private address.")


@router.get(
    "/students/{student_id}",
    response_model=list[ContactMessageOut],
    dependencies=[Depends(require_school_admin)],
)
def list_inbox(
    student_id: str, db: Session = Depends(get_db)
) -> list[ContactMessageOut]:
    rows = (
        db.query(ContactMessage)
        .filter(ContactMessage.student_id == student_id)
        .order_by(ContactMessage.created_at.desc())
        .all()
    )
    return [ContactMessageOut.model_validate(r) for r in rows]
