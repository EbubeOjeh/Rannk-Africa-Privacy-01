"""Shared LLM provider client — the single swap point for RankAfrica's AI.

Every AI feature (project rubric scoring, integrity/plagiarism review,
opportunity %-match, and the free-text profile assessment) calls
``complete_json()`` here instead of importing a provider SDK directly, so the
active provider is decided in ONE place (``settings.AI_PROVIDER``).

Default provider is **OpenAI** (``gpt-4o-mini``); Anthropic Claude remains
selectable via ``AI_PROVIDER=anthropic``. Callers keep their own
fence-stripping + ``json.loads`` + graceful-degradation fallbacks — this module
only produces the raw model text (a JSON object) or raises :class:`AIError`.
"""
from __future__ import annotations

from app.core.config import settings
from app.core.logging import logger


class AIError(Exception):
    """Raised when an AI completion cannot be produced (disabled / no key /
    missing SDK / provider error). Callers catch this and fall back."""


def ai_configured() -> bool:
    """True when AI is enabled AND the active provider has an API key."""
    return bool(settings.AI_ENABLED and settings.ai_api_key)


def ai_engine_label() -> str:
    """The engine id persisted alongside AI-produced scores/flags. Falls back
    to a stable sentinel when AI is off so audit rows stay meaningful."""
    return settings.ai_model if ai_configured() else "disabled"


def complete_json(system: str, user: str, max_tokens: int = 600) -> str:
    """Return the raw model text (expected to be a single JSON object).

    Raises :class:`AIError` when AI is disabled, the provider key is missing,
    the SDK is not installed, or the provider call fails.
    """
    if not ai_configured():
        raise AIError("AI disabled or API key not configured.")
    provider = settings.ai_provider
    if provider == "anthropic":
        return _complete_anthropic(system, user, max_tokens)
    return _complete_openai(system, user, max_tokens)


def _complete_openai(system: str, user: str, max_tokens: int) -> str:
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:  # pragma: no cover - only when SDK absent
        raise AIError("openai package is not installed.") from exc

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model=settings.ai_model,
            max_tokens=max_tokens,
            temperature=0,
            # Native JSON mode — the model is constrained to emit a JSON object.
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
    except Exception as exc:  # noqa: BLE001 — surface as AIError for the caller
        logger.error("OpenAI completion failed: {exc}", exc=exc)
        raise AIError(str(exc)) from exc
    return (response.choices[0].message.content or "").strip()


def _complete_anthropic(system: str, user: str, max_tokens: int) -> str:
    try:
        from anthropic import Anthropic  # type: ignore
    except ImportError as exc:  # pragma: no cover - only when SDK absent
        raise AIError("anthropic package is not installed.") from exc

    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    try:
        response = client.messages.create(
            model=settings.ai_model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as exc:  # noqa: BLE001 — surface as AIError for the caller
        logger.error("Anthropic completion failed: {exc}", exc=exc)
        raise AIError(str(exc)) from exc
    text_blocks = [b.text for b in response.content if getattr(b, "type", "") == "text"]
    return "".join(text_blocks).strip()
