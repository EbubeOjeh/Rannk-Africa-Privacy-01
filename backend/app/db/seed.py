"""Seed initial reference data: super-admin, fields, universities, an active cycle,
sample students with achievements/projects.

Run with:  python -m app.db.seed
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.achievement import (
    ACHIEVEMENT_POINTS,
    Achievement,
    AchievementType,
    VerificationStatus,
)
from app.models.field import Field
from app.models.opportunity import Opportunity, OpportunityType
from app.models.project_submission import ProjectStatus, ProjectSubmission
from app.models.student import ApprovalStatus, Student
from app.models.submission_cycle import CycleStatus, SubmissionCycle
from app.models.university import SchoolApprovalStatus, University
from app.models.user import User, UserRole
from app.services import ranking_service
from app.services.field_mapping import CANONICAL_FIELDS
from app.utils.slug import slugify

# PRS §4 — the eight canonical fields (single source of truth lives in
# app.services.field_mapping so the seed + course auto-mapping never drift).
FIELDS = CANONICAL_FIELDS

UNIVERSITIES = [
    {"name": "Covenant University", "domain": "covenantuniversity.edu.ng", "city": "Ota", "state": "Ogun", "tier": 1, "institution_type": "university"},
    {"name": "University of Ibadan", "domain": "ui.edu.ng", "city": "Ibadan", "state": "Oyo", "tier": 1, "institution_type": "university"},
    {"name": "Ahmadu Bello University", "domain": "abu.edu.ng", "city": "Zaria", "state": "Kaduna", "tier": 1, "institution_type": "university"},
    {"name": "University of Lagos", "domain": "unilag.edu.ng", "city": "Lagos", "state": "Lagos", "tier": 1, "institution_type": "university"},
    {"name": "University of Port Harcourt", "domain": "uniport.edu.ng", "city": "Port Harcourt", "state": "Rivers", "tier": 2, "institution_type": "university"},
    {"name": "Lagos State University", "domain": "lasu.edu.ng", "city": "Lagos", "state": "Lagos", "tier": 2, "institution_type": "university"},
    {"name": "University of Ilorin", "domain": "unilorin.edu.ng", "city": "Ilorin", "state": "Kwara", "tier": 2, "institution_type": "university"},
    {"name": "University of Nigeria, Nsukka", "domain": "unn.edu.ng", "city": "Nsukka", "state": "Enugu", "tier": 1, "institution_type": "university"},
    {"name": "Obafemi Awolowo University", "domain": "oauife.edu.ng", "city": "Ile-Ife", "state": "Osun", "tier": 1, "institution_type": "university"},
    {"name": "Federal University of Technology, Akure", "domain": "futa.edu.ng", "city": "Akure", "state": "Ondo", "tier": 2, "institution_type": "university"},
    {"name": "Nnamdi Azikiwe University", "domain": "unizik.edu.ng", "city": "Awka", "state": "Anambra", "tier": 2, "institution_type": "university"},
    {"name": "University of Benin", "domain": "uniben.edu", "city": "Benin City", "state": "Edo", "tier": 2, "institution_type": "university"},
    {"name": "Babcock University", "domain": "babcock.edu.ng", "city": "Ilishan-Remo", "state": "Ogun", "tier": 1, "institution_type": "university"},
    {"name": "Yaba College of Technology", "domain": "yabatech.edu.ng", "city": "Lagos", "state": "Lagos", "tier": 1, "institution_type": "polytechnic"},
    {"name": "Federal Polytechnic, Ilaro", "domain": "federalpolyilaro.edu.ng", "city": "Ilaro", "state": "Ogun", "tier": 2, "institution_type": "polytechnic"},
    {"name": "Lagos State Polytechnic", "domain": "laspotech.edu.ng", "city": "Ikorodu", "state": "Lagos", "tier": 2, "institution_type": "polytechnic"},
]

FIRST_NAMES = [
    "Folake", "James", "Biodun", "Ifeoma", "Peter", "Chidi", "Lilian", "Nkechi",
    "Akinwale", "Quadri", "Ronke", "Adebayo", "Xena", "Chinedu", "Maryam",
    "Mercy", "Yetunde", "Yakubu", "Damilola", "Stella", "Dolapo", "Ngozi",
    "Kelechi", "Aisha", "Tunde", "Ibrahim", "Sade", "Emeka", "Funmi",
]
LAST_NAMES = [
    "Adeleke", "Adegoke", "Fatoke", "Chukwuma", "Olumide", "Onyekachi", "Obasi",
    "Onwueme", "Dosumu", "Animashaun", "Afolabi", "Ogunlesi", "Abubakar",
    "Igwe", "Suleiman", "Abiodun", "Olatunbosun", "Musa", "Fasuyi", "Aghimien",
    "Oyekan", "Okwudili", "Eze", "Bello", "Sanusi",
]

PROJECT_SEEDS = [
    {
        "title": "MediQueue — AI triage for understaffed clinics",
        "description": (
            "A mobile-first triage app for rural Nigerian clinics. Patients enter "
            "symptoms in pidgin; a fine-tuned model classifies severity and routes "
            "high-risk cases to the duty doctor first."
        ),
        "problem_statement": "Most rural clinics in Nigeria have 1 doctor per 5,000+ patients; manual triage delays critical cases.",
        "originality": 8, "technical_depth": 8, "problem_solving": 9, "innovation": 8,
    },
    {
        "title": "GreenGrid — distributed solar accounting for cooperatives",
        "description": (
            "Lets neighbours pool rooftop solar contributions onto a shared meter "
            "with per-household billing reconciled on-chain."
        ),
        "problem_statement": "Cooperative solar billing today is run on spreadsheets and disputes are rampant.",
        "originality": 7, "technical_depth": 9, "problem_solving": 8, "innovation": 8,
    },
    {
        "title": "Tutorly — peer tutor marketplace for 100-level students",
        "description": "Matches struggling first-years with vetted second/third-year tutors on a per-paper basis.",
        "problem_statement": "First-year dropout rates are highest in 100-level core papers; existing tutoring is informal.",
        "originality": 5, "technical_depth": 6, "problem_solving": 7, "innovation": 5,
    },
]


def reset_database() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def _ensure_super_admin(db: Session) -> User:
    user = db.query(User).filter(User.email == settings.SEED_SUPERADMIN_EMAIL.lower()).first()
    if user:
        return user
    user = User(
        name="Super Admin",
        email=settings.SEED_SUPERADMIN_EMAIL.lower(),
        password_hash=hash_password(settings.SEED_SUPERADMIN_PASSWORD),
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        is_email_verified=True,
    )
    db.add(user)
    db.flush()
    return user


def _seed_fields(db: Session) -> list[Field]:
    out: list[Field] = []
    for f in FIELDS:
        row = Field(
            name=f["name"],
            slug=f.get("slug") or slugify(f["name"]),
            description=f.get("description"),
            icon=f.get("icon"),
            color=f.get("color"),
        )
        db.add(row)
        out.append(row)
    db.flush()
    return out


def _seed_universities(db: Session) -> list[University]:
    out: list[University] = []
    for u in UNIVERSITIES:
        institution = u.get("institution_type", "university")
        grading_system = "4_point" if institution == "polytechnic" else "5_point"
        row = University(
            name=u["name"],
            slug=slugify(u["name"]),
            country="Nigeria",
            state=u["state"],
            city=u["city"],
            tier=u["tier"],
            domain=u.get("domain"),
            grading_system=grading_system,
            institution_type=institution,
            accreditation_type=(
                "Federal" if "Federal" in u["name"] or u["tier"] == 1 else "State"
            ),
            # Seeded institutions are well-known and approved out-of-the-box.
            approval_status=SchoolApprovalStatus.APPROVED,
            approved_at=datetime.now(timezone.utc),
            approval_notes="Pre-approved (seeded institution).",
        )
        db.add(row)
        out.append(row)
    db.flush()
    return out


def _seed_cycle(db: Session) -> SubmissionCycle:
    now = datetime.now(timezone.utc)
    cycle = SubmissionCycle(
        name="RankAfrica 2026",
        year=2026,
        submission_opens_at=now - timedelta(days=7),
        submission_closes_at=now + timedelta(weeks=5),
        review_ends_at=now + timedelta(weeks=7),
        status=CycleStatus.OPEN,
        max_students_per_school=15,
        description="Inaugural Nigerian tech-discipline ranking cycle.",
    )
    db.add(cycle)
    db.flush()
    return cycle


def _seed_students(
    db: Session,
    fields: list[Field],
    unis: list[University],
    cycle: SubmissionCycle,
) -> list[Student]:
    rnd = random.Random(42)
    students: list[Student] = []
    # Spec: max 15 students per school per cycle. Honour it in the seed too.
    for uni in unis:
        is_poly = uni.institution_type == "polytechnic"
        native_scale = 4.0 if is_poly else 5.0
        # Schools submit their TOP performers per spec; sample CGPAs accordingly.
        cgpa_range = (2.8, 4.0) if is_poly else (3.6, 4.95)
        for _ in range(rnd.randint(10, cycle.max_students_per_school)):
            first = rnd.choice(FIRST_NAMES)
            last = rnd.choice(LAST_NAMES)
            field = rnd.choice(fields)
            raw_gpa = round(rnd.uniform(*cgpa_range), 2)
            student = Student(
                full_name=f"{first} {last}",
                email=f"{first.lower()}.{last.lower()}@{uni.slug}.edu.ng",
                phone_number=f"+234 80{rnd.randint(10000000, 99999999)}",
                linkedin_url=f"https://linkedin.com/in/{first.lower()}-{last.lower()}",
                matric_number=f"{uni.slug[:3].upper()}/{rnd.randint(10000, 99999)}",
                university_id=uni.id,
                field_id=field.id,
                submission_cycle_id=cycle.id,
                academic_level=rnd.choice([300, 400, 500]),
                bio=(
                    f"{first} is a {field.name.lower()} student at {uni.name}, "
                    "focused on shipping production-ready software and giving back "
                    "to the local developer community."
                ),
                raw_gpa=raw_gpa,
                raw_cgpa=raw_gpa,
                gpa_scale=native_scale,
                credits_earned=rnd.randint(120, 200),
                avatar_url=None,
                approval_status=ApprovalStatus.APPROVED,
                is_publicly_visible=True,
                approved_at=datetime.now(timezone.utc),
            )
            db.add(student)
            students.append(student)
    db.flush()
    return students


def _seed_projects_and_achievements(db: Session, students: list[Student]) -> None:
    rnd = random.Random(1337)
    # Give roughly the top quartile pre-scored projects + a couple of achievements.
    for student in rnd.sample(students, k=max(1, len(students) // 3)):
        spec = rnd.choice(PROJECT_SEEDS)
        project = ProjectSubmission(
            student_id=student.id,
            title=spec["title"],
            description=spec["description"],
            problem_statement=spec["problem_statement"],
            originality=float(spec["originality"]),
            technical_depth=float(spec["technical_depth"]),
            problem_solving=float(spec["problem_solving"]),
            innovation=float(spec["innovation"]),
            total_score=float(
                spec["originality"] + spec["technical_depth"]
                + spec["problem_solving"] + spec["innovation"]
            ),
            status=ProjectStatus.MODERATED,
            ai_engine="seed",
            evaluated_at=datetime.now(timezone.utc),
            moderated_at=datetime.now(timezone.utc),
        )
        db.add(project)

    for student in rnd.sample(students, k=max(1, len(students) // 2)):
        types = rnd.sample(list(AchievementType), k=rnd.randint(1, 3))
        for t in types:
            db.add(
                Achievement(
                    student_id=student.id,
                    type=t,
                    points=ACHIEVEMENT_POINTS[t],
                    title=f"Sample {t.value.replace('_', ' ').title()}",
                    description="Seeded sample achievement for demo purposes.",
                    verification_status=VerificationStatus.VERIFIED,
                    verified_at=datetime.now(timezone.utc),
                )
            )
    db.flush()


def _seed_opportunities(db: Session, admin: User) -> None:
    """A small set of live opportunities, including the JEF Consulting-sponsored
    Toastmasters programme, so the Opportunities portal is populated in dev. The
    structure is deliberately a plain list so more can be added easily."""
    opportunities = [
        dict(
            type=OpportunityType.LEADERSHIP_PROGRAM,
            title="Toastmasters 1-Year Subscription",
            organization="JEF Consulting",
            description=(
                "A fully sponsored one-year Toastmasters membership, paid for by "
                "JEF Consulting, to help you build world-class public speaking and "
                "leadership skills."
            ),
            location="Abuja",
            requirements="Open to students based in Abuja.",
            is_featured=True,
        ),
        dict(
            type=OpportunityType.INTERNSHIP,
            title="Software Engineering Internship",
            organization="RankAfrica Partners",
            description="A three-month paid internship building products used across the continent.",
            location="Lagos",
            requirements="Final-year students in a technology discipline.",
        ),
        dict(
            type=OpportunityType.SCHOLARSHIP,
            title="Merit Scholarship for Top Performers",
            organization="RankAfrica Foundation",
            description="Tuition support for high-ranking students across all disciplines.",
            requirements="Open to students with a strong academic record.",
        ),
    ]
    for o in opportunities:
        db.add(Opportunity(posted_by_id=admin.id, is_active=True, **o))
    db.flush()


def run(reset: bool = True) -> None:
    configure_logging()
    if reset:
        logger.warning("Dropping + recreating all tables.")
        reset_database()

    with SessionLocal() as db:
        admin = _ensure_super_admin(db)
        fields = _seed_fields(db)
        unis = _seed_universities(db)
        cycle = _seed_cycle(db)
        students = _seed_students(db, fields, unis, cycle)
        _seed_projects_and_achievements(db, students)
        _seed_opportunities(db, admin)
        db.commit()
        ranking_service.recompute_all(db)
        logger.info("Seed complete.")


if __name__ == "__main__":
    run()
