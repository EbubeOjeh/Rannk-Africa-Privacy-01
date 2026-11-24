"""Public ranking endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user_optional, require_super_admin
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.field import Field
from app.models.ranking import RankingSnapshot
from app.models.student import Student
from app.models.university import University
from app.models.user import SCHOOL_ADMIN_ROLES, User, UserRole
from app.schemas.ranking import (
    SeasonLeaderboard,
    SeasonOut,
    SeasonPublishIn,
    StudentLeaderboard,
    UniversityLeaderboard,
)
from app.schemas.student import StudentRow
from app.schemas.university import UniversityOut
from app.services import ranking_service, settings_service

router = APIRouter()

SEASON_SCOPE = "season"

# Staff who may preview rankings even before they are publicly released.
_PREVIEW_ROLES = (UserRole.SUPER_ADMIN, UserRole.EMPLOYEE, UserRole.EVALUATOR, *SCHOOL_ADMIN_ROLES)


def _can_preview(viewer: User | None) -> bool:
    return viewer is not None and viewer.role in _PREVIEW_ROLES


def _student_row(s: Student) -> StudentRow:
    return StudentRow(
        id=s.id,
        full_name=s.full_name,
        avatar_url=s.avatar_url,
        university_id=s.university_id,
        university_name=s.university.name if s.university else "",
        university_state=s.university.state if s.university else None,
        institution_type=(s.university.institution_type if s.university else None),
        field_id=s.field_id,
        field_name=s.field.name if s.field else None,
        field_slug=s.field.slug if s.field else None,
        field_color=s.field.color if s.field else None,
        academic_level=s.academic_level,
        academic_score=s.academic_score,
        project_score=s.project_score,
        achievement_score=s.achievement_score,
        profile_score=s.profile_score,
        final_score=s.final_score,
        standardized_gpa_4=s.standardized_gpa_4,
        class_of_degree=s.class_of_degree,
        standardized_score=s.final_score,
        overall_rank=s.overall_rank,
    )


@router.get("/students", response_model=StudentLeaderboard)
def student_leaderboard(
    db: Session = Depends(get_db),
    scope: str = Query("global", pattern="^(global|university|field|department|country|state)$"),
    scope_key: str | None = None,
    state: str | None = None,
    min_score: float | None = Query(None, ge=0, le=100),
    max_score: float | None = Query(None, ge=0, le=100),
    include_unpublished: bool = False,
    limit: int = Query(80, ge=1, le=500),
    offset: int = 0,
    sort: str = Query("score", pattern="^(score|name)$"),
    viewer: User | None = Depends(get_current_user_optional),
):
    """The public leaderboard. By default only PUBLICLY VISIBLE students show.

    Rankings are hidden entirely until an admin releases them (after the
    registration period closes). Staff may preview beforehand.

    ``include_unpublished=true`` (to see pending submissions) is honoured only
    for staff previews and ignored for public callers.
    """
    preview = _can_preview(viewer)

    # Hide everything until rankings are released — unless a staff member previews.
    if not preview and not settings_service.is_rankings_released(db):
        return StudentLeaderboard(scope=scope, scope_key=scope_key, total=0, rows=[])

    # The unpublished-preview bypass is staff-only; ignore it for the public.
    if include_unpublished and not preview:
        include_unpublished = False

    query = db.query(Student).options(joinedload(Student.university), joinedload(Student.field))

    if not include_unpublished:
        query = query.filter(Student.is_publicly_visible.is_(True))

    if scope == "university" and scope_key:
        query = query.filter(Student.university_id == scope_key)
    elif scope == "field" and scope_key:
        query = query.join(Field, Student.field_id == Field.id).filter(
            (Field.id == scope_key) | (Field.slug == scope_key)
        )
    elif scope == "department" and scope_key:
        query = query.filter(Student.department_id == scope_key)
    elif scope == "country" and scope_key:
        query = query.join(Student.university).filter(University.country == scope_key)
    elif scope == "state" and scope_key:
        query = query.join(Student.university).filter(University.state == scope_key)

    if state and scope != "state":
        query = query.join(Student.university).filter(University.state == state)
    if min_score is not None:
        query = query.filter(Student.final_score >= min_score)
    if max_score is not None:
        query = query.filter(Student.final_score <= max_score)

    total = query.count()
    # The rank badge is the stored `overall_rank`, so the row order has to agree
    # with it or the column reads as scrambled (2, 1, 4, 3) whenever scores tie.
    # The trailing `id` makes the order total, which offset pagination needs to
    # avoid dropping or repeating rows. Mirrors students.py's listing.
    if sort == "name":
        order = (Student.full_name.asc(), Student.id.asc())
    else:
        order = (
            Student.final_score.desc(),
            Student.overall_rank.asc().nullslast(),
            Student.id.asc(),
        )
    rows = query.order_by(*order).offset(offset).limit(limit).all()

    return StudentLeaderboard(
        scope=scope,
        scope_key=scope_key,
        total=total,
        rows=[_student_row(s) for s in rows],
    )


@router.get("/universities", response_model=UniversityLeaderboard)
def university_leaderboard(
    db: Session = Depends(get_db),
    state: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = 0,
    viewer: User | None = Depends(get_current_user_optional),
):
    # University rankings are derived from student scores, so they stay hidden
    # until rankings are released (staff may preview).
    if not _can_preview(viewer) and not settings_service.is_rankings_released(db):
        return UniversityLeaderboard(total=0, rows=[])

    query = db.query(University)
    if state:
        query = query.filter(University.state == state)
    total = query.count()
    rows = (
        query.order_by(University.overall_rank.asc().nullslast(), University.avg_score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return UniversityLeaderboard(
        total=total,
        rows=[UniversityOut.model_validate(r) for r in rows],
    )


@router.get("/universities/by-field")
def university_field_rankings(
    field_key: str = Query(..., description="Field id or slug, e.g. 'technology'"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_current_user_optional),
) -> dict:
    """PRS §8 — per-field university ranking (e.g. Technology University Rankings),
    ranked by publicly-visible students' average score within that field."""
    if not _can_preview(viewer) and not settings_service.is_rankings_released(db):
        return {"field": field_key, "rows": []}
    return {
        "field": field_key,
        "rows": ranking_service.university_field_leaderboard(db, field_key, limit),
    }


@router.post("/recompute", dependencies=[Depends(require_super_admin)])
def trigger_recompute(db: Session = Depends(get_db)) -> dict:
    return ranking_service.recompute_all(db)


# --------------------------------------------------------------------------- #
# Historical ranking archive — frozen "seasons"
# --------------------------------------------------------------------------- #

@router.post("/seasons/publish", response_model=SeasonOut, dependencies=[Depends(require_super_admin)])
def publish_season(payload: SeasonPublishIn, db: Session = Depends(get_db)) -> SeasonOut:
    """Freeze the current public leaderboard as a named season (e.g. "2025/26").

    Re-publishing the same label refreshes that season; other seasons are never
    touched, so historical records are preserved permanently.
    """
    ranking_service.recompute_all(db)
    students = (
        db.query(Student)
        .options(joinedload(Student.university), joinedload(Student.field))
        .filter(Student.is_publicly_visible.is_(True))
        # Same total ordering as the live leaderboard — a frozen season would
        # otherwise archive the scrambled order permanently.
        .order_by(
            Student.final_score.desc(),
            Student.overall_rank.asc().nullslast(),
            Student.id.asc(),
        )
        .all()
    )
    rows = [_student_row(s).model_dump() for s in students]
    label = payload.label.strip()

    snap = (
        db.query(RankingSnapshot)
        .filter(RankingSnapshot.scope == SEASON_SCOPE, RankingSnapshot.scope_key == label)
        .first()
    )
    if snap is None:
        snap = RankingSnapshot(scope=SEASON_SCOPE, scope_key=label)
        db.add(snap)
    snap.total_entities = len(rows)
    snap.payload = rows
    db.commit()
    db.refresh(snap)
    return SeasonOut(label=label, total=snap.total_entities, published_at=snap.updated_at)


@router.get("/seasons", response_model=list[SeasonOut])
def list_seasons(db: Session = Depends(get_db)) -> list[SeasonOut]:
    snaps = (
        db.query(RankingSnapshot)
        .filter(RankingSnapshot.scope == SEASON_SCOPE)
        .order_by(RankingSnapshot.scope_key.desc())
        .all()
    )
    return [SeasonOut(label=s.scope_key, total=s.total_entities, published_at=s.updated_at) for s in snaps]


@router.get("/season", response_model=SeasonLeaderboard)
def get_season(label: str = Query(...), db: Session = Depends(get_db)) -> SeasonLeaderboard:
    snap = (
        db.query(RankingSnapshot)
        .filter(RankingSnapshot.scope == SEASON_SCOPE, RankingSnapshot.scope_key == label)
        .first()
    )
    if not snap:
        raise NotFoundError("Season not found.")
    rows = [StudentRow.model_validate(r) for r in (snap.payload or [])]
    return SeasonLeaderboard(label=snap.scope_key, total=snap.total_entities, published_at=snap.updated_at, rows=rows)
