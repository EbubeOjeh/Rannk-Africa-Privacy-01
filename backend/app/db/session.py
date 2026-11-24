"""SQLAlchemy session/engine setup — works with SQLite (dev) and Postgres (prod)."""
from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs: dict = {"pool_pre_ping": True, "future": True}
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # On serverless (Vercel) every invocation may be a fresh process, and we
    # connect through Supabase's transaction-mode pooler (port 6543). Holding
    # a SQLAlchemy-side pool there exhausts connections, so use NullPool and
    # let the pooler manage them. pool_pre_ping is incompatible with NullPool.
    _engine_kwargs["poolclass"] = NullPool
    _engine_kwargs.pop("pool_pre_ping", None)

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)


# SQLite ignores FK constraints by default; turn them on so ondelete=CASCADE works.
if _is_sqlite:
    @event.listens_for(Engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, _):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
