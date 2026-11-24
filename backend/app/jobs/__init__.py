"""Background jobs.

Currently the recompute step runs synchronously inside the upload endpoint.
For larger datasets, move ``recompute_rankings_job`` onto Celery (already in
requirements.txt) or APScheduler. The job lives here so the rest of the app
imports a stable interface.
"""
from app.jobs.recompute_rankings import recompute_rankings_job

__all__ = ["recompute_rankings_job"]
