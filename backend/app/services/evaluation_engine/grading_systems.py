"""Convert raw GPA on heterogeneous scales to a 0..1 ratio."""
from __future__ import annotations

SUPPORTED_SCALES: dict[str, float] = {
    "4_point": 4.0,
    "4.0": 4.0,
    "5_point": 5.0,
    "5.0": 5.0,
    "7_point": 7.0,
    "10_point": 10.0,
    "percentage": 100.0,
}


def gpa_to_ratio(gpa: float | None, scale: float | str | None = 4.0) -> float:
    """Map a raw GPA value to a [0, 1] ratio.

    ``scale`` may be a numeric maximum (e.g. ``4.0``, ``5.0``, ``100``) or one of
    the named scales in :data:`SUPPORTED_SCALES`.
    """
    if gpa is None:
        return 0.0
    if isinstance(scale, str):
        max_value = SUPPORTED_SCALES.get(scale.lower(), 4.0)
    else:
        max_value = float(scale or 4.0)
    if max_value <= 0:
        return 0.0
    return max(0.0, min(1.0, gpa / max_value))


def letter_to_points(grade: str, scale: float = 4.0) -> float:
    """Best-effort letter-grade → point conversion for common Nigerian scales."""
    if not grade:
        return 0.0
    g = grade.strip().upper()
    if scale >= 4.99:
        return {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "F": 0}.get(g[0], 0.0)
    return {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}.get(g[0], 0.0)
