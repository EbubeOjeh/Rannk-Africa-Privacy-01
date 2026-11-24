from test_privacy import env
from test_open_classroom import register,auth
from app.models.exit_feedback import ExitFeedback
from app.services import exit_feedback
from app.core.config import settings


def payload():return dict(respondent_name='Test Classmate',student_identifier='DEMO-ID-001',answers=['True']*3+['5 Very likely']*4,general_review='A fictional test review.',consent_to_submit=True)


def test_exit_saved_once_and_emailed_with_identity(env,monkeypatch):
 c,db,h,*_=env;head=auth(register(c));sent=[]
 def send(row):sent.append((row.respondent_name,row.student_identifier,row.answers,row.general_review));return 'sent'
 monkeypatch.setattr(exit_feedback,'send_response',send)
 assert not c.get('/api/v1/classroom/exit-feedback/me',headers=head).json()['submitted']
 qs=c.get('/api/v1/classroom/exit-questionnaire',headers=head).json();assert len(qs['questions'])==7
 r=c.post('/api/v1/classroom/exit-feedback/me',headers=head,json=payload());assert r.status_code==200,r.text
 assert r.json()['email_status']=='sent' and len(sent)==1
 assert sent[0][0]=='Test Classmate' and sent[0][1]=='DEMO-ID-001'
 assert c.post('/api/v1/classroom/exit-feedback/me',headers=head,json=payload()).json()['already_submitted']
 assert len(sent)==1
 assert c.get('/api/v1/classroom/exit-feedback/me',headers=head).json()['submitted']
 assert not any(c.get('/api/v1/privacy/me',headers=head).json()['choices'].values())
 assert c.get('/api/v1/classroom/exit-feedback',headers=head).status_code==403
 exported=c.get('/api/v1/classroom/exit-feedback',headers=h('admin')).json()
 assert len(exported)==1 and exported[0]['student_identifier']=='DEMO-ID-001'
 assert 'consent_text' not in c.get('/api/v1/students').text


def test_exit_owner_scope_validation_and_consent(env,monkeypatch):
 c,db,h,*_=env;ha=auth(register(c));hb=auth(register(c,'P02'))
 monkeypatch.setattr(exit_feedback,'send_response',lambda row:'not_configured')
 p=payload();p['consent_to_submit']=False
 assert c.post('/api/v1/classroom/exit-feedback/me',headers=ha,json=p).status_code==400
 p=payload();p['respondent_name']='  '
 assert c.post('/api/v1/classroom/exit-feedback/me',headers=ha,json=p).status_code==422
 p=payload();p['answers'][0]='Invalid'
 assert c.post('/api/v1/classroom/exit-feedback/me',headers=ha,json=p).status_code==422
 p=payload();p['answers']=[None]*7
 assert c.post('/api/v1/classroom/exit-feedback/me',headers=ha,json=p).json()['email_status']=='not_configured'
 assert not c.get('/api/v1/classroom/exit-feedback/me',headers=hb).json()['submitted']
 assert c.get('/api/v1/classroom/exit-feedback/me').status_code==401
 row=db.query(ExitFeedback).one()
 assert c.post('/api/v1/classroom/exit-feedback/'+row.user_id+'/retry-email',headers=hb).status_code==403


def test_failed_email_saved_and_admin_can_retry(env,monkeypatch):
 c,db,h,*_=env;head=auth(register(c))
 monkeypatch.setattr(exit_feedback,'send_response',lambda row:'failed')
 assert c.post('/api/v1/classroom/exit-feedback/me',headers=head,json=payload()).json()['email_status']=='failed'
 row=db.query(ExitFeedback).one();identifier=row.user_id
 monkeypatch.setattr(exit_feedback,'send_response',lambda row:'sent')
 assert c.post('/api/v1/classroom/exit-feedback/'+identifier+'/retry-email',headers=h('admin')).json()['email_status']=='sent'
 monkeypatch.setattr(exit_feedback,'send_response',lambda row:(_ for _ in ()).throw(AssertionError('already sent')))
 assert c.post('/api/v1/classroom/exit-feedback/'+identifier+'/retry-email',headers=h('admin')).json()['email_status']=='sent'


def test_smtp_delivery_uses_tls_and_no_stub_success(monkeypatch):
 from types import SimpleNamespace
 monkeypatch.setattr(settings,'EXIT_FEEDBACK_RECIPIENT','facilitator@example.com');monkeypatch.setattr(settings,'SMTP_HOST','')
 row=SimpleNamespace(participant_id='S-TEST',respondent_name='Test Name',student_identifier='TEST-ID',answers=[None]*7,general_review='Test',consent_text=exit_feedback.CONSENT)
 assert exit_feedback.send_response(row)=='not_configured'
 monkeypatch.setattr(settings,'SMTP_HOST','smtp.example.com');monkeypatch.setattr(settings,'SMTP_FROM','sender@example.com');monkeypatch.setattr(settings,'SMTP_USE_SSL',False)
 calls=[]
 class SMTP:
  def __init__(self,*a,**k):pass
  def __enter__(self):return self
  def __exit__(self,*a):pass
  def ehlo(self):pass
  def starttls(self,**kwargs):calls.append('tls')
  def login(self,*args):pass
  def send_message(self,msg):calls.append(msg)
 monkeypatch.setattr(exit_feedback.smtplib,'SMTP',SMTP)
 assert exit_feedback.send_response(row)=='sent'
 assert calls[0]=='tls' and 'TEST-ID' in calls[1].get_content()
 assert calls[1]['To']=='facilitator@example.com'
 class Broken(SMTP):
  def starttls(self,**kwargs):raise RuntimeError('no TLS')
 monkeypatch.setattr(exit_feedback.smtplib,'SMTP',Broken)
 assert exit_feedback.send_response(row)=='failed'


def test_cleanup_removes_identified_exit_reviews(env,monkeypatch):
 c,db,h,*_=env;head=auth(register(c));monkeypatch.setattr(settings,'ENABLE_STUDENT_CLEANUP',True)
 monkeypatch.setattr(exit_feedback,'send_response',lambda row:'not_configured')
 c.post('/api/v1/classroom/exit-feedback/me',headers=head,json=payload())
 preview=c.post('/api/v1/admin-cleanup/preview',headers=h('admin'),json={'scope':'all_students'}).json()
 result=c.post('/api/v1/admin-cleanup/execute',headers=h('admin'),json={'scope':'all_students','preview_token':preview['preview_token'],'confirmation':preview['required_confirmation'],'backup_acknowledged':True})
 assert result.status_code==200 and db.query(ExitFeedback).count()==0
