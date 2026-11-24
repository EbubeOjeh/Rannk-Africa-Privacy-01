import pytest
from test_privacy import env
from app.core.config import settings
from app.models.classroom import ClassroomEnrollment,ClassroomFeedback,ClassroomIdentity
from app.models.student import Student
from app.models.user import User
from app.models.terms_acceptance import TermsAcceptance
from app.db.base import Base
from app.db import privacy_seed
from app.services.classroom import DATA
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def register(c,template='P01',**extra):
 return c.post('/api/v1/classroom/register',json={'template_id':template,'full_name':next((x['profile_name'] for x in DATA if x['template_id']==template),'Test Name'),'student_identifier':'TEST-'+template,'password':'OpenClassroomPassword123!','accept_classroom_notice':True,**extra})
def auth(response):return {'Authorization':'Bearer '+response.json()['tokens']['access_token']}

def test_open_registration_all_templates_no_invitation(env):
 c,db,h,*_=env
 ids=set()
 for record in DATA:
  r=register(c,record['template_id']);assert r.status_code==201,r.text
  head=auth(r);me=c.get('/api/v1/classroom/me',headers=head).json()
  assert me['fictional_school']==record['fictional_school'] and me['cgpa']==record['cgpa']
  assert me['academic_score']>0
  ids.add(me['participant_id'])
  pdf=c.get('/api/v1/classroom/me/transcript',headers=head)
  assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')
  from pypdf import PdfReader
  from io import BytesIO
  text=PdfReader(BytesIO(pdf.content)).pages[0].extract_text()
  assert me['fictional_school'] in text and me['profile_name'] in text
  assert f"{me['cgpa']:.2f}" in text and 'NOT AN OFFICIAL' in text
 assert len(ids)==10
 # An eleventh account can reuse a dataset; no hidden participant cap/codes.
 assert register(c,'P01').status_code==201
 assert db.query(ClassroomEnrollment).count()==11
 for field in ['Technology','Engineering','Law']:
  assert len({x['fictional_school'] for x in DATA if x['field']==field})>=2

def test_private_defaults_disclosure_and_login(env):
 c,db,h,*_=env;r=register(c);assert r.status_code==201
 head=auth(r);user=r.json()['user'];student=db.query(Student).filter_by(user_id=user['id']).one()
 result=c.get('/api/v1/privacy/me',headers=head).json();assert not any(result['choices'].values())
 assert c.get('/api/v1/students/'+student.id).status_code==404
 assert c.put('/api/v1/privacy/me',headers=head,json={'public_enabled':True,'public_bio':True}).status_code==200
 public=c.get('/api/v1/students/'+student.id).json()
 assert public['university_name']=='Demo Coast University' and 'email' not in public and 'avatar_url' not in public
 assert c.post('/api/v1/auth/login',json={'email':user['email'],'password':'OpenClassroomPassword123!'}).status_code==200
 assert db.query(TermsAcceptance).filter_by(user_id=user['id']).one().version=='assignment-real-name-v2'

def test_separate_optional_feedback_and_owner_scope(env):
 c,db,h,*_=env;a=register(c);b=register(c,'P02');ha=auth(a);hb=auth(b)
 qs=c.get('/api/v1/classroom/questionnaire').json();assert len(qs)==7
 payload={'answers':[None]*7,'general_review':'Test review','consent_to_submit':False}
 assert c.put('/api/v1/classroom/feedback/me',headers=ha,json=payload).status_code==400
 payload['consent_to_submit']=True
 assert c.put('/api/v1/classroom/feedback/me',headers=ha,json=payload).status_code==200
 assert c.get('/api/v1/classroom/feedback/me',headers=ha).json()['saved']
 assert not c.get('/api/v1/classroom/feedback/me',headers=hb).json()['saved']
 assert c.get('/api/v1/classroom/feedback',headers=ha).status_code==403
 assert len(c.get('/api/v1/classroom/feedback',headers=h('admin')).json())==1
 assert len(c.get('/api/v1/classroom/participants',headers=h('admin')).json())==2
 payload['answers'][0]='invalid';assert c.put('/api/v1/classroom/feedback/me',headers=ha,json=payload).status_code==422

def test_unchanged_academic_fields_allowed_but_edits_blocked(env):
 c,db,h,*_=env;r=register(c);head=auth(r)
 assert c.patch('/api/v1/me',headers=head,json={'raw_cgpa':1.0}).status_code==400
 assert c.patch('/api/v1/me',headers=head,json={'bio':'A revised fictional biography','raw_cgpa':4.5,'course':'Computer Science','faculty':''}).status_code==200
 assert c.post('/api/v1/me/transcript',headers=head,files={'file':('real.pdf',b'private','application/pdf')}).status_code==400

def test_notice_and_template_validation(env,monkeypatch):
 c,*_=env
 assert register(c,accept_classroom_notice=False).status_code==400
 assert register(c,'unknown').status_code==422
 monkeypatch.setattr(settings,'APP_ENV','assessment');monkeypatch.setattr(settings,'STUDY_CONTACT','');monkeypatch.setattr(settings,'STUDY_RETENTION_NOTICE','')
 assert not c.get('/api/v1/classroom/config').json()['ready']
 assert register(c).status_code==503
 monkeypatch.setattr(settings,'STUDY_CONTACT','Facilitator');monkeypatch.setattr(settings,'STUDY_RETENTION_NOTICE','Agreed test retention')
 assert register(c).status_code==201

def test_fresh_seed_has_no_student_accounts(tmp_path,monkeypatch):
 engine=create_engine('sqlite:///'+str(tmp_path/'fresh.db'));Base.metadata.create_all(engine)
 factory=sessionmaker(bind=engine);monkeypatch.setattr(privacy_seed,'SessionLocal',factory)
 monkeypatch.setattr(settings,'SEED_DEMO_STUDENTS',False)
 privacy_seed.run();privacy_seed.run()
 with factory() as db:
  assert db.query(Student).count()==0
  assert db.query(User).filter_by(email='admin@rankafrica.example').count()==1
 engine.dispose()

def test_cleanup_removes_classroom_feedback_too(env,monkeypatch):
 c,db,h,*_=env;monkeypatch.setattr(settings,'ENABLE_STUDENT_CLEANUP',True)
 r=register(c);head=auth(r)
 c.put('/api/v1/classroom/feedback/me',headers=head,json={'answers':[None]*7,'general_review':'demo','consent_to_submit':True})
 p=c.post('/api/v1/admin-cleanup/preview',headers=h('admin'),json={'scope':'all_students'}).json()
 result=c.post('/api/v1/admin-cleanup/execute',headers=h('admin'),json={'scope':'all_students','preview_token':p['preview_token'],'confirmation':p['required_confirmation'],'backup_acknowledged':True})
 assert result.status_code==200,result.text
 assert db.query(ClassroomEnrollment).count()==0 and db.query(ClassroomFeedback).count()==0 and db.query(ClassroomIdentity).count()==0


def test_chosen_classroom_photo_obeys_public_consent(env,tmp_path,monkeypatch):
 import base64
 c,db,h,*_=env
 monkeypatch.setattr(settings,'UPLOAD_DIR',str(tmp_path/'photo-storage'))
 r=register(c);head=auth(r)
 # A valid one-pixel PNG. Uploading must not turn on either audience.
 png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l9sAAAAASUVORK5CYII=')
 up=c.post('/api/v1/me/avatar',headers=head,files={'file':('chosen.png',png,'image/png')})
 assert up.status_code==200,up.text
 sid=up.json()['id'];url=up.json()['avatar_url']
 assert c.get(url,headers=head).status_code==200
 assert c.get(url).status_code==404
 assert not any(c.get('/api/v1/privacy/me',headers=head).json()['choices'].values())
 assert not any(x['id']==sid for x in c.get('/api/v1/rankings/students').json()['rows'])
 assert c.patch('/api/v1/me',headers=head,json={'bio':'My selected biography','portfolio_url':'https://example.com/my-work'}).status_code==200
 saved_choices=c.get('/api/v1/privacy/me',headers=head).json()['choices']
 def save(**v):
  saved_choices.update(v)
  assert c.put('/api/v1/privacy/me',headers=head,json=saved_choices).status_code==200
 def row():return next(x for x in c.get('/api/v1/rankings/students').json()['rows'] if x['id']==sid)
 save(public_enabled=True)
 assert not {'avatar_url','bio','portfolio_url','email','transcript_url'} & row().keys()
 assert c.get(url).status_code==404
 save(public_photo=True,public_bio=True,public_portfolio=True)
 visible=row();assert visible['avatar_url']==url and visible['bio']=='My selected biography'
 assert visible['portfolio_url']=='https://example.com/my-work'
 assert not {'email','transcript_url','raw_cgpa','resume_url'} & visible.keys()
 assert c.get(url).status_code==200
 save(public_photo=False,public_bio=False,public_portfolio=False)
 assert not {'avatar_url','bio','portfolio_url'} & row().keys()
 assert c.get(url).status_code==404
 save(public_enabled=False)
 assert not any(x['id']==sid for x in c.get('/api/v1/rankings/students').json()['rows'])


def test_photo_upload_keeps_recruiter_choice_and_academics_separate(env,tmp_path,monkeypatch):
 c,db,h,*_=env;monkeypatch.setattr(settings,'UPLOAD_DIR',str(tmp_path/'images'))
 r=register(c,'P05');head=auth(r)
 original=c.get('/api/v1/classroom/me',headers=head).json()
 upload=c.post('/api/v1/me/avatar',headers=head,files={'file':('chosen.jpg',b'example-image-bytes','image/jpeg')})
 assert upload.status_code==200
 url=upload.json()['avatar_url'];sid=upload.json()['id']
 assert c.put('/api/v1/privacy/me',headers=head,json={'recruiter_enabled':True,'recruiter_photo':True}).status_code==200
 assert c.get(url).status_code==404
 assert c.get(url,headers=h('recruiter1')).status_code==200
 assert c.get(url,headers=h('pending')).status_code==404
 assert c.get('/api/v1/students/'+sid).status_code==404
 assert c.put('/api/v1/privacy/me',headers=head,json={'recruiter_photo':False}).status_code==200
 assert c.get(url,headers=h('recruiter1')).status_code==404
 current=c.get('/api/v1/classroom/me',headers=head).json()
 for k in ['fictional_school','cgpa','academic_score','final_score']:assert current[k]==original[k]
 assert c.post('/api/v1/me/transcript',headers=head,files={'file':('grades.pdf',b'private','application/pdf')}).status_code==400
 assert c.post('/api/v1/me/avatar',headers=head,files={'file':('bad.html',b'bad','text/html')}).status_code==422


def test_registration_identity_is_private_but_name_shares_with_consent(env):
 c,db,h,*_=env
 r=register(c,full_name=' Test Real Name ',student_identifier=' STUDY-ID-100 ');assert r.status_code==201,r.text
 head=auth(r);sid=db.query(Student).filter_by(user_id=r.json()['user']['id']).one().id
 assert r.json()['user']['name']=='Test Real Name'
 me=c.get('/api/v1/classroom/me',headers=head).json()
 assert me['student_identifier']=='STUDY-ID-100' and me['profile_name']=='Test Real Name'
 assert c.get('/api/v1/students/'+sid).status_code==404
 assert c.put('/api/v1/privacy/me',headers=head,json={'public_enabled':True,'recruiter_enabled':True}).status_code==200
 public=c.get('/api/v1/students/'+sid).json()
 assert public['full_name']=='Test Real Name' and 'student_identifier' not in public and 'email' not in public
 recruiter=c.get('/api/v1/students/'+sid+'/full',headers=h('recruiter1')).json()
 assert 'student_identifier' not in recruiter and 'STUDY-ID-100' not in str(recruiter)
 rows=c.get('/api/v1/classroom/participants',headers=h('admin')).json()
 assert rows[0]['full_name']=='Test Real Name' and rows[0]['student_identifier']=='STUDY-ID-100'
 assert c.get('/api/v1/classroom/participants',headers=head).status_code==403
 qs=c.get('/api/v1/classroom/exit-questionnaire',headers=head).json()
 assert qs['registered_name']=='Test Real Name' and qs['student_identifier']=='STUDY-ID-100'


def test_registration_requires_name_and_student_id(env):
 c,*_=env
 for extra in [{'full_name':''},{'full_name':'   '},{'student_identifier':''},{'student_identifier':'  '}]:
  assert register(c,**extra).status_code==422
 r=c.post('/api/v1/classroom/register',json={'template_id':'P01','password':'Password123!','accept_classroom_notice':True})
 assert r.status_code==422
