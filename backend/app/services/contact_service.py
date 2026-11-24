"""Contact relay — persist + forward employer/recruiter messages to students.

The student's email is NEVER exposed to the sender. The platform stores the
inquiry and forwards it via SMTP when configured; in dev (no SMTP host) the
message is logged and persisted as ``sent`` so the flow can be exercised.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.contact_message import ContactMessage, ContactMessageStatus
from app.models.student import Student
from app.services import notification_service


def relay_message(
    db: Session,
    *,
    student: Student,
    sender_name: str,
    sender_email: str,
    sender_organization: str | None,
    sender_role: str | None,
    subject: str,
    message: str,
) -> ContactMessage:
    record = ContactMessage(
        student_id=student.id,
        sender_name=sender_name.strip(),
        sender_email=sender_email.strip().lower(),
        sender_organization=(sender_organization or "").strip() or None,
        sender_role=(sender_role or "").strip() or None,
        subject=subject.strip(),
        message=message.strip(),
        status=ContactMessageStatus.PENDING,
    )
    db.add(record)
    db.flush()

    target = student.email
    if not target:
        record.status = ContactMessageStatus.FAILED
        record.failure_reason = "Student has no contact email on file."
        return record

    full_body = (
        f"You received a new inquiry via RankAfrica.\n\n"
        f"From:    {sender_name} <{sender_email}>\n"
        f"Org:     {sender_organization or '(not provided)'}\n"
        f"Role:    {sender_role or '(not provided)'}\n\n"
        f"Subject: {subject}\n\n"
        f"--- Message ---\n{message}\n\n"
        f"Reply directly to {sender_email} to continue the conversation."
    )

    delivered = notification_service.send_email(
        to=target,
        subject=f"[RankAfrica] {subject}",
        body=full_body,
    )

    if not settings.SMTP_HOST or delivered:
        # In dev (no SMTP) we treat the stubbed email as delivered so the UI
        # accurately reflects "message recorded + queued". A real send is a
        # drop-in replacement in notification_service.send_email.
        record.status = ContactMessageStatus.SENT
        record.sent_at = datetime.now(timezone.utc)
    else:
        record.status = ContactMessageStatus.FAILED
        record.failure_reason = "SMTP send returned False."

    logger.info(
        "ContactMessage relay student_id={sid} status={s}",
        sid=student.id,
        s=record.status.value,
    )
    return record
