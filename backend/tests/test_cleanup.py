import pytest
from test_privacy import env
from app.core.config import settings
from app.models.user import User,UserRole
from app.models.student import Student
from app.models.privacy import StudentConsent,PrivacyEvent,ApplicationDisclosure
from app.models.opportunity_application import OpportunityApplication
from app.models.saved_candidate import SavedCandidate
from app.models.ranking import RankingSnapshot
from app.models.university import University
from app.models.audit_log import AuditLog
from app.models.opportunity import Opportunity

@pytest.fixture
def cleanup(env,monkeypatch,tmp_path):
 monkeypatch.setattr(settings,'ENABLE_STUDENT_CLEANUP',True)
 monkeypatch.setattr(settings,'UPLOAD_DIR',str(tmp_path/'uploads'))
 return env

def preview(e,scope='seeded_students'):
 c,db,h,*_=e;r=c.post('/api/v1/admin-cleanup/preview',headers=h('admin'),json={'scope':scope});assert r.status_code==200,r.text;return r.json()
def execute(e,p,**extra):
 c,db,h,*_=e
 return c.post('/api/v1/admin-cleanup/execute',headers=h('admin'),json={'scope':p['scope'],'preview_token':p['preview_token'],'confirmation':p['required_confirmation'],'backup_acknowledged':True,**extra})

def test_disabled_by_default(env):
 c,db,h,*_=env
 assert c.post('/api/v1/admin-cleanup/preview',headers=h('admin'),json={}).status_code==403

def test_permissions_and_preview_do_not_delete(cleanup):
 c,db,h,*_=cleanup
 assert c.post('/api/v1/admin-cleanup/preview',json={}).status_code==401
 assert c.post('/api/v1/admin-cleanup/preview',headers=h('student01'),json={}).status_code==403
 p=preview(cleanup);assert p['student_logins']==12 and p['student_profiles']==12
 assert db.query(Student).count()==12
 assert execute(cleanup,p,confirmation='wrong').status_code==400
 assert execute(cleanup,p,backup_acknowledged=False).status_code==400
 assert db.query(Student).count()==12

def test_seed_cleanup_preserves_other_students_and_staff(cleanup):
 c,db,h,s,opp,u=cleanup
 new=User(name='Ordinary student',email='ordinary@example.com',password_hash='dummy',role=UserRole.STUDENT,is_active=True)
 db.add(new);db.flush();db.add(Student(full_name='Ordinary student',email=new.email,user_id=new.id,university_id=s.university_id,field_id=s.field_id));db.commit()
 p=preview(cleanup);assert p['student_logins']==12
 assert execute(cleanup,p).status_code==200
 db.expire_all();assert db.query(Student).count()==1
 assert db.query(User).filter_by(email='admin@rankafrica.example').one()
 assert db.query(User).filter_by(email='ordinary@example.com').one()
 assert db.query(University).count()==3 and db.query(Opportunity).count()==6
 assert db.query(User).filter(User.role==UserRole.EMPLOYER).count()==3
 assert db.query(User).filter(User.role==UserRole.SCHOOL_ADMIN).count()==3

def test_all_students_cleans_dependents_files_and_archive(cleanup):
 from pathlib import Path
 c,db,h,s,opp,u=cleanup
 # Keep primitive IDs because commit expires deleted ORM instances.
 sid=s.id;uid=s.user_id
 db.add(StudentConsent(student_id=sid,choices={'public_enabled':True}))
 db.add(PrivacyEvent(student_id=sid,action='choices.saved',details={}))
 app=OpportunityApplication(student_id=sid,opportunity_id=opp.id);db.add(app);db.flush()
 db.add(ApplicationDisclosure(application_id=app.id,student_id=sid,recipient_id=u('recruiter1').id,recipient_name='Demo',snapshot={'full_name':s.full_name}))
 db.add(SavedCandidate(student_id=sid,employer_id=u('recruiter1').id))
 db.add(RankingSnapshot(scope='season',scope_key='demo',payload=[{'id':sid,'full_name':s.full_name}],total_entities=1));db.commit()
 path=Path(settings.UPLOAD_DIR)/'transcripts'/sid;path.mkdir(parents=True);(path/'example.pdf').write_bytes(b'fictional')
 staff=Path(settings.UPLOAD_DIR)/'staff'/'preserve';staff.mkdir(parents=True);(staff/'file.txt').write_text('keep')
 p=preview(cleanup,'all_students');assert p['records_by_table']['application_disclosures']==1
 r=execute(cleanup,p);assert r.status_code==200,r.text
 db.expire_all()
 for model in [Student,StudentConsent,PrivacyEvent,OpportunityApplication,ApplicationDisclosure,SavedCandidate,RankingSnapshot]:assert db.query(model).count()==0,model
 assert not path.exists() and (staff/'file.txt').exists()
 assert db.query(User).filter_by(id=uid).first() is None
 assert db.query(AuditLog).filter_by(action='students.cleanup').count()==1
 assert c.get('/api/v1/students').json()['items']==[]


def test_changed_preview_invalidated(cleanup):
 c,db,h,s,*_=cleanup
 p=preview(cleanup);s.bio='changed since preview';db.commit()
 assert execute(cleanup,p).status_code==409
 assert db.query(Student).count()==12

def test_wrong_scope_invalid_token_and_replay(cleanup):
 c,db,h,*_=cleanup
 p=preview(cleanup)
 assert execute(cleanup,p,scope='all_students',confirmation='DELETE ALL STUDENT DATA').status_code==409
 assert execute(cleanup,p,preview_token='invalid').status_code==409
 assert execute(cleanup,p).status_code==200
 assert execute(cleanup,p).status_code==409
