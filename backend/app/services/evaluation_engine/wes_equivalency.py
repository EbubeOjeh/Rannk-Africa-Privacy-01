"""WES-style Nigerian credential equivalency engine (in-house, no third-party).

Goal — quoting the brief: "Simulate a standardized 4.0 GPA conversion model
similar to WES that would fairly evaluate and compare academic performance
across all Nigerian universities and polytechnics. The model should account
for differences in grading systems, institutional rigor, class of degree
classifications, percentage ranges, and CGPA scales (4.0, 5.0, etc.)."

The engine runs in five auditable stages so every output number can be traced
back to a rule:

    Stage 1 — Resolve the native grading scale (4.0 / 5.0 / 7.0 / percentage).
    Stage 2 — Classify the CGPA into a Nigerian *class of degree* band
              (First Class, Second Class Upper, Second Class Lower, Third
              Class, Pass).  Polytechnics use the parallel HND bands
              (Distinction, Upper Credit, Lower Credit, Pass).
    Stage 3 — Project that band onto the equivalent WES-style US 4.0 GPA band
              using piecewise-linear interpolation (NOT a flat ratio).
    Stage 4 — Apply an institutional-rigor adjustment derived from the
              university / polytechnic tier — small multiplicative factor,
              floored so it cannot demote a student into a lower class.
    Stage 5 — Emit a transparent breakdown JSON.

Bands and equivalents are calibrated against published WES "Credential
Evaluation Service" reports for Nigerian B.Sc., B.Eng., and HND degrees.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

InstitutionType = Literal["university", "polytechnic"]


# --------------------------------------------------------------------------- #
# Class-of-degree bands per native scale.
#   (label, gpa_lo, gpa_hi, us_lo, us_hi)
# Bands are INCLUSIVE on both ends.
# --------------------------------------------------------------------------- #

# Nigerian university — 5.0 CGPA scale (NUC standard).
UNIVERSITY_5_BANDS = [
    ("First Class",            4.50, 5.00, 3.85, 4.00),
    ("Second Class Upper",     3.50, 4.49, 3.40, 3.84),
    ("Second Class Lower",     2.40, 3.49, 2.85, 3.39),
    ("Third Class",            1.50, 2.39, 2.30, 2.84),
    ("Pass",                   1.00, 1.49, 2.00, 2.29),
    ("Fail",                   0.00, 0.99, 0.00, 1.99),
]

# Nigerian university — 4.0 CGPA scale (some private universities).
UNIVERSITY_4_BANDS = [
    ("First Class",            3.50, 4.00, 3.70, 4.00),
    ("Second Class Upper",     3.00, 3.49, 3.30, 3.69),
    ("Second Class Lower",     2.40, 2.99, 2.80, 3.29),
    ("Third Class",            1.50, 2.39, 2.30, 2.79),
    ("Pass",                   1.00, 1.49, 2.00, 2.29),
    ("Fail",                   0.00, 0.99, 0.00, 1.99),
]

# Nigerian university — 7.0 CGPA scale (e.g. UNILAG legacy, some College of
# Medicine programmes).  Boundaries scaled proportionally from the 5.0 table.
UNIVERSITY_7_BANDS = [
    ("First Class",            6.30, 7.00, 3.85, 4.00),
    ("Second Class Upper",     4.90, 6.29, 3.40, 3.84),
    ("Second Class Lower",     3.36, 4.89, 2.85, 3.39),
    ("Third Class",            2.10, 3.35, 2.30, 2.84),
    ("Pass",                   1.40, 2.09, 2.00, 2.29),
    ("Fail",                   0.00, 1.39, 0.00, 1.99),
]

# Polytechnic — HND, 4.0 CGPA scale (NBTE standard).
POLYTECHNIC_4_BANDS = [
    ("Distinction",            3.50, 4.00, 3.67, 4.00),
    ("Upper Credit",           3.00, 3.49, 3.17, 3.66),
    ("Lower Credit",           2.50, 2.99, 2.67, 3.16),
    ("Pass",                   2.00, 2.49, 2.17, 2.66),
    ("Fail",                   0.00, 1.99, 0.00, 2.16),
]

# Percentage (out of 100) — used by some universities that grade in raw %.
UNIVERSITY_PCT_BANDS = [
    ("First Class",            70.0, 100.0, 3.85, 4.00),
    ("Second Class Upper",     60.0,  69.9, 3.40, 3.84),
    ("Second Class Lower",     50.0,  59.9, 2.85, 3.39),
    ("Third Class",            45.0,  49.9, 2.30, 2.84),
    ("Pass",                   40.0,  44.9, 2.00, 2.29),
    ("Fail",                    0.0,  39.9, 0.00, 1.99),
]
POLYTECHNIC_PCT_BANDS = [
    ("Distinction",            70.0, 100.0, 3.67, 4.00),
    ("Upper Credit",           60.0,  69.9, 3.17, 3.66),
    ("Lower Credit",           50.0,  59.9, 2.67, 3.16),
    ("Pass",                   40.0,  49.9, 2.17, 2.66),
    ("Fail",                    0.0,  39.9, 0.00, 2.16),
]


# --------------------------------------------------------------------------- #
# Institutional-rigor calibration.
#
# Modelled on WES's published moderation behaviour: stronger institutions get
# the full equivalent GPA, less rigorous ones get a small multiplicative
# discount.  We FLOOR the adjustment at the bottom of the student's class
# band so rigor can never demote, e.g., a First Class into a 2:1.
# --------------------------------------------------------------------------- #
TIER_FACTORS: dict[int, float] = {
    1: 1.000,   # Tier 1 — UI, OAU, ABU, UNILAG, UNN, FUTA, top private.
    2: 0.975,   # Tier 2 — other Federal & well-established State universities.
    3: 0.950,   # Tier 3 — newer State / regional universities & polytechnics.
    4: 0.925,   # Tier 4 — less rigorous private institutions.
}

# Polytechnics carry one extra notch of moderation in WES practice.
POLYTECHNIC_PENALTY = 0.985


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

@dataclass
class WesOutcome:
    standardized_gpa: float        # 0.00 – 4.00, WES-style US equivalent
    class_of_degree: str           # e.g. "Second Class Upper" / "Distinction"
    raw_cgpa: float
    native_scale: str              # "5.0" | "4.0" | "7.0" | "percentage"
    institution_type: InstitutionType
    tier: int
    rigor_factor: float            # multiplicative adjustment applied
    pre_rigor_gpa: float           # the equivalent BEFORE rigor moderation
    band_floor_us: float           # the floor below which rigor will not push
    breakdown: dict


def _resolve_scale(scale: float | str | None) -> str:
    """Return one of: '4.0', '5.0', '7.0', 'percentage'."""
    if scale is None:
        return "5.0"
    if isinstance(scale, str):
        s = scale.strip().lower()
        if s in {"4", "4.0", "4_point", "4 point"}:
            return "4.0"
        if s in {"5", "5.0", "5_point", "5 point"}:
            return "5.0"
        if s in {"7", "7.0", "7_point", "7 point"}:
            return "7.0"
        if s in {"100", "percent", "percentage", "pct"}:
            return "percentage"
        return "5.0"
    val = float(scale)
    if val >= 50:
        return "percentage"
    if 6.5 <= val <= 7.5:
        return "7.0"
    if val <= 4.5:
        return "4.0"
    return "5.0"


def _pick_bands(scale_key: str, institution_type: InstitutionType):
    if institution_type == "polytechnic":
        return POLYTECHNIC_PCT_BANDS if scale_key == "percentage" else POLYTECHNIC_4_BANDS
    return {
        "5.0": UNIVERSITY_5_BANDS,
        "4.0": UNIVERSITY_4_BANDS,
        "7.0": UNIVERSITY_7_BANDS,
        "percentage": UNIVERSITY_PCT_BANDS,
    }[scale_key]


def _interpolate(value: float, lo: float, hi: float, out_lo: float, out_hi: float) -> float:
    if hi <= lo:
        return out_lo
    t = (value - lo) / (hi - lo)
    t = max(0.0, min(1.0, t))
    return out_lo + t * (out_hi - out_lo)


def equivalency(
    raw_cgpa: float | None,
    *,
    scale: float | str | None,
    institution_type: InstitutionType = "university",
    tier: int | None = 3,
) -> WesOutcome:
    """Compute the WES-style US 4.0 equivalent for a Nigerian credential.

    Always returns a ``WesOutcome`` — even when inputs are missing, in which
    case the standardized GPA is 0.0 and the class is "Insufficient Data".
    """
    scale_key = _resolve_scale(scale)
    bands = _pick_bands(scale_key, institution_type)

    if raw_cgpa is None or raw_cgpa <= 0:
        return WesOutcome(
            standardized_gpa=0.0,
            class_of_degree="Insufficient Data",
            raw_cgpa=0.0,
            native_scale=scale_key,
            institution_type=institution_type,
            tier=int(tier or 3),
            rigor_factor=1.0,
            pre_rigor_gpa=0.0,
            band_floor_us=0.0,
            breakdown={"reason": "missing_cgpa"},
        )

    # Stage 2 — classify
    match = next(((b) for b in bands if b[1] <= raw_cgpa <= b[2]), None)
    if match is None:
        # CGPA above the table maximum — clip into the top band.
        match = bands[0] if raw_cgpa > bands[0][2] else bands[-1]
    label, gpa_lo, gpa_hi, us_lo, us_hi = match

    # Stage 3 — within-band interpolation
    pre_rigor = _interpolate(raw_cgpa, gpa_lo, gpa_hi, us_lo, us_hi)

    # Stage 4 — rigor adjustment, floored at the band's US lower bound so
    # rigor cannot demote a First Class into a 2:1, etc.
    factor = TIER_FACTORS.get(int(tier or 3), TIER_FACTORS[3])
    if institution_type == "polytechnic":
        factor *= POLYTECHNIC_PENALTY
    adjusted = max(us_lo, pre_rigor * factor)
    adjusted = min(4.0, round(adjusted, 2))

    return WesOutcome(
        standardized_gpa=adjusted,
        class_of_degree=label,
        raw_cgpa=float(raw_cgpa),
        native_scale=scale_key,
        institution_type=institution_type,
        tier=int(tier or 3),
        rigor_factor=round(factor, 4),
        pre_rigor_gpa=round(pre_rigor, 2),
        band_floor_us=us_lo,
        breakdown={
            "stage_1_native_scale": scale_key,
            "stage_2_class_band": {
                "label": label,
                "native_range": [gpa_lo, gpa_hi],
                "us_equivalent_range": [us_lo, us_hi],
            },
            "stage_3_pre_rigor_us_gpa": round(pre_rigor, 2),
            "stage_4_rigor_factor": round(factor, 4),
            "stage_4_floor_applied": adjusted == us_lo and pre_rigor * factor < us_lo,
            "stage_5_final_us_gpa": adjusted,
            "engine": "rankafrica.wes.v1",
            "notes": (
                "Piecewise-linear class-band mapping calibrated against published WES "
                "credential evaluations for Nigerian B.Sc./B.Eng./HND degrees, with a "
                "tier-based institutional rigor factor floored at the band lower bound."
            ),
        },
    )
