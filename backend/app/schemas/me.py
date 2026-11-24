"""Student self-service (profile builder + dashboard) schemas — PRS §9, §11."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.student import ApprovalStatus
from app.schemas.achievement import AchievementOut
from app.schemas.competition import CompetitionOut
from app.schemas.experience import ExperienceOut
from app.schemas.leadership import LeadershipOut
from app.schemas.project import ProjectSubmissionOut
from app.schemas.research import ResearchOut


class StudentMeUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=180)
    bio: str | None = Field(default=None, max_length=1600)
    # Free-text "Achievements & Profile Assessment" (non-Technology/Music fields);
    # AI-scored /60. Saving it re-scores the student's profile.
    profile_statement: str | None = Field(default=None, max_length=8000)
    gender: str | None = None
    phone_number: str | None = None
    whatsapp_number: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    behance_url: str | None = None
    portfolio_url: str | None = None
    google_scholar_url: str | None = None
    music_url: str | None = None
    course: str | None = None          # re-maps field automatically
    faculty: str | None = None
    department_id: str | None = None
    academic_level: int | None = None
    year_of_study: int | None = None
    skills: list[str] | None = None
    languages: list[str] | None = None
    raw_cgpa: float | None = None
    raw_gpa: float | None = None
    gpa_scale: float | None = None
    credits_earned: int | None = None


class BadgeOut(BaseModel):
    badge_key: str
    label: str
    emoji: str
    is_auto: bool


class ScoreComponents(BaseModel):
    # "project" (Technology/Music: Academic 40 + Project 40 + Achievements 20)
    # or "profile" (other fields: Academic 40 + Profile Assessment 60).
    model: str = "project"
    academic: float = 0.0
    project: float = 0.0
    achievement: float = 0.0   # /20 for the project model
    profile: float = 0.0       # /60 for the profile model
    # Legacy sub-dimensions (kept for back-compat; 0 under engine v3).
    research: float = 0.0
    leadership: float = 0.0
    experience: float = 0.0
    competition: float = 0.0
    final: float = 0.0
    weights: dict[str, float] = {}


class StudentMeOut(BaseModel):
    id: str
    user_id: str | None = None
    full_name: str
    email: str | None = None
    avatar_url: str | None = None
    resume_url: str | None = None
    transcript_url: str | None = None
    bio: str | None = None
    profile_statement: str | None = None
    profile_score: float = 0.0
    gender: str | None = None

    university_id: str
    university_name: str | None = None
    faculty: str | None = None
    department_id: str | None = None
    course: str | None = None
    field_id: str | None = None
    field_name: str | None = None
    field_slug: str | None = None
    academic_level: int | None = None
    year_of_study: int | None = None

    phone_number: str | None = None
    whatsapp_number: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    behance_url: str | None = None
    portfolio_url: str | None = None
    google_scholar_url: str | None = None
    music_url: str | None = None

    skills: list[str] = []
    languages: list[str] = []

    raw_cgpa: float | None = None
    gpa_scale: float | None = None
    normalized_cgpa: float | None = None
    standardized_gpa_4: float | None = None
    class_of_degree: str | None = None
    credits_earned: int = 0

    scores: ScoreComponents
    approval_status: ApprovalStatus
    is_publicly_visible: bool = False
    is_self_registered: bool = False
    terms_accepted_at: datetime | None = None

    overall_rank: int | None = None
    field_rank: int | None = None
    university_rank: int | None = None

    badges: list[BadgeOut] = []
    projects: list[ProjectSubmissionOut] = []
    research: list[ResearchOut] = []
    experiences: list[ExperienceOut] = []
    competitions: list[CompetitionOut] = []
    leadership: list[LeadershipOut] = []
    achievements: list[AchievementOut] = []


class Recommendation(BaseModel):
    title: str
    detail: str
    action: str | None = None   # frontend route hint


class OpportunityMatchBrief(BaseModel):
    opportunity_id: str
    title: str
    organization: str | None = None
    type: str
    score: float
    reasoning: str | None = None


class DashboardOut(BaseModel):
    student_id: str
    full_name: str
    avatar_url: str | None = None
    final_score: float
    scores: ScoreComponents
    overall_rank: int | None = None
    field_rank: int | None = None
    university_rank: int | None = None
    field_name: str | None = None
    university_name: str | None = None

    approval_status: ApprovalStatus
    is_publicly_visible: bool
    profile_completion: int  # 0..100
    verified_items: int
    pending_items: int

    missing_info: list[str] = []
    recommendations: list[Recommendation] = []
    badges: list[BadgeOut] = []
    opportunity_matches: list[OpportunityMatchBrief] = []
    unread_notifications: int = 0
