"""University CRUD + listing."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin, require_university_admin
from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import get_db
from app.models.department import Department
from app.models.field import Field
from app.models.university import University
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.university import UniversityCreate, UniversityOut, UniversityUpdate
from app.utils.slug import slugify

router = APIRouter()


def _hydrate(u: University, db: Session) -> UniversityOut:
    tags = (
        db.query(Field.name)
        .join(Department, Department.field_id == Field.id)
        .filter(Department.university_id == u.id)
        .distinct()
        .all()
    )
    out = UniversityOut.model_validate(u)
    from app.services.privacy import visible
    rows = [s for s in visible(db) if s.university_id == u.id]
    out.student_count = len(rows)
    out.avg_score = sum(s.final_score for s in rows)/len(rows) if rows else 0.0
    out.top_score = max((s.final_score for s in rows), default=0.0)
    out.elite_student_count = sum(s.final_score >= 80 for s in rows)
    out.overall_rank = None
    out.field_tags = [t[0] for t in tags]
    return out


@router.get("", response_model=Page[UniversityOut])
def list_universities(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    country: str | None = None,
):
    query = db.query(University)
    if q:
        query = query.filter(University.name.ilike(f"%{q}%"))
    if country:
        query = query.filter(University.country == country)

    total = query.count()
    rows = (
        query.order_by(University.overall_rank.asc().nullslast(), University.avg_score.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [_hydrate(r, db) for r in rows]
    return Page[UniversityOut](
        items=items,
        meta=PageMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=max(1, (total + page_size - 1) // page_size),
        ),
    )


@router.get("/{slug}", response_model=UniversityOut)
def get_university(slug: str, db: Session = Depends(get_db)) -> UniversityOut:
    u = db.query(University).filter((University.slug == slug) | (University.id == slug)).first()
    if not u:
        raise NotFoundError("University not found.")
    return _hydrate(u, db)


@router.post(
    "",
    response_model=UniversityOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_super_admin)],
)
def create_university(payload: UniversityCreate, db: Session = Depends(get_db)) -> UniversityOut:
    slug = slugify(payload.name)
    if db.query(University).filter((University.slug == slug) | (University.name == payload.name)).first():
        raise ConflictError("University already exists.")
    u = University(**payload.model_dump(), slug=slug)
    db.add(u)
    db.commit()
    db.refresh(u)
    return _hydrate(u, db)


@router.patch(
    "/{university_id}",
    response_model=UniversityOut,
    dependencies=[Depends(require_university_admin)],
)
def update_university(
    university_id: str, payload: UniversityUpdate, db: Session = Depends(get_db)
) -> UniversityOut:
    u = db.query(University).filter(University.id == university_id).first()
    if not u:
        raise NotFoundError("University not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(u, k, v)
    db.commit()
    db.refresh(u)
    return _hydrate(u, db)


@router.delete(
    "/{university_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_super_admin)],
)
def delete_university(university_id: str, db: Session = Depends(get_db)) -> MessageResponse:
    u = db.query(University).filter(University.id == university_id).first()
    if not u:
        raise HTTPException(404)
    db.delete(u)
    db.commit()
    return MessageResponse(message="University deleted.")
