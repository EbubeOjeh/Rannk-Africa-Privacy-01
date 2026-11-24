"""Proposal R1-R8 plus protected compatibility endpoints for original screens.

Registered BEFORE legacy routers so legacy discovery cannot bypass this policy.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, ConfigDict, StrictBool
from sqlalchemy.orm import Session
from app.api.deps import get_current_student, get_current_user, get_current_user_optional, require_super_admin
from app.db.session import get_db
from app.models.student import Student
from app.models.user import User, UserRole, UserApprovalStatus, SCHOOL_ADMIN_ROLES
from app.models.privacy import StudentConsent, PrivacyEvent, ApplicationDisclosure
from app.models.opportunity import Opportunity
from app.models.opportunity_application import OpportunityApplication
from app.models.saved_candidate import SavedCandidate
from app.models.ranking import RankingSnapshot
from app.services import privacy as p

router = APIRouter()

def denied(): raise HTTPException(404, 'Record not available for this audience.')
def approved(actor):
    if actor.role != UserRole.EMPLOYER or actor.approval_status != UserApprovalStatus.APPROVED:
        raise HTTPException(403,'Current recruiter approval is required.')

def event(db,s,action,details): db.add(PrivacyEvent(student_id=s.id,action=action,details=details))

class Choices(BaseModel):
    model_config = ConfigDict(extra='forbid')
    public_enabled: StrictBool = False
    public_bio: StrictBool = False
    public_photo: StrictBool = False
    public_portfolio: StrictBool = False
    recruiter_enabled: StrictBool = False
    recruiter_bio: StrictBool = False
    recruiter_photo: StrictBool = False
    recruiter_portfolio: StrictBool = False

def settings_out(db,s):
    # Recruiter preview uses a synthetic approved audience; actual requests use
    # the authenticated current user and still recheck approval on every call.
    audience = User(role=UserRole.EMPLOYER, approval_status=UserApprovalStatus.APPROVED,is_active=True)
    return dict(choices=p.choices(db,s), notice=p.NOTICE, retention=p.RETENTION,
                academic_released=s.is_publicly_visible,
                previews={a:p.disclose(db,s,a,audience if a=='recruiter' else None) for a in ('public','recruiter')})

@router.get('/privacy/me')
def my_privacy(db:Session=Depends(get_db),s:Student=Depends(get_current_student)):
    return settings_out(db,s)

@router.put('/privacy/me')
def save_privacy(payload:Choices,db:Session=Depends(get_db),s:Student=Depends(get_current_student)):
    c=payload.model_dump()
    for a in ('public','recruiter'):
        if not c[a+'_enabled']:
            for f in ('bio','photo','portfolio'): c[a+'_'+f]=False
    row=db.query(StudentConsent).filter_by(student_id=s.id).first()
    if row is None: row=StudentConsent(student_id=s.id);db.add(row)
    row.choices=c
    event(db,s,'choices.saved',c)
    db.commit()
    return settings_out(db,s)

@router.get('/privacy/history')
def history(db:Session=Depends(get_db),s:Student=Depends(get_current_student)):
    return [dict(action=x.action,details=x.details,created_at=x.created_at) for x in
            db.query(PrivacyEvent).filter_by(student_id=s.id).order_by(PrivacyEvent.created_at.desc()).all()]

@router.get('/privacy/school/roster')
def roster(db:Session=Depends(get_db),actor:User=Depends(get_current_user)):
    if actor.role not in SCHOOL_ADMIN_ROLES or not actor.university_id:
        raise HTTPException(403,'Assigned school account required.')
    return [dict(**p.core(s),academic_released=s.is_publicly_visible) for s in db.query(Student).filter_by(university_id=actor.university_id).all()]

class Release(BaseModel):
    model_config=ConfigDict(extra='forbid')
    released: StrictBool

@router.put('/privacy/school/{student_id}/release')
def release(student_id:str,payload:Release,db:Session=Depends(get_db),actor:User=Depends(get_current_user)):
    s=db.get(Student,student_id)
    if actor.role not in SCHOOL_ADMIN_ROLES or not s or s.university_id!=actor.university_id: denied()
    s.is_publicly_visible=payload.released
    event(db,s,'academic.release',{'released':payload.released})
    db.commit()
    return {'academic_released':s.is_publicly_visible}

# Explicit public discovery. Authentication never turns this into an owner or
# staff record. Owners use /me; school staff use the scoped roster above.
@router.get('/students')
def students(db:Session=Depends(get_db),page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),
             q:str|None=None,university_id:str|None=None,field_id:str|None=None):
    rows=p.visible(db)
    rows=[s for s in rows if (not q or q.lower() in s.full_name.lower()) and
          (not university_id or s.university_id==university_id) and (not field_id or s.field_id==field_id)]
    items=[dict(**p.disclose(db,s,'public'),overall_rank=i+1) for i,s in enumerate(rows)]
    return dict(items=items[(page-1)*page_size:page*page_size],meta=dict(page=page,page_size=page_size,total=len(items),total_pages=max(1,(len(items)+page_size-1)//page_size)))

@router.get('/students/{student_id}')
@router.get('/students/{student_id}/full')
def profile(student_id:str,db:Session=Depends(get_db),viewer:User|None=Depends(get_current_user_optional)):
    s=db.get(Student,student_id);a=p.audience_for(viewer)
    out=p.disclose(db,s,a,viewer) if s else None
    if out is None: denied()
    return out

@router.get('/rankings/students')
def rankings(db:Session=Depends(get_db),scope:str='global',scope_key:str|None=None,
             state:str|None=None,min_score:float|None=None,max_score:float|None=None,
             limit:int=Query(80,ge=1,le=500),offset:int=Query(0,ge=0),sort:str='score'):
    rows=p.visible(db)
    def match(s):
        if scope_key:
            if scope=='university' and s.university_id!=scope_key:return False
            if scope=='field' and scope_key not in (s.field_id,s.field.slug if s.field else None):return False
            if scope=='department' and s.department_id!=scope_key:return False
            if scope=='country' and s.university.country!=scope_key:return False
            if scope=='state' and s.university.state!=scope_key:return False
        return (not state or s.university.state==state) and (min_score is None or s.final_score>=min_score) and (max_score is None or s.final_score<=max_score)
    rows=[s for s in rows if match(s)]
    # Ranks refer to this filtered list, before pagination; name sort preserves them.
    items=[dict(**p.disclose(db,s,'public'),overall_rank=i+1,standardized_score=s.final_score) for i,s in enumerate(rows)]
    if sort=='name': items.sort(key=lambda x:(x['full_name'],x['id']))
    return dict(scope=scope,scope_key=scope_key,total=len(items),rows=items[offset:offset+limit])

@router.get('/rankings/season')
def season(label:str,db:Session=Depends(get_db)):
    snap=db.query(RankingSnapshot).filter_by(scope='season',scope_key=label).first()
    if not snap:denied()
    ids={r.get('id') for r in (snap.payload or [])}
    # Deliberately use CURRENT consent and CURRENT allowed fields, never replay
    # a stale serialized photograph or biography from a historical snapshot.
    rows=[dict(**p.disclose(db,s,'public'),overall_rank=i+1,standardized_score=s.final_score)
          for i,s in enumerate([s for s in p.visible(db) if s.id in ids])]
    return dict(label=label,published_at=snap.updated_at,total=len(rows),rows=rows)

@router.get('/rankings/seasons')
def seasons(db:Session=Depends(get_db)):
    return [dict(label=s.scope_key,total=season(s.scope_key,db)['total'],published_at=s.updated_at)
            for s in db.query(RankingSnapshot).filter_by(scope='season').all()]

@router.get('/analytics/platform')
def platform_stats(db:Session=Depends(get_db)):
    from app.models.university import University
    from app.models.field import Field
    rows=p.visible(db);s=rows[0] if rows else None
    return dict(total_students=len(rows),total_universities=db.query(University).count(),total_fields=db.query(Field).count(),
                top_student_name=s.full_name if s else None,top_student_score=s.final_score if s else None,
                top_student_university=s.university.name if s else None,top_university_name=None,
                top_university_avg_score=None,top_university_student_count=None)

@router.get('/employers/search')
def search(db:Session=Depends(get_db),actor:User=Depends(get_current_user),q:str|None=None,
           university_id:str|None=None,field_id:str|None=None,min_score:float|None=None,max_score:float|None=None,
           page:int=Query(1,ge=1),page_size:int=Query(24,ge=1,le=100)):
    approved(actor)
    rows=[s for s in p.visible(db,'recruiter',actor) if (not q or q.lower() in s.full_name.lower()) and
          (not university_id or s.university_id==university_id) and (not field_id or s.field_id==field_id) and
          (min_score is None or s.final_score>=min_score) and (max_score is None or s.final_score<=max_score)]
    saved={x.student_id for x in db.query(SavedCandidate).filter_by(employer_id=actor.id).all()}
    items=[dict(**p.disclose(db,s,'recruiter',actor),overall_rank=i+1,saved=s.id in saved,contact_unlocked=False) for i,s in enumerate(rows)]
    return dict(items=items[(page-1)*page_size:page*page_size],total=len(items),page=page,page_size=page_size)

@router.get('/employers/saved')
def saved(db:Session=Depends(get_db),actor:User=Depends(get_current_user)):
    approved(actor);ids={x.student_id for x in db.query(SavedCandidate).filter_by(employer_id=actor.id).all()}
    return [dict(**p.disclose(db,s,'recruiter',actor),saved=True,contact_unlocked=False)
            for s in p.visible(db,'recruiter',actor) if s.id in ids]

class Save(BaseModel):
    notes:str|None=None

@router.post('/employers/saved/{student_id}',status_code=201)
def bookmark(student_id:str,payload:Save,db:Session=Depends(get_db),actor:User=Depends(get_current_user)):
    approved(actor);s=db.get(Student,student_id)
    if not p.eligible(db,s,'recruiter',actor):denied()
    row=db.query(SavedCandidate).filter_by(employer_id=actor.id,student_id=student_id).first()
    if not row:db.add(SavedCandidate(employer_id=actor.id,student_id=student_id,notes=payload.notes))
    else:row.notes=payload.notes
    db.commit();return {'message':'Candidate saved.'}

class Apply(BaseModel):
    model_config=ConfigDict(extra='forbid')
    confirmed:StrictBool
    recipient_id:str
    email:StrictBool=False
    bio:StrictBool=False
    photo:StrictBool=False
    portfolio:StrictBool=False

def recipient(db,opp):
    user=db.get(User,opp.posted_by_id) if opp else None
    if not user or not user.is_active or user.role!=UserRole.EMPLOYER or user.approval_status!=UserApprovalStatus.APPROVED:
        raise HTTPException(409,'This opportunity has no currently approved recipient.')
    return user

@router.get('/privacy/opportunities/{opportunity_id}/review')
def review(opportunity_id:str,db:Session=Depends(get_db),s:Student=Depends(get_current_student)):
    opp=db.get(Opportunity,opportunity_id)
    if not opp or not opp.is_active:denied()
    r=recipient(db,opp)
    return dict(opportunity_id=opp.id,title=opp.title,recipient_id=r.id,recipient_name=r.organization or r.name,
                required=p.core(s),optional=['email','bio','photo','portfolio'],retention=p.RETENTION)

@router.post('/opportunities/{opportunity_id}/apply',status_code=201)
def apply(opportunity_id:str,payload:Apply,db:Session=Depends(get_db),s:Student=Depends(get_current_student)):
    if not payload.confirmed:raise HTTPException(400,'Application confirmation required.')
    opp=db.get(Opportunity,opportunity_id)
    if not opp or not opp.is_active:denied()
    r=recipient(db,opp)
    if payload.recipient_id!=r.id:raise HTTPException(409,'Recipient changed. Review this application again.')
    old=db.query(OpportunityApplication).filter_by(opportunity_id=opp.id,student_id=s.id).first()
    if old:
        return dict(id=old.id,already_applied=True,status=old.status.value)
    snap=p.core(s)
    for choice,field in [('email','email'),('bio','bio'),('photo','avatar_url'),('portfolio','portfolio_url')]:
        if getattr(payload,choice):snap[field]=getattr(s,field)
    row=OpportunityApplication(opportunity_id=opp.id,student_id=s.id);db.add(row);db.flush()
    db.add(ApplicationDisclosure(application_id=row.id,student_id=s.id,recipient_id=r.id,
                                recipient_name=r.organization or r.name,snapshot=snap))
    event(db,s,'application.confirmed',dict(application_id=row.id,recipient=r.organization or r.name,shared_fields=list(snap)))
    db.commit()
    return dict(id=row.id,already_applied=False,status=row.status.value)

def application_out(d):
    return dict(id=d.application_id,student_id=d.student_id,recipient_id=d.recipient_id,
                recipient_name=d.recipient_name,snapshot=d.snapshot,created_at=d.created_at)

@router.get('/privacy/applications')
def applications(db:Session=Depends(get_db),actor:User=Depends(get_current_user)):
    if actor.role==UserRole.STUDENT:
        s=db.query(Student).filter_by(user_id=actor.id).first()
        return [application_out(d) for d in db.query(ApplicationDisclosure).filter_by(student_id=s.id).all()] if s else []
    approved(actor)
    return [application_out(d) for d in db.query(ApplicationDisclosure).filter_by(recipient_id=actor.id).all()]

@router.get('/privacy/applications/{application_id}')
def application(application_id:str,db:Session=Depends(get_db),actor:User=Depends(get_current_user)):
    d=db.query(ApplicationDisclosure).filter_by(application_id=application_id).first()
    if not d:denied()
    s=db.get(Student,d.student_id)
    if actor.role==UserRole.STUDENT and s.user_id==actor.id:return application_out(d)
    approved(actor)
    if d.recipient_id!=actor.id:denied()
    return application_out(d)

@router.get('/opportunities/{opportunity_id}/applicants')
def legacy_applicants(opportunity_id:str,db:Session=Depends(get_db),actor:User=Depends(get_current_user)):
    approved(actor)
    opp=db.get(Opportunity,opportunity_id)
    if not opp or opp.posted_by_id!=actor.id:denied()
    ids={a.id for a in db.query(OpportunityApplication).filter_by(opportunity_id=opp.id).all()}
    return [application_out(d) for d in db.query(ApplicationDisclosure).filter_by(recipient_id=actor.id).all() if d.application_id in ids]

# Old rich resources are private owner resources, not discovery fields.
@router.get('/projects/by-student/{student_id}')
@router.get('/achievements/by-student/{student_id}')
def private_extras(student_id:str,s:Student=Depends(get_current_student)):
    if student_id!=s.id:denied()
    return []

@router.get('/rankings/universities')
def university_rankings(db:Session=Depends(get_db),state:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0)):
    from app.models.university import University
    from app.api.v1.endpoints.universities import _hydrate
    rows=[_hydrate(u,db).model_dump() for u in db.query(University).all() if not state or u.state==state]
    rows=[x for x in rows if x['student_count']>0]
    rows.sort(key=lambda x:(-x['avg_score'],x['id']))
    for i,x in enumerate(rows):x['overall_rank']=i+1
    return dict(total=len(rows),rows=rows[offset:offset+limit])

@router.get('/rankings/universities/by-field')
def universities_by_field(field_key:str,db:Session=Depends(get_db)):
    from collections import defaultdict
    groups=defaultdict(list)
    for s in p.visible(db):
        if field_key in (s.field_id,s.field.slug if s.field else None):groups[s.university_id].append(s)
    rows=[]
    for uid,ss in groups.items():
        rows.append(dict(id=uid,university_id=uid,name=ss[0].university.name,university_name=ss[0].university.name,avg_score=sum(s.final_score for s in ss)/len(ss),student_count=len(ss)))
    rows.sort(key=lambda x:(-x['avg_score'],x['id']))
    for i,x in enumerate(rows):x['overall_rank']=i+1
    return dict(field=field_key,rows=rows)

@router.post('/contact/students/{student_id}')
def disabled_contact(student_id:str):
    raise HTTPException(403,'Direct contact relay is disabled in this fictional privacy demonstration. Use a separately confirmed application.')
