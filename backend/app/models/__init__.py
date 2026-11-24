"""Import all models so SQLAlchemy + Alembic see them."""
from app.models.achievement import (  # noqa: F401
    Achievement,
    AchievementType,
    ACHIEVEMENT_POINTS,
    ACHIEVEMENT_CAP,
    ACHIEVEMENT_LABELS,
    VerificationStatus,
)
from app.models.ai_flag import (  # noqa: F401
    AIFlag,
    FlagSeverity,
    FlagStatus,
    FlagType,
)
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.badge import BADGE_CATALOG, StudentBadge  # noqa: F401
from app.models.competition import (  # noqa: F401
    Competition,
    CompetitionResult,
    CompetitionType,
)
from app.models.contact_message import ContactMessage, ContactMessageStatus  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.employer_profile import EmployerProfile  # noqa: F401
from app.models.evaluation import EvaluationResult  # noqa: F401
from app.models.experience import Experience, ExperienceType  # noqa: F401
from app.models.faculty import Faculty  # noqa: F401
from app.models.field import Field  # noqa: F401
from app.models.leadership import LeadershipActivity, LeadershipType  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.opportunity import Opportunity, OpportunityType  # noqa: F401
from app.models.opportunity_application import (  # noqa: F401
    ApplicationStatus,
    OpportunityApplication,
)
from app.models.opportunity_match import OpportunityMatch  # noqa: F401
from app.models.project_submission import ProjectStatus, ProjectSubmission  # noqa: F401
from app.models.ranking import RankingSnapshot  # noqa: F401
from app.models.research import ResearchPublication, ResearchType  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.saved_candidate import SavedCandidate  # noqa: F401
from app.models.site_content import SiteContent  # noqa: F401
from app.models.student import ApprovalStatus, Student  # noqa: F401
from app.models.submission_cycle import CycleStatus, SubmissionCycle  # noqa: F401
from app.models.terms_acceptance import CURRENT_TERMS_VERSION, TermsAcceptance  # noqa: F401
from app.models.university import University  # noqa: F401
from app.models.user import SCHOOL_ADMIN_ROLES, User, UserRole  # noqa: F401

from app.models.privacy import StudentConsent, PrivacyEvent, ApplicationDisclosure

from app.models.classroom import ClassroomEnrollment, ClassroomFeedback

from app.models.exit_feedback import ExitFeedback

from app.models.classroom import ClassroomIdentity
