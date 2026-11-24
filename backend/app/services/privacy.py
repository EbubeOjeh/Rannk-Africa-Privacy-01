"""One disclosure policy used by discovery, saved previews, and legacy routes.

Discovery is never an administrative preview. Owner and school records have
separate routes. API metadata IDs enable navigation, not extra profile fields.
"""
from app.models.privacy import StudentConsent
from app.models.student import Student, ApprovalStatus
from app.models.user import UserRole, UserApprovalStatus
from app.services import settings_service

KEYS = tuple(f'{a}_{f}' for a in ('public','recruiter') for f in ('enabled','bio','photo','portfolio'))
NOTICE = ('Discovery sharing is optional. Leave these boxes unchecked to stay out of public and recruiter discovery. '
          'You can still browse opportunities and apply to a recipient you choose. Your assigned school retains its limited roster view.')
RETENTION = ('Withdrawal stops future discovery requests. It cannot recall received copies or delete application snapshots. '
             'Applications remain available to you and their currently approved named recipient until the demonstration database is reset.')

def choices(db, s):
    row = db.query(StudentConsent).filter_by(student_id=s.id).first()
    return {k: bool((row.choices if row else {}).get(k, False)) for k in KEYS}

def eligible(db, s, audience, viewer=None):
    if not s or not s.is_publicly_visible or s.approval_status != ApprovalStatus.APPROVED:
        return False
    if not choices(db, s)[audience+'_enabled']:
        return False
    if audience == 'public':
        return settings_service.is_rankings_released(db)
    return bool(viewer and viewer.is_active and viewer.role == UserRole.EMPLOYER
                and viewer.approval_status == UserApprovalStatus.APPROVED)

def audience_for(viewer):
    return 'recruiter' if viewer and viewer.role == UserRole.EMPLOYER else 'public'

def core(s):
    return dict(id=s.id, full_name=s.full_name, university_id=s.university_id,
                university_name=s.university.name if s.university else '',
                field_id=s.field_id, field_name=s.field.name if s.field else None,
                final_score=s.final_score)

def disclose(db, s, audience, viewer=None):
    if not eligible(db, s, audience, viewer):
        return None
    out = core(s)
    c = choices(db,s)
    for choice, field in [('bio','bio'),('photo','avatar_url'),('portfolio','portfolio_url')]:
        if c[audience+'_'+choice]: out[field] = getattr(s,field)
    return out

def visible(db, audience='public', viewer=None):
    return [s for s in db.query(Student).order_by(Student.final_score.desc(), Student.id).all()
            if eligible(db,s,audience,viewer)]
