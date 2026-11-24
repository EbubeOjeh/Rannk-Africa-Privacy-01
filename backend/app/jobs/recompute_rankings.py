"""Recompute rankings asynchronously.

Today this is a thin wrapper that opens its own DB session and calls
``ranking_service.recompute_all``. When you wire up Celery it becomes a
``@celery_app.task`` with the same body.
"""
from __future__ import annotations

from app.core.logging import logger
from app.db.session import SessionLocal
from app.services import ranking_service


def recompute_rankings_job() -> dict:
    with SessionLocal() as db:
        try:
            result = ranking_service.recompute_all(db)
            logger.info("Background rankings recomputed: {r}", r=result)
            return result
        except Exception as exc:  # noqa: BLE001
            logger.exception("Background recompute failed: {exc}", exc=exc)
            raise
