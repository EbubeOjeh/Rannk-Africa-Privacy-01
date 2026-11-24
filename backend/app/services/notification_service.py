"""In-app notifications + best-effort email delivery (SMTP, pluggable)."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.notification import Notification


def notify(
    db: Session,
    *,
    user_id: str,
    title: str,
    body: str | None = None,
    link: str | None = None,
    category: str = "info",
) -> Notification:
    n = Notification(
        user_id=user_id,
        title=title,
        body=body,
        link=link,
        category=category,
    )
    db.add(n)
    db.flush()
    return n


def send_email(to: str, subject: str, body: str) -> bool:
    """Best-effort email send. Returns True only if actually dispatched.

    When SMTP isn't configured (no ``SMTP_HOST``) this is a no-op that logs the
    message, so development / un-provisioned environments never error. Any
    delivery failure is swallowed and logged — email must never break the
    request that triggered it.
    """
    if not to:
        return False
    if not settings.SMTP_HOST:
        logger.info("[email-stub] to={to} subject={subject}", to=to, subject=subject)
        return False
    try:
        msg = EmailMessage()
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except smtplib.SMTPException:
                pass  # server may not offer STARTTLS (e.g. local relay)
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Sent email to {to}", to=to)
        return True
    except Exception as exc:  # noqa: BLE001 — never let email break the flow
        logger.warning("Email send failed to {to}: {err}", to=to, err=str(exc))
        return False


def admin_emails(db: Session) -> list[str]:
    """Addresses that should receive admin notifications: every super admin,
    plus an optional explicit ``ADMIN_NOTIFICATION_EMAIL`` override. De-duped."""
    from app.models.user import User, UserRole  # local import avoids a cycle

    collected = [
        u.email
        for u in db.query(User).filter(User.role == UserRole.SUPER_ADMIN).all()
        if u.email
    ]
    extra = (settings.ADMIN_NOTIFICATION_EMAIL or "").strip()
    if extra:
        collected.append(extra)

    seen: set[str] = set()
    unique: list[str] = []
    for email in collected:
        key = email.lower()
        if key not in seen:
            seen.add(key)
            unique.append(email)
    return unique


def email_admins(db: Session, subject: str, body: str) -> int:
    """Email every admin recipient. Best-effort; returns the number dispatched."""
    sent = 0
    for addr in admin_emails(db):
        if send_email(addr, subject, body):
            sent += 1
    return sent
