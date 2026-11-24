"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, logger
from app.db.init_db import init_db
from app.middleware.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    # Only touch the local filesystem when uploads are stored on disk (dev).
    # On serverless hosts the FS is read-only outside /tmp, so we skip this
    # when Supabase Storage is configured.
    if not settings.supabase_storage_enabled:
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    if settings.INIT_DB_ON_STARTUP:
        try:
            init_db()
        except Exception as exc:  # noqa: BLE001
            logger.error("init_db failed: {exc}", exc=exc)
            raise
    logger.info("{name} started in {env} mode", name=settings.APP_NAME, env=settings.APP_ENV)
    yield
    logger.info("Shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    register_exception_handlers(app)

    # Never expose the complete upload directory as a public static mount.
    from app.api.deps import get_current_user_optional
    from app.db.session import get_db
    from app.models.student import Student
    from app.services import privacy
    from sqlalchemy.orm import Session

    @app.get('/uploads/{file_path:path}')
    def protected_upload(file_path: str, db: Session = Depends(get_db), viewer=Depends(get_current_user_optional)):
        root = Path(settings.UPLOAD_DIR).resolve()
        target = (root / file_path).resolve()
        if root not in target.parents or not target.is_file():
            raise HTTPException(404)
        url = '/uploads/' + file_path
        for student in db.query(Student).all():
            owner = bool(viewer and student.user_id == viewer.id)
            if owner and student.id in file_path.split('/'):
                return FileResponse(target, headers={'Cache-Control':'no-store'})
            # Public photo URLs are readable only while the public photo choice
            # is saved and currently eligible. Private files need owner auth.
            if student.avatar_url == url:
                shared = privacy.disclose(db, student, 'public')
                if shared and shared.get('avatar_url') == url:
                    return FileResponse(target, headers={'Cache-Control':'no-store'})
        # A retained application can authorize an uploaded photo independently
        # of discovery withdrawal, but only for its owner or current recipient.
        if viewer:
            from app.models.privacy import ApplicationDisclosure
            from app.models.user import UserRole, UserApprovalStatus
            for disclosure in db.query(ApplicationDisclosure).all():
                if disclosure.snapshot.get('avatar_url') != url:
                    continue
                student = db.get(Student, disclosure.student_id)
                owner = student and student.user_id == viewer.id
                recipient = (disclosure.recipient_id == viewer.id and viewer.role == UserRole.EMPLOYER
                             and viewer.approval_status == UserApprovalStatus.APPROVED)
                if owner or recipient:
                    return FileResponse(target, headers={'Cache-Control':'no-store'})
            for student in db.query(Student).all():
                shared = privacy.disclose(db, student, 'recruiter', viewer)
                if shared and shared.get('avatar_url') == url:
                    return FileResponse(target, headers={'Cache-Control':'no-store'})
        raise HTTPException(404)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok", "service": settings.APP_NAME}

    frontend = Path(__file__).resolve().parents[2] / 'frontend_dist'
    if frontend.is_dir():
        if (frontend / 'assets').is_dir():
            app.mount('/assets', StaticFiles(directory=str(frontend / 'assets')), name='assets')
        @app.get('/{path:path}')
        def frontend_page(path: str):
            if path.startswith(('api/', 'uploads/')):
                raise HTTPException(404)
            candidate = (frontend / path).resolve()
            if frontend.resolve() in candidate.parents and candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(frontend / 'index.html')
    return app


app = create_app()
