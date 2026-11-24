"""Pipeline 1 — Academic Score (/40).

Now powered by the in-house WES-style equivalency engine (no third-party
service). The student's native CGPA is classified into a Nigerian class of
degree, mapped onto the WES-equivalent US 4.0 GPA, and then scaled to /40
via the spec's auditable formula:

    academic_score = standardized_us_gpa / 4.0 × 40

This means a First Class on a 5.0 scale and a First Class on a 4.0 scale
both land in the same WES-equivalent band, then convert identically to /40.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.services.evaluation_engine.wes_equivalency import (
    WesOutcome,
    equivalency,
)

ACADEMIC_MAX = 40.0

InstitutionType = Literal["university", "polytechnic"]


@dataclass
class AcademicOutcome:
    raw_cgpa: float | None
    gpa_scale: float
    standardized_gpa_4: float    # WES-equivalent US 4.0 GPA
    class_of_degree: str
    score: float                 # /40
    breakdown: dict


def academic_score(
    cgpa: float | None,
    scale: float | str | None = 4.0,
    *,
    institution_type: InstitutionType = "university",
    tier: int | None = 3,
) -> AcademicOutcome:
    """Compute the /40 academic score from a raw CGPA using the WES engine.

    ``institution_type`` and ``tier`` come from the student's University and
    decide which class-band table and rigor adjustment to apply.
    """
    wes: WesOutcome = equivalency(
        cgpa,
        scale=scale,
        institution_type=institution_type,
        tier=tier,
    )

    score = round(wes.standardized_gpa / 4.0 * ACADEMIC_MAX, 2)

    try:
        gpa_scale_val = float(scale) if scale is not None else 5.0
    except (TypeError, ValueError):
        gpa_scale_val = 5.0

    return AcademicOutcome(
        raw_cgpa=wes.raw_cgpa or None,
        gpa_scale=gpa_scale_val,
        standardized_gpa_4=wes.standardized_gpa,
        class_of_degree=wes.class_of_degree,
        score=score,
        breakdown={
            "raw_cgpa": cgpa,
            "native_scale_input": scale,
            "wes_equivalency": wes.breakdown,
            "standardized_us_gpa": wes.standardized_gpa,
            "class_of_degree": wes.class_of_degree,
            "formula": "(standardized_us_gpa / 4.0) * 40",
            "academic_score_out_of_40": score,
        },
    )
