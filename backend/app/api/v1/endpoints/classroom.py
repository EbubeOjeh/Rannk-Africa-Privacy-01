"""Open classroom registration: no invitations, codes, or ten-account cap."""
from uuid import uuid4
from io import BytesIO
from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import Response
from pydantic import BaseModel,Field,StrictBool,ConfigDict,field_validator
from sqlalchemy.orm import Session
from app.api.deps import get_current_student,require_super_admin
from app.db.session import get_db
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User,UserRole,UserApprovalStatus
from app.models.student import Student,ApprovalStatus
from app.models.university import University,SchoolApprovalStatus
from app.models.field import Field as AcademicField
from app.models.classroom import ClassroomEnrollment,ClassroomFeedback,ClassroomIdentity
from app.models.terms_acceptance import TermsAcceptance
from app.models.privacy import PrivacyEvent
from app.services.classroom import DATA,TERMS,transcript_pdf
from app.services.auth_service import _build_auth_response
from app.services.evaluation_engine import evaluate_student
from app.services import settings_service
router=APIRouter()

def deployment_ready():
    # Local testing works immediately. Public deployment must supply study info.
    return bool(settings.STUDY_CONTACT.strip() and settings.STUDY_RETENTION_NOTICE.strip()) or settings.APP_ENV=='development'

@router.get('/config')
def config():
    return dict(terms=TERMS,contact=settings.STUDY_CONTACT,retention=settings.STUDY_RETENTION_NOTICE,
                ready=deployment_ready(),local_test=settings.APP_ENV=='development',
                templates=[{k:x[k] for k in ['template_id','field','programme','fictional_school','cgpa']} for x in DATA])

class Register(BaseModel):
    model_config=ConfigDict(extra='forbid')
    template_id:str
    full_name:str=Field(min_length=1,max_length=180)
    student_identifier:str=Field(min_length=1,max_length=100)
    @field_validator("full_name","student_identifier")
    @classmethod
    def nonblank(cls,value):
        value=value.strip()
        if not value:raise ValueError("Name and student ID cannot be blank.")
        return value
    password:str=Field(min_length=8,max_length=64)
    accept_classroom_notice:StrictBool

@router.post('/register',status_code=201)
def register(payload:Register,db:Session=Depends(get_db)):
    if not deployment_ready():raise HTTPException(503,'The facilitator must configure study contact and retention information before registration.')
    if not payload.accept_classroom_notice:raise HTTPException(400,'Read and accept the classroom account notice.')
    record=next((x for x in DATA if x['template_id']==payload.template_id),None)
    if not record:raise HTTPException(422,'Select an available fictional academic profile.')
    if len(payload.password.encode('utf-8'))>72:raise HTTPException(422,'Use no more than 72 UTF-8 bytes for the password.')
    # Every signup receives its own account even if two people select the same
    # synthetic template. Template IDs are public data, never invitation codes.
    unique=uuid4().hex[:12];participant='S-'+unique.upper();email='s'+unique+'@study.rankafrica.example'
    university=db.query(University).filter_by(name=record['fictional_school']).first()
    if not university:raise HTTPException(409,'Required fictional school is missing. Ask the administrator to initialize the classroom dataset.')
    if university.institution_type!='university' or university.tier!=3:
        raise HTTPException(409,'The fictional school configuration changed; the administrator must check its type and tier.')
    field=db.query(AcademicField).filter_by(slug=record['field'].lower()).first()
    if not field:raise HTTPException(409,'Required study field is missing.')
    user=User(name=payload.full_name,email=email,password_hash=hash_password(payload.password),role=UserRole.STUDENT,is_active=True,is_email_verified=False,approval_status=UserApprovalStatus.APPROVED)
    db.add(user);db.flush()
    student=Student(full_name=payload.full_name,email=email,user_id=user.id,university_id=university.id,field_id=field.id,course=record['programme'],raw_cgpa=record['cgpa'],gpa_scale=5.0,credits_earned=18,is_self_registered=True,approval_status=ApprovalStatus.APPROVED,is_publicly_visible=True,bio=f'Fictional classroom study profile {participant}. No real academic records.',avatar_url='/study-avatar.svg',portfolio_url=None)
    db.add(student);db.flush();evaluate_student(db,student)
    db.add(ClassroomIdentity(user_id=user.id,full_name=payload.full_name,student_identifier=payload.student_identifier))
    db.add(ClassroomEnrollment(user_id=user.id,participant_id=participant,template_id=record['template_id'],academic_record=record))
    db.add(TermsAcceptance(user_id=user.id,student_id=student.id,version='assignment-real-name-v2',accepted_text=TERMS+' Contact: '+settings.STUDY_CONTACT+' Retention: '+settings.STUDY_RETENTION_NOTICE))
    db.add(PrivacyEvent(student_id=student.id,action='classroom.account.created',details={'participant_id':participant,'template_id':record['template_id'],'synthetic_data':True,'public_consent':False,'recruiter_consent':False}))
    db.commit();db.refresh(user)
    return _build_auth_response(user)

@router.get('/me')
def me(db:Session=Depends(get_db),student:Student=Depends(get_current_student)):
    enrolled=db.get(ClassroomEnrollment,student.user_id)
    if not enrolled:raise HTTPException(404,'This student account was not created through open classroom registration.')
    identity=db.get(ClassroomIdentity,student.user_id)
    record=dict(enrolled.academic_record,profile_name=student.full_name)
    return dict(**record,student_identifier=identity.student_identifier if identity else None,participant_id=enrolled.participant_id,login=student.email,
                academic_score=student.academic_score,final_score=student.final_score,
                platform_rankings_released=settings_service.is_rankings_released(db))

@router.get('/me/transcript')
def transcript(db:Session=Depends(get_db),student:Student=Depends(get_current_student)):
    enrollment=db.get(ClassroomEnrollment,student.user_id)
    if not enrollment:raise HTTPException(404,'No assigned synthetic academic record.')
    return Response(transcript_pdf(enrollment,student),media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="{enrollment.participant_id}_Synthetic_Record.pdf"','Cache-Control':'no-store'})

QUESTIONS=[
 ('How easy was it to create your student account?',['1 Very difficult','2 Difficult','3 Neither easy nor difficult','4 Easy','5 Very easy','Not completed']),
 ('Immediately after registration, before you changed any privacy settings, which discovery audiences could find your profile?',['Public visitors only','Approved recruiters only','Both audiences','Neither audience','Not sure']),
 ('You saved public discovery ON with biography selected, public photo and portfolio OFF, and recruiter discovery OFF. What should discovery disclose?',['Public visitors receive the core profile and biography; recruiter discovery does not include the profile','Both audiences receive the complete private profile','Public visitors receive the email and transcript too','Not sure']),
 ('Can a student browse opportunities and send a separately confirmed application while both discovery audiences and all optional application fields remain OFF?',['Yes','No','Not sure']),
 ('You change a privacy checkbox but do not click Save. Which settings control the information other people receive?',['The newly selected but unsaved choices','The last successfully saved choices','Both sets of choices','Not sure']),
 ('After sending an application, you withdraw discovery sharing. What should happen to that earlier application?',['It is automatically deleted from the recipient','Its original authorized snapshot remains available to its named recipient while that recipient has current approval','Every recruiter can now see it','Not sure']),
 ('How easy was it to choose who could see your information and then withdraw discovery sharing?',['1 Very difficult','2 Difficult','3 Neither easy nor difficult','4 Easy','5 Very easy','Not attempted'])]

@router.get('/questionnaire')
def questionnaire():
 return [{'question':q,'options':options} for q,options in QUESTIONS]

class Feedback(BaseModel):
 model_config=ConfigDict(extra='forbid')
 consent_to_submit:StrictBool
 answers:list[str|None]=Field(min_length=7,max_length=7)
 general_review:str=Field(default='',max_length=3000)

@router.get('/feedback/me')
def feedback_me(db:Session=Depends(get_db),student:Student=Depends(get_current_student)):
 info=me(db,student);row=db.get(ClassroomFeedback,student.user_id)
 return dict(participant_id=info['participant_id'],answers=row.answers if row else [None]*7,general_review=row.general_review if row else '',saved=bool(row))

@router.put('/feedback/me')
def feedback_save(payload:Feedback,db:Session=Depends(get_db),student:Student=Depends(get_current_student)):
 info=me(db,student)
 if not payload.consent_to_submit:raise HTTPException(400,'Feedback is optional; explicit consent is required to submit it.')
 for i,answer in enumerate(payload.answers):
  if answer is not None and answer not in QUESTIONS[i][1]:raise HTTPException(422,'An answer does not match the options.')
 row=db.get(ClassroomFeedback,student.user_id)
 if row is None:row=ClassroomFeedback(user_id=student.user_id,participant_id=info['participant_id']);db.add(row)
 row.answers=payload.answers;row.general_review=payload.general_review.strip();db.commit()
 return {'message':'Feedback saved. Thank you.','participant_id':info['participant_id']}

@router.get('/feedback',dependencies=[Depends(require_super_admin)])
def feedback_admin(db:Session=Depends(get_db)):
 return [dict(full_name=(db.get(ClassroomIdentity,x.user_id).full_name if db.get(ClassroomIdentity,x.user_id) else None),student_identifier=(db.get(ClassroomIdentity,x.user_id).student_identifier if db.get(ClassroomIdentity,x.user_id) else None),participant_id=x.participant_id,answers=x.answers,general_review=x.general_review,updated_at=x.updated_at) for x in db.query(ClassroomFeedback).order_by(ClassroomFeedback.participant_id).all()]

@router.get('/participants',dependencies=[Depends(require_super_admin)])
def participants(db:Session=Depends(get_db)):
    return [dict(full_name=(db.get(ClassroomIdentity,e.user_id).full_name if db.get(ClassroomIdentity,e.user_id) else None),student_identifier=(db.get(ClassroomIdentity,e.user_id).student_identifier if db.get(ClassroomIdentity,e.user_id) else None),participant_id=e.participant_id,template_id=e.template_id,school=e.academic_record['fictional_school'],field=e.academic_record['field'],feedback_submitted=bool(db.get(ClassroomFeedback,e.user_id))) for e in db.query(ClassroomEnrollment).order_by(ClassroomEnrollment.created_at).all()]

# Exit feedback is separate from the original task questionnaire and consent.
from app.models.exit_feedback import ExitFeedback
from app.services import exit_feedback as exit_review

@router.get('/exit-questionnaire')
def exit_questions(db:Session=Depends(get_db),student:Student=Depends(get_current_student)):
 identity=db.get(ClassroomIdentity,student.user_id)
 return dict(registered_name=student.full_name,student_identifier=identity.student_identifier if identity else "",questions=exit_review.QUESTIONS,consent_text=exit_review.CONSENT,
             email_configured=exit_review.mail_ready(),recipient=settings.EXIT_FEEDBACK_RECIPIENT,
             contact=settings.STUDY_CONTACT,retention=settings.STUDY_RETENTION_NOTICE)

@router.get('/exit-feedback/me')
def exit_me(db:Session=Depends(get_db),student:Student=Depends(get_current_student)):
 row=db.get(ExitFeedback,student.user_id)
 return dict(submitted=bool(row),email_status=row.email_status if row else None)

class ExitSubmission(BaseModel):
 model_config=ConfigDict(extra='forbid')
 respondent_name:str=Field(min_length=1,max_length=180)
 student_identifier:str=Field(min_length=1,max_length=100)
 answers:list[str|None]=Field(min_length=7,max_length=7)
 general_review:str=Field(default='',max_length=3000)
 consent_to_submit:StrictBool

@router.post('/exit-feedback/me')
def submit_exit(payload:ExitSubmission,db:Session=Depends(get_db),student:Student=Depends(get_current_student)):
 if not payload.consent_to_submit:raise HTTPException(400,'Separate agreement is required to submit this identified review.')
 name=payload.respondent_name.strip();identifier=payload.student_identifier.strip()
 if not name or not identifier:raise HTTPException(422,'Enter your name and student ID, or log out without submitting.')
 for question,answer in zip(exit_review.QUESTIONS,payload.answers):
  if answer is not None and answer not in question['options']:raise HTTPException(422,'Choose a listed answer or leave it unanswered.')
 existing=db.get(ExitFeedback,student.user_id)
 if existing:return dict(saved=True,email_status=existing.email_status,already_submitted=True)
 enrollment=db.get(ClassroomEnrollment,student.user_id)
 row=ExitFeedback(user_id=student.user_id,participant_id=enrollment.participant_id if enrollment else "LEGACY-"+student.id[:20],
                  respondent_name=name,student_identifier=identifier,answers=payload.answers,general_review=payload.general_review,
                  consent_text=exit_review.CONSENT,email_status='pending')
 db.add(row);db.commit()
 # Save first so SMTP failure cannot lose a participant's response.
 row.email_status=exit_review.send_response(row);db.commit()
 return dict(saved=True,email_status=row.email_status,already_submitted=False)

@router.get('/exit-feedback')
def exit_export(db:Session=Depends(get_db),actor:User=Depends(require_super_admin)):
 return [dict(user_id=r.user_id,participant_id=r.participant_id,respondent_name=r.respondent_name,
              student_identifier=r.student_identifier,answers=r.answers,general_review=r.general_review,
              email_status=r.email_status,created_at=r.created_at) for r in db.query(ExitFeedback).all()]

@router.post('/exit-feedback/{user_id}/retry-email')
def retry_exit_email(user_id:str,db:Session=Depends(get_db),actor:User=Depends(require_super_admin)):
 row=db.get(ExitFeedback,user_id)
 if not row:raise HTTPException(404,'Response not found.')
 if row.email_status!='sent':row.email_status=exit_review.send_response(row);db.commit()
 return dict(email_status=row.email_status)
