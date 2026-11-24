"""User self-service (profile) + admin listing."""
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_super_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthUser
from app.schemas.team import ProfileUpdate
from app.services import auth_service, file_storage
from app.validators.files import ALLOWED_IMAGE, validate_upload

router = APIRouter()


@router.get("/me", response_model=AuthUser)
def me(user: User = Depends(get_current_user)) -> AuthUser:
    return auth_service._hydrate_auth_user(user, user.university)


@router.patch("/me", response_model=AuthUser)
def update_me(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AuthUser:
    """Update own profile. Email is intentionally NOT editable."""
    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.title is not None:
        user.title = payload.title
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    db.commit()
    db.refresh(user)
    return auth_service._hydrate_auth_user(user, user.university)


@router.post("/me/avatar", response_model=AuthUser)
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AuthUser:
    validate_upload(file, allowed=ALLOWED_IMAGE)
    url = file_storage.save_upload(file, subdir=f"avatars/users/{user.id}")
    user.avatar_url = url
    db.commit()
    db.refresh(user)
    return auth_service._hydrate_auth_user(user, user.university)


@router.get("", response_model=list[AuthUser], dependencies=[Depends(require_super_admin)])
def list_users(db: Session = Depends(get_db)) -> list[AuthUser]:
    rows = db.query(User).order_by(User.created_at.desc()).limit(200).all()
    return [auth_service._hydrate_auth_user(r, r.university) for r in rows]
