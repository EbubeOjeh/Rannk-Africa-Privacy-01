"""Reusable validation helpers.

Pydantic schemas in ``app/schemas`` cover the bulk of request validation. This
package holds cross-cutting validators that don't belong on a single schema —
e.g. file MIME/size validation, transcript row shape validation.
"""
from app.validators.files import validate_upload

__all__ = ["validate_upload"]
