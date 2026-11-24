"""Team & dynamic-role management.

Gated on the ``manage_team`` permission (the technical admin and the CEO have
it via full access). Also exposes a public roster for the marketing Team page.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.core.permissions import ALL_PERMISSIONS, MANAGE_TEAM, PERMISSION_CATALOG
from app.core.security import hash_password
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.team import (
    PermissionOut,
    ProfileUpdate,
    PublicTeamMember,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    TeamCreate,
    TeamMemberOut,
    TeamUpdate,
)

router = APIRouter()

DEFAULT_TEMP_PASSWORD = "rankpass"
STAFF_ROLES = (UserRole.SUPER_ADMIN, UserRole.EMPLOYEE)


def _member_out(u: User) -> TeamMemberOut:
    data = TeamMemberOut.model_validate(u).model_dump()
    data["company_role_name"] = u.company_role.name if u.company_role else None
    return TeamMemberOut.model_validate(data)


def _role_out(r: Role, member_count: int = 0) -> RoleOut:
    out = RoleOut.model_validate(r).model_dump()
    out["member_count"] = member_count
    return RoleOut.model_validate(out)


# --- Public roster (marketing Team page) ------------------------------------
# Display order for the leadership cards (most senior first); anyone else falls
# back to creation order after these.
TEAM_DISPLAY_ORDER = [
    "Chief Executive Officer",
    "Chief Technology Officer",
    "Chief Operating Officer",
    "Chief Marketing Officer",
    "Chief Partnerships Officer",
    "Chief Programs Officer",
]


@router.get("/public", response_model=list[PublicTeamMember])
def public_team(db: Session = Depends(get_db)) -> list[PublicTeamMember]:
    rows = (
        db.query(User)
        .filter(User.is_active.is_(True), User.company_role_id.is_not(None))
        .all()
    )

    def _key(u: User):
        role_name = u.company_role.name if u.company_role else (u.title or "")
        idx = TEAM_DISPLAY_ORDER.index(role_name) if role_name in TEAM_DISPLAY_ORDER else len(TEAM_DISPLAY_ORDER)
        return (idx, u.created_at)

    rows.sort(key=_key)
    return [
        PublicTeamMember(name=u.name, title=u.title or (u.company_role.name if u.company_role else None), avatar_url=u.avatar_url)
        for u in rows
    ]


# --- Permission catalog (for the role editor) -------------------------------
@router.get("/permissions", response_model=list[PermissionOut], dependencies=[Depends(require_permission(MANAGE_TEAM))])
def list_permissions() -> list[PermissionOut]:
    return [PermissionOut(**p) for p in PERMISSION_CATALOG]


# --- Roles -------------------------------------------------------------------
@router.get("/roles", response_model=list[RoleOut], dependencies=[Depends(require_permission(MANAGE_TEAM))])
def list_roles(db: Session = Depends(get_db)) -> list[RoleOut]:
    roles = db.query(Role).order_by(Role.is_system.desc(), Role.name.asc()).all()
    counts = dict(
        db.query(User.company_role_id, func.count(User.id))
        .group_by(User.company_role_id)
        .all()
    )
    return [_role_out(r, counts.get(r.id, 0)) for r in roles]


def _clean_permissions(perms: list[str]) -> list[str]:
    return sorted({p for p in perms if p in ALL_PERMISSIONS})


@router.post("/roles", response_model=RoleOut, dependencies=[Depends(require_permission(MANAGE_TEAM))])
def create_role(payload: RoleCreate, db: Session = Depends(get_db)) -> RoleOut:
    if db.query(Role).filter(Role.name == payload.name.strip()).first():
        raise ConflictError("A role with that name already exists.")
    role = Role(
        name=payload.name.strip(),
        description=payload.description,
        permissions=_clean_permissions(payload.permissions),
        is_system=False,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return _role_out(role, 0)


@router.patch("/roles/{role_id}", response_model=RoleOut, dependencies=[Depends(require_permission(MANAGE_TEAM))])
def update_role(role_id: str, payload: RoleUpdate, db: Session = Depends(get_db)) -> RoleOut:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise NotFoundError("Role not found.")
    if payload.name is not None:
        clash = db.query(Role).filter(Role.name == payload.name.strip(), Role.id != role_id).first()
        if clash:
            raise ConflictError("A role with that name already exists.")
        role.name = payload.name.strip()
    if payload.description is not None:
        role.description = payload.description
    if payload.permissions is not None:
        role.permissions = _clean_permissions(payload.permissions)
    db.commit()
    db.refresh(role)
    count = db.query(User).filter(User.company_role_id == role.id).count()
    return _role_out(role, count)


@router.delete("/roles/{role_id}", response_model=MessageResponse, dependencies=[Depends(require_permission(MANAGE_TEAM))])
def delete_role(role_id: str, db: Session = Depends(get_db)) -> MessageResponse:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise NotFoundError("Role not found.")
    if role.is_system:
        raise ForbiddenError("System roles can't be deleted (you can still edit their permissions).")
    if db.query(User).filter(User.company_role_id == role.id).count() > 0:
        raise ConflictError("Reassign the members of this role before deleting it.")
    db.delete(role)
    db.commit()
    return MessageResponse(message="Role deleted.")


# --- Team members ------------------------------------------------------------
@router.get("", response_model=list[TeamMemberOut], dependencies=[Depends(require_permission(MANAGE_TEAM))])
def list_team(db: Session = Depends(get_db)) -> list[TeamMemberOut]:
    rows = (
        db.query(User)
        .filter(User.role.in_(STAFF_ROLES))
        .order_by(User.created_at.asc())
        .all()
    )
    return [_member_out(u) for u in rows]


@router.post("", response_model=TeamMemberOut, dependencies=[Depends(require_permission(MANAGE_TEAM))])
def create_member(payload: TeamCreate, db: Session = Depends(get_db)) -> TeamMemberOut:
    if db.query(User).filter(User.email == payload.email).first():
        raise ConflictError("An account with this email already exists.")
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise ValidationError("Unknown role.")
    user = User(
        name=payload.name.strip(),
        email=payload.email,
        password_hash=hash_password(DEFAULT_TEMP_PASSWORD),
        role=UserRole.EMPLOYEE,
        title=payload.title or role.name,
        company_role_id=role.id,
        is_active=True,
        is_email_verified=True,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _member_out(user)


@router.patch("/{user_id}", response_model=TeamMemberOut, dependencies=[Depends(require_permission(MANAGE_TEAM))])
def update_member(
    user_id: str,
    payload: TeamUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> TeamMemberOut:
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise NotFoundError("Team member not found.")
    if target.id == actor.id and payload.is_active is False:
        raise ForbiddenError("You can't block your own account.")
    # Only EMPLOYEE accounts can be blocked or reassigned; admins/CEO are protected.
    if target.role != UserRole.EMPLOYEE and (payload.is_active is not None or payload.role_id is not None):
        raise ForbiddenError("Admin accounts can't be blocked or reassigned here.")

    if payload.name is not None:
        target.name = payload.name.strip()
    if payload.title is not None:
        target.title = payload.title
    if payload.role_id is not None:
        role = db.query(Role).filter(Role.id == payload.role_id).first()
        if not role:
            raise ValidationError("Unknown role.")
        target.company_role_id = role.id
    if payload.is_active is not None:
        target.is_active = payload.is_active
    db.commit()
    db.refresh(target)
    return _member_out(target)


@router.delete("/{user_id}", response_model=MessageResponse, dependencies=[Depends(require_permission(MANAGE_TEAM))])
def delete_member(
    user_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> MessageResponse:
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise NotFoundError("Team member not found.")
    if target.id == actor.id:
        raise ForbiddenError("You can't delete your own account.")
    if target.role != UserRole.EMPLOYEE:
        raise ForbiddenError("Admin accounts can't be deleted here.")
    db.delete(target)
    db.commit()
    return MessageResponse(message="Team member removed.")
