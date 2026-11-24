"""Aggregate v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    achievements,
    admin_users,
    analytics,
    approvals,
    auth,
    contact,
    cycles,
    employers,
    fields,
    flags,
    me,
    notifications,
    opportunities,
    projects,
    rankings,
    recruiters,
    reports,
    scoring,
    site,
    students,
    team,
    test_accounts,
    universities,
    users,
    verification,
)

from app.api.v1.endpoints import privacy

from app.api.v1.endpoints import classroom,cleanup
api_router = APIRouter()
api_router.include_router(classroom.router, prefix="/classroom", tags=["open classroom"])
api_router.include_router(cleanup.router, prefix="/admin-cleanup", tags=["student cleanup"])
api_router.include_router(privacy.router, tags=["privacy"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(universities.router, prefix="/universities", tags=["universities"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(me.router, prefix="/me", tags=["me"])
api_router.include_router(fields.router, prefix="/fields", tags=["fields"])
api_router.include_router(rankings.router, prefix="/rankings", tags=["rankings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(cycles.router, prefix="/cycles", tags=["cycles"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["achievements"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(recruiters.router, prefix="/recruiters", tags=["recruiters"])
api_router.include_router(team.router, prefix="/team", tags=["team"])
api_router.include_router(test_accounts.router, prefix="/test-accounts", tags=["test-accounts"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(site.router, prefix="/site", tags=["site"])
# --- PRS v2.0 surfaces ---
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(employers.router, prefix="/employers", tags=["employers"])
api_router.include_router(flags.router, prefix="/flags", tags=["flags"])
api_router.include_router(verification.router, prefix="/verification", tags=["verification"])
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(admin_users.router, prefix="/admin-users", tags=["admin-users"])
