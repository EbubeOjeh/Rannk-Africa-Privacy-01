"""Vercel serverless entrypoint.

Vercel's Python runtime serves the ASGI application exposed as ``app`` here.
All routes are forwarded to this function via ``vercel.json``.
"""
from app.main import app  # noqa: F401  (re-exported for the Vercel runtime)
