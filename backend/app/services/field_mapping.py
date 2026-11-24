"""Canonical 8 academic fields + automatic course→field mapping (PRS §4).

The PRS replaces the old tech-only field list with exactly eight disciplines and
requires that a student's *chosen course/degree* be mapped automatically to one
of them. This module is the single source of truth for both:

  * ``CANONICAL_FIELDS`` — the 8 fields (name, slug, icon, colour, description)
    consumed by the seed + the field auto-provisioner.
  * ``map_course_to_field(course)`` — keyword resolver returning a field slug.

Keep this list and the homepage field cards in sync.
"""
from __future__ import annotations

# --- The canonical fields (Music deferred — see note in CANONICAL_FIELDS) ----
LAW = "law"
TECHNOLOGY = "technology"
MEDICAL_SCIENCES = "medical-sciences"
ENGINEERING = "engineering"
ARCHITECTURE = "architecture"
MUSIC = "music"
BUSINESS = "business"
MEDIA_COMMUNICATIONS = "media-communications"

CANONICAL_FIELDS: list[dict[str, str]] = [
    {"slug": LAW, "name": "Law", "icon": "scale", "color": "#7c2d12",
     "description": "Law, legal studies and jurisprudence."},
    {"slug": TECHNOLOGY, "name": "Technology", "icon": "cpu", "color": "#1A3D2B",
     "description": "Computing, software, data, AI and emerging technology."},
    {"slug": MEDICAL_SCIENCES, "name": "Medical Sciences", "icon": "heart-pulse", "color": "#b91c1c",
     "description": "Medicine, nursing, pharmacy and allied health sciences."},
    {"slug": ENGINEERING, "name": "Engineering", "icon": "wrench", "color": "#3a6a4b",
     "description": "Civil, mechanical, electrical, chemical and other engineering."},
    {"slug": ARCHITECTURE, "name": "Architecture", "icon": "ruler", "color": "#a05a1f",
     "description": "Architecture, design and the built environment."},
    # NOTE: Music is intentionally deferred to a future update — the MUSIC slug +
    # its scoring code are kept (dormant) so it can be re-added by simply
    # restoring this entry. Music courses currently map to Media & Communications.
    {"slug": BUSINESS, "name": "Business", "icon": "briefcase", "color": "#C47C2B",
     "description": "Business, accounting, finance, economics and management."},
    {"slug": MEDIA_COMMUNICATIONS, "name": "Media & Communications", "icon": "megaphone", "color": "#0e7490",
     "description": "Journalism, mass communication, media and PR."},
]

FIELD_SLUGS: tuple[str, ...] = tuple(f["slug"] for f in CANONICAL_FIELDS)
FIELD_NAME_BY_SLUG: dict[str, str] = {f["slug"]: f["name"] for f in CANONICAL_FIELDS}

DEFAULT_FIELD = TECHNOLOGY

# --- Course → field keyword resolver ----------------------------------------
# Ordered list of (keyword, field_slug). The FIRST keyword found in the
# (lower-cased) course string wins, so put more specific terms before generic
# ones (e.g. "biomedical engineering" before "engineering").
_COURSE_KEYWORDS: list[tuple[str, str]] = [
    # Law
    ("law", LAW), ("legal", LAW), ("jurisprudence", LAW),
    # Medical sciences (before "science"/"engineering" generics)
    ("biomedical engineering", ENGINEERING),
    ("medicine", MEDICAL_SCIENCES), ("medical", MEDICAL_SCIENCES), ("surgery", MEDICAL_SCIENCES),
    ("mbbs", MEDICAL_SCIENCES), ("nursing", MEDICAL_SCIENCES), ("pharmacy", MEDICAL_SCIENCES),
    ("pharmacology", MEDICAL_SCIENCES), ("physiology", MEDICAL_SCIENCES), ("anatomy", MEDICAL_SCIENCES),
    ("dentistry", MEDICAL_SCIENCES), ("dental", MEDICAL_SCIENCES), ("radiography", MEDICAL_SCIENCES),
    ("physiotherapy", MEDICAL_SCIENCES), ("optometry", MEDICAL_SCIENCES), ("nutrition", MEDICAL_SCIENCES),
    ("public health", MEDICAL_SCIENCES), ("biochemistry", MEDICAL_SCIENCES), ("microbiology", MEDICAL_SCIENCES),
    ("veterinary", MEDICAL_SCIENCES),
    # Architecture (before generic engineering/design)
    ("architecture", ARCHITECTURE), ("architectural", ARCHITECTURE),
    ("urban", ARCHITECTURE), ("quantity survey", ARCHITECTURE), ("building tech", ARCHITECTURE),
    ("estate management", BUSINESS),
    # Engineering
    ("software engineering", TECHNOLOGY),
    ("engineering", ENGINEERING), ("mechatronics", ENGINEERING), ("metallurg", ENGINEERING),
    ("petroleum", ENGINEERING), ("aeronautic", ENGINEERING),
    # Technology / computing
    ("computer science", TECHNOLOGY), ("computer", TECHNOLOGY), ("software", TECHNOLOGY),
    ("information technology", TECHNOLOGY), ("information system", TECHNOLOGY),
    ("data science", TECHNOLOGY), ("cyber", TECHNOLOGY), ("artificial intelligence", TECHNOLOGY),
    ("machine learning", TECHNOLOGY), ("informatics", TECHNOLOGY), ("computing", TECHNOLOGY),
    # Music (discipline deferred — map to Media & Communications for now)
    ("music", MEDIA_COMMUNICATIONS), ("performing arts", MEDIA_COMMUNICATIONS),
    ("musicology", MEDIA_COMMUNICATIONS),
    # Media & communications
    ("journalism", MEDIA_COMMUNICATIONS), ("mass communication", MEDIA_COMMUNICATIONS),
    ("mass comm", MEDIA_COMMUNICATIONS), ("media", MEDIA_COMMUNICATIONS),
    ("communication", MEDIA_COMMUNICATIONS), ("public relations", MEDIA_COMMUNICATIONS),
    ("broadcasting", MEDIA_COMMUNICATIONS), ("film", MEDIA_COMMUNICATIONS),
    ("theatre arts", MEDIA_COMMUNICATIONS), ("theater arts", MEDIA_COMMUNICATIONS),
    # Business
    ("accounting", BUSINESS), ("accountancy", BUSINESS), ("finance", BUSINESS),
    ("banking", BUSINESS), ("economics", BUSINESS), ("business", BUSINESS),
    ("marketing", BUSINESS), ("management", BUSINESS), ("entrepreneur", BUSINESS),
    ("actuarial", BUSINESS), ("insurance", BUSINESS), ("commerce", BUSINESS),
    ("administration", BUSINESS), ("procurement", BUSINESS), ("logistics", BUSINESS),
]


def map_course_to_field(course: str | None) -> str:
    """Map a free-text degree/course name to one of the canonical field slugs.

    Falls back to :data:`DEFAULT_FIELD` (Technology) when nothing matches, so a
    student always lands in a field. The match is substring-based and
    case-insensitive; the keyword order above resolves ambiguity.
    """
    if not course:
        return DEFAULT_FIELD
    needle = course.strip().lower()
    for keyword, slug in _COURSE_KEYWORDS:
        if keyword in needle:
            return slug
    return DEFAULT_FIELD
