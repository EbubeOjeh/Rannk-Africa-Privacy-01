"""Auth payloads."""
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    university_id: str | None = None
    # Optional role hint. Only honoured for self-serve EMPLOYER signups; all
    # other elevated roles must be provisioned by a Super Admin.
    role: UserRole | None = None
    organization: str | None = Field(default=None, max_length=200)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class AuthUser(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    university_id: str | None = None
    organization: str | None = None
    # Recruiter approval state ("pending" until an admin approves).
    approval_status: str | None = None
    # Profile + staff fields.
    avatar_url: str | None = None
    title: str | None = None
    must_change_password: bool = False
    company_role_id: str | None = None
    company_role_name: str | None = None
    # Effective fine-grained permissions, so the frontend can gate UI.
    permissions: list[str] = []
    # Surfaced so the frontend can render a "Pending approval" banner and
    # disable write actions for school admins whose school hasn't been
    # approved yet by the Super Admin.
    school_approval_status: str | None = None
    school_name: str | None = None

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class RecruiterRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    organization: str = Field(min_length=2, max_length=200)
    # PRS §18 — recruiters/organizations must accept the Terms before registering.
    accept_terms: bool = False


class StudentRegisterRequest(BaseModel):
    """PRS §4 — students register individually. They pick an existing university
    or name one (find-or-create), and their course auto-maps to a field."""
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    university_id: str | None = None
    university_name: str | None = Field(default=None, max_length=200)
    state: str | None = None
    course: str = Field(min_length=2, max_length=200)
    faculty: str | None = None
    department: str | None = None
    year_of_study: int | None = None
    academic_level: int | None = None
    gender: str | None = None
    phone_number: str | None = None
    # PRS §18 — must actively agree to the Terms & Conditions before submitting.
    accept_terms: bool = False

    @field_validator("year_of_study", "academic_level", mode="before")
    @classmethod
    def _coerce_numeric_or_none(cls, v):
        """These columns are integers, but older/self-service clients may send a
        label (e.g. "Undergraduate", "Final Year") or an empty string. Accept a
        number (or numeric string) and treat anything non-numeric as unset,
        rather than failing the whole registration with a 422/500."""
        if v is None or isinstance(v, int):
            return v
        s = str(v).strip()
        return int(s) if s.isdigit() else None


class TermsInfo(BaseModel):
    version: str
    confirmation: str
    clauses: list[str]


class AuthResponse(BaseModel):
    user: AuthUser
    tokens: TokenPair


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
