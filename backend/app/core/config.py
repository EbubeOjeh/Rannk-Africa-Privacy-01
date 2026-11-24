"""Application configuration loaded from environment variables."""
import json
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SEED_DEMO_STUDENTS: bool = False
    ENABLE_STUDENT_CLEANUP: bool = False
    STUDY_CONTACT: str = ""
    STUDY_RETENTION_NOTICE: str = ""

    APP_NAME: str = "RankAfrica"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "sqlite:///./rankafrica.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Comma-separated list (or JSON array) of allowed browser origins.
    # Kept as a plain string so it can be set in any platform's env UI
    # without the JSON-array quoting that pydantic would otherwise require.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Run create_all() + lightweight backfills on app startup. Safe for local
    # dev; in production (serverless) set this to false and run the one-time
    # `scripts/init_prod_db.py` instead so each cold start doesn't hit the DB.
    INIT_DB_ON_STARTUP: bool = True

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 25

    # --- Supabase Storage (production file uploads) ---
    # When SUPABASE_URL + SUPABASE_SERVICE_KEY are set, uploaded files
    # (avatars, project reports, evidence) are pushed to Supabase Storage and
    # a public URL is returned. When unset, files fall back to local disk
    # under UPLOAD_DIR (dev only — does NOT work on serverless hosts).
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_BUCKET: str = "uploads"

    EXIT_FEEDBACK_RECIPIENT: str = ""
    SMTP_USE_SSL: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "no-reply@rankafrica.org"
    # Optional extra recipient for admin notifications (new recruiter sign-ups,
    # etc.), on top of every super-admin account. Leave blank to notify only
    # the super-admins that exist in the database.
    ADMIN_NOTIFICATION_EMAIL: str = ""

    SEED_SUPERADMIN_EMAIL: str = "admin@rankafrica.org"
    SEED_SUPERADMIN_PASSWORD: str = "ChangeMe123!"
    AUTO_SEED: bool = True
    DEMO_PASSWORD: str = "DemoPrivacy2026!"

    # AI scorers (project rubric /40, profile assessment /60, integrity review,
    # opportunity %-match). When the active provider has no key OR AI_ENABLED is
    # false, AI scores stay at 0 / "pending" and callers fall back to their
    # deterministic heuristics until a key is configured.
    #
    # Provider is selected by AI_PROVIDER: "openai" (default) or "anthropic".
    # All AI calls go through app.services.ai_client, which reads the
    # provider-aware `ai_api_key` / `ai_model` helpers below.
    AI_ENABLED: bool = False
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    AI_PROJECT_MODEL: str = "claude-sonnet-4-6"  # model used when AI_PROVIDER=anthropic

    @property
    def ai_provider(self) -> str:
        """Normalised active provider ("openai" | "anthropic")."""
        return (self.AI_PROVIDER or "openai").strip().lower()

    @property
    def ai_api_key(self) -> str:
        """API key for the active provider."""
        return self.OPENAI_API_KEY if self.ai_provider == "openai" else self.ANTHROPIC_API_KEY

    @property
    def ai_model(self) -> str:
        """Model id for the active provider (also persisted as the engine label)."""
        return self.OPENAI_MODEL if self.ai_provider == "openai" else self.AI_PROJECT_MODEL

    @property
    def cors_origins(self) -> List[str]:
        """Parsed allow-list. Accepts a JSON array or a comma-separated string."""
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                return [str(o).strip() for o in json.loads(raw) if str(o).strip()]
            except json.JSONDecodeError:
                pass
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def supabase_storage_enabled(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_KEY)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
