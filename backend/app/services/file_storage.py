"""Storage for uploaded artifacts (avatars, evidence, project files).

Two backends, selected automatically:

* **Supabase Storage** (production) — used when ``SUPABASE_URL`` and
  ``SUPABASE_SERVICE_KEY`` are configured. Files are uploaded to the
  ``SUPABASE_BUCKET`` bucket and an absolute public URL is returned. This is
  the path that works on serverless hosts (Vercel), whose filesystem is
  read-only outside ``/tmp``.

* **Local disk** (development) — used when Supabase is not configured. Files
  are written under ``settings.UPLOAD_DIR`` and a relative ``/uploads/...``
  URL is returned; the FastAPI app mounts that directory so browsers can
  fetch it.

Callers don't care which backend is active — ``save_upload`` returns a URL
either way.
"""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationError

PUBLIC_PREFIX = "/uploads"


def _safe_name(filename: str) -> str:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return f"{uuid4().hex}{ext}"


def _save_to_supabase(data: bytes, *, subdir: str, filename: str, content_type: str) -> str:
    object_path = f"{subdir}/{filename}"
    base = settings.SUPABASE_URL.rstrip("/")
    upload_url = f"{base}/storage/v1/object/{settings.SUPABASE_BUCKET}/{object_path}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Content-Type": content_type or "application/octet-stream",
        # Overwrite if an object with the same (random) name somehow exists.
        "x-upsert": "true",
    }
    try:
        resp = httpx.post(upload_url, content=data, headers=headers, timeout=30.0)
    except httpx.HTTPError as exc:  # network / DNS / timeout
        raise ValidationError(f"Upload to storage failed: {exc}") from exc
    if resp.status_code not in (200, 201):
        raise ValidationError(
            f"Upload to storage failed ({resp.status_code}): {resp.text[:300]}"
        )
    return f"{base}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{object_path}"


def _save_to_disk(data: bytes, *, subdir: str, filename: str) -> str:
    base = Path(settings.UPLOAD_DIR) / subdir
    base.mkdir(parents=True, exist_ok=True)
    (base / filename).write_bytes(data)
    return f"{PUBLIC_PREFIX}/{subdir}/{filename}"


def save_upload(file: UploadFile, *, subdir: str) -> str:
    if not file.filename:
        raise ValidationError("Missing filename.")

    filename = _safe_name(file.filename)
    file.file.seek(0)
    data = file.file.read()

    if settings.supabase_storage_enabled:
        raise ValidationError('Public Supabase storage is disabled for this privacy prototype. Use the protected persistent local upload directory.')
        return _save_to_supabase(
            data,
            subdir=subdir,
            filename=filename,
            content_type=file.content_type or "application/octet-stream",
        )
    return _save_to_disk(data, subdir=subdir, filename=filename)


def save_bytes(data: bytes, *, subdir: str, filename: str, content_type: str = "application/octet-stream") -> str:
    """Persist raw bytes (already read from an upload) and return a URL.

    Uses Supabase Storage when configured (works on serverless), else local
    disk in dev. Used by the transcript endpoints, which read the file into
    memory before parsing.
    """
    safe = _safe_name(filename or "upload.dat")
    if settings.supabase_storage_enabled:
        raise ValidationError('Public Supabase storage is disabled for this privacy prototype. Use the protected persistent local upload directory.')
        return _save_to_supabase(data, subdir=subdir, filename=safe, content_type=content_type)
    return _save_to_disk(data, subdir=subdir, filename=safe)
