"""Upload validation helpers."""
from __future__ import annotations

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationError

ALLOWED_TABULAR = {".csv", ".xls", ".xlsx"}
ALLOWED_PDF = {".pdf"}
ALLOWED_IMAGE = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
ALLOWED_DOC = {".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_VIDEO = {".mp4", ".mov", ".webm"}


def _extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


def validate_upload(
    file: UploadFile,
    *,
    allowed: set[str],
    max_mb: int | None = None,
) -> None:
    ext = _extension(file.filename)
    if ext not in allowed:
        raise ValidationError(
            f"Unsupported file type '{ext or 'unknown'}'. Allowed: {sorted(allowed)}"
        )
    if max_mb is None:
        max_mb = settings.MAX_UPLOAD_MB
    # ``file.size`` is populated for spooled multipart uploads
    if file.size is not None and file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"File exceeds {max_mb} MB limit.")
