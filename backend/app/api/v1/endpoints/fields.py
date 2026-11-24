"""Public field/discipline endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.field import Field
from app.models.student import Student
from app.schemas.field import FieldOut

router = APIRouter()


def _hydrate(f: Field, db: Session) -> FieldOut:
    from app.services.privacy import visible
    rows = [s for s in visible(db) if s.field_id == f.id]
    out = FieldOut.model_validate(f)
    out.student_count = len(rows)
    out.top_score = max((s.final_score for s in rows), default=0.0)
    return out


@router.get("", response_model=list[FieldOut])
def list_fields(db: Session = Depends(get_db)) -> list[FieldOut]:
    return [_hydrate(f, db) for f in db.query(Field).order_by(Field.name.asc()).all()]


@router.get("/{slug}", response_model=FieldOut)
def get_field(slug: str, db: Session = Depends(get_db)) -> FieldOut:
    f = db.query(Field).filter((Field.slug == slug) | (Field.id == slug)).first()
    if not f:
        raise NotFoundError("Field not found.")
    return _hydrate(f, db)
