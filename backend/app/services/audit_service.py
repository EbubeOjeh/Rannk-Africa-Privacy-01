"""Lightweight audit logging helper."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def record(
    db: Session,
    *,
    actor: User | None,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    ip: str | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_id=actor.id if actor else None,
        actor_email=actor.email if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=ip,
        metadata_json=metadata,
    )
    db.add(entry)
    db.flush()
    return entry
