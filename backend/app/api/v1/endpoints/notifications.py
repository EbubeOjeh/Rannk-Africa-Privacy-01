"""In-app notification endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("")
def list_notifications(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    unread_only: bool = False,
    limit: int = 50,
):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)  # noqa: E712
    items = q.order_by(Notification.created_at.desc()).limit(limit).all()
    return {
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "link": n.link,
                "category": n.category,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in items
        ],
        "unread_count": q.filter(Notification.is_read == False).count(),  # noqa: E712
    }


@router.post("/{notification_id}/read", response_model=MessageResponse)
def mark_read(
    notification_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    n = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user.id)
        .first()
    )
    if not n:
        raise NotFoundError("Notification not found.")
    n.is_read = True
    db.commit()
    return MessageResponse(message="Marked as read.")


@router.post("/read-all", response_model=MessageResponse)
def mark_all_read(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> MessageResponse:
    db.query(Notification).filter(
        Notification.user_id == user.id, Notification.is_read == False  # noqa: E712
    ).update({"is_read": True})
    db.commit()
    return MessageResponse(message="All notifications marked as read.")
