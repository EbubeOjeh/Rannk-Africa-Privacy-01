"""API acceptance tests against isolated temporary SQLite; no real user data."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.core.security import create_access_token
from app.models.user import User, UserApprovalStatus
from app.models.student import Student
from app.models.privacy import StudentConsent, ApplicationDisclosure
from app.models.opportunity import Opportunity
from app.models.ranking import RankingSnapshot
from app.models.site_content import SiteContent
from app.db import privacy_seed

@pytest.fixture
def env(tmp_path,monkeypatch):
    engine=create_engine('sqlite:///'+str(tmp_path/'test.db'),connect_args={'check_same_thread':False})
    Base.metadata.create_all(engine);factory=sessionmaker(bind=engine)
    monkeypatch.setattr(privacy_seed,'SessionLocal',factory)
    from app.core.config import settings
    monkeypatch.setattr(settings,"SEED_DEMO_STUDENTS",True)
    privacy_seed.run()
    app=create_app()
    def override():
        with factory() as s:yield s
    app.dependency_overrides[get_db]=override
    client=TestClient(app)
    db=factory()
    def user(key):return db.query(User).filter(User.email==key+'@rankafrica.example').one()
    def auth(key):return {'Authorization':'Bearer '+create_access_token(user(key).id)}
    student=db.query(Student).filter_by(user_id=user('student01').id).one()
    opp=db.query(Opportunity).filter_by(posted_by_id=user('recruiter1').id).first()
    yield client,db,auth,student,opp,user
    db.close();engine.dispose()

def settings(c,h,**kwargs):
    return c.put('/api/v1/privacy/me',headers=h,json=kwargs)

def test_T1_private_defaults(env):
    c,db,h,s,opp,u=env
    r=c.get('/api/v1/privacy/me',headers=h('student01')).json()
    assert not any(r['choices'].values())
    assert c.get('/api/v1/students').json()['meta']['total']==0
    assert c.get('/api/v1/employers/search',headers=h('recruiter1')).json()['total']==0

def test_T2_independent_audiences(env):
    c,db,h,s,opp,u=env
    settings(c,h('student01'),recruiter_enabled=True,recruiter_bio=True)
    assert c.get(f'/api/v1/students/{s.id}').status_code==404
    r=c.get(f'/api/v1/students/{s.id}/full',headers=h('recruiter1')).json()
    assert r['bio']==s.bio
    assert 'email' not in r
    settings(c,h('student01'),public_enabled=True)
    assert c.get(f'/api/v1/students/{s.id}').status_code==200
    assert c.get(f'/api/v1/students/{s.id}',headers=h('recruiter1')).status_code==404

def test_T3_release_not_consent(env):
    c,db,h,s,opp,u=env
    assert c.put(f'/api/v1/privacy/school/{s.id}/release',headers=h('school1'),json={'released':True}).status_code==200
    assert c.get(f'/api/v1/students/{s.id}').status_code==404
    settings(c,h('student01'),public_enabled=True)
    c.put(f'/api/v1/privacy/school/{s.id}/release',headers=h('school1'),json={'released':False})
    assert c.get(f'/api/v1/students/{s.id}').status_code==404
    assert c.get('/api/v1/privacy/me',headers=h('student01')).json()['choices']['public_enabled']

def test_T4_minimization(env):
    c,db,h,s,opp,u=env
    settings(c,h('student01'),public_enabled=True,public_bio=True)
    r=c.get(f'/api/v1/students/{s.id}/full').json()
    assert r['bio']==s.bio
    assert not {'email','phone_number','avatar_url','portfolio_url','resume_url','raw_cgpa','matric_number'} & r.keys()
    r=c.get('/api/v1/students').json()['items'][0]
    assert not {'email','phone_number','resume_url'} & r.keys()

def test_T5_saved_preview_exact(env):
    c,db,h,s,opp,u=env
    result=settings(c,h('student01'),public_enabled=True,public_portfolio=True,recruiter_enabled=True,recruiter_bio=True).json()
    assert result['previews']['public']==c.get(f'/api/v1/students/{s.id}/full').json()
    assert result['previews']['recruiter']==c.get(f'/api/v1/students/{s.id}/full',headers=h('recruiter1')).json()

def test_T6_withdrawal_saved_and_archive(env):
    c,db,h,s,opp,u=env
    settings(c,h('student01'),public_enabled=True,recruiter_enabled=True)
    c.post(f'/api/v1/employers/saved/{s.id}',headers=h('recruiter1'),json={})
    db.add(RankingSnapshot(scope='season',scope_key='demo',payload=[{'id':s.id,'email':'never disclose'}],total_entities=1));db.commit()
    assert c.get('/api/v1/rankings/season?label=demo').json()['total']==1
    settings(c,h('student01'))
    for path in [f'/students/{s.id}',f'/students/{s.id}/full']:
        assert c.get('/api/v1'+path).status_code==404
    assert c.get('/api/v1/employers/saved',headers=h('recruiter1')).json()==[]
    assert c.get('/api/v1/rankings/season?label=demo').json()['rows']==[]
    assert c.get('/api/v1/analytics/platform').json()['top_student_name'] is None

def test_T6_persistence_new_session(env):
    c,db,h,s,opp,u=env
    settings(c,h('student01'),recruiter_enabled=True,recruiter_portfolio=True)
    db.expire_all()
    assert c.get('/api/v1/privacy/me',headers=h('student01')).json()['choices']['recruiter_portfolio']
    assert db.query(StudentConsent).filter_by(student_id=s.id).one().choices['recruiter_enabled']

def send(env,**extra):
    c,db,h,s,opp,u=env
    return c.post(f'/api/v1/opportunities/{opp.id}/apply',headers=h('student01'),json={'confirmed':True,'recipient_id':u('recruiter1').id,**extra})

def test_T7_confirmation_required(env):
    c,db,h,s,opp,u=env
    assert send(env,confirmed=False).status_code==400
    assert c.post(f'/api/v1/opportunities/{opp.id}/apply',headers=h('student01')).status_code==422
    assert db.query(ApplicationDisclosure).count()==0

def test_T7_named_recipient(env):
    c,db,h,s,opp,u=env
    assert send(env,recipient_id=u('recruiter2').id).status_code==409
    r=send(env,email=True).json()
    right=c.get('/api/v1/privacy/applications/'+r['id'],headers=h('recruiter1'))
    assert right.json()['snapshot']['email']==s.email
    assert c.get('/api/v1/privacy/applications/'+r['id'],headers=h('recruiter2')).status_code==404
    assert c.get('/api/v1/privacy/applications/'+r['id'],headers=h('student02')).status_code==403

def test_T7_immutable_retained_snapshot(env):
    c,db,h,s,opp,u=env
    appid=send(env,bio=True).json()['id']
    original=c.get('/api/v1/privacy/applications/'+appid,headers=h('recruiter1')).json()['snapshot']
    s.bio='Edited later';db.commit()
    settings(c,h('student01'))
    send(env,email=True)
    assert c.get('/api/v1/privacy/applications/'+appid,headers=h('recruiter1')).json()['snapshot']==original

def test_T8_private_application_no_extras(env):
    c,db,h,s,opp,u=env
    assert len(c.get('/api/v1/opportunities').json())==6
    assert c.get(f'/api/v1/privacy/opportunities/{opp.id}/review',headers=h('student01')).json()['recipient_name']=='Demo Employer 1'
    appid=send(env).json()['id']
    snap=c.get('/api/v1/privacy/applications/'+appid,headers=h('student01')).json()['snapshot']
    assert not {'email','bio','avatar_url','portfolio_url'} & snap.keys()
    assert not any(c.get('/api/v1/privacy/me',headers=h('student01')).json()['choices'].values())

def test_current_approval_each_request(env):
    c,db,h,s,opp,u=env
    settings(c,h('student01'),recruiter_enabled=True)
    appid=send(env).json()['id']
    r=u('recruiter1');r.approval_status=UserApprovalStatus.REJECTED;db.commit()
    assert c.get('/api/v1/employers/search',headers=h('recruiter1')).status_code==403
    assert c.get('/api/v1/privacy/applications/'+appid,headers=h('recruiter1')).status_code==403
    assert c.get(f'/api/v1/students/{s.id}',headers=h('recruiter1')).status_code==404

def test_cross_school_denied(env):
    c,db,h,s,opp,u=env
    assert c.put(f'/api/v1/privacy/school/{s.id}/release',headers=h('school2'),json={'released':False}).status_code==404
    assert all(x['university_id']==u('school2').university_id for x in c.get('/api/v1/privacy/school/roster',headers=h('school2')).json())

def test_owner_only_settings(env):
    c,db,h,s,opp,u=env
    assert settings(c,h('recruiter1'),public_enabled=True).status_code==403
    assert settings(c,h('admin'),student_id=s.id,public_enabled=True).status_code==403
    assert settings(c,h('student01'),student_id=s.id,public_enabled=True).status_code==422
    assert c.get('/api/v1/privacy/me').status_code==401

def test_filtered_rank_no_hidden_positions(env):
    c,db,h,s,opp,u=env
    settings(c,h('student01'),public_enabled=True)
    settings(c,h('student03'),public_enabled=True)
    rows=c.get('/api/v1/rankings/students?include_unpublished=true').json()['rows']
    assert [r['overall_rank'] for r in rows]==[1,2]
    result=c.get('/api/v1/rankings/students?min_score=93').json()
    assert [r['overall_rank'] for r in result['rows']]==[1]

def test_withdraw_clears_optional_choices(env):
    c,db,h,s,opp,u=env
    result=settings(c,h('student01'),public_enabled=False,public_bio=True).json()
    assert not result['choices']['public_bio']

def test_platform_release_blocks_even_admin_discovery(env):
    c,db,h,s,opp,u=env
    settings(c,h('student01'),public_enabled=True)
    row=db.query(SiteContent).filter_by(key='rankings').one();row.data={'released':False};db.commit()
    assert c.get('/api/v1/rankings/students?include_unpublished=true',headers=h('admin')).json()['rows']==[]
    assert c.get(f'/api/v1/students/{s.id}',headers=h('admin')).status_code==404

def test_legacy_rich_routes_denied(env):
    c,db,h,s,opp,u=env
    assert c.get(f'/api/v1/projects/by-student/{s.id}').status_code==401
    assert c.get(f'/api/v1/achievements/by-student/{s.id}',headers=h('student02')).status_code==404
    assert c.get(f'/api/v1/opportunities/{opp.id}/applicants',headers=h('admin')).status_code==403

def test_seeded_login_all_roles(env):
    c,db,h,s,opp,u=env
    for key in ['student01','recruiter1','school1','admin']:
        r=c.post('/api/v1/auth/login',json={'email':key+'@rankafrica.example','password':'DemoPrivacy2026!'})
        assert r.status_code==200, (key,r.text)
        assert r.json()['tokens']['access_token']

def test_protected_upload_and_recipient_retention(env,tmp_path,monkeypatch):
    from app.core.config import settings as config
    c,db,h,s,opp,u=env
    monkeypatch.setattr(config,'UPLOAD_DIR',str(tmp_path))
    folder=tmp_path/'avatars'/s.id;folder.mkdir(parents=True)
    (folder/'photo.png').write_bytes(b'fictional-photo-bytes')
    s.avatar_url=f'/uploads/avatars/{s.id}/photo.png';db.commit()
    assert c.get(s.avatar_url).status_code==404
    assert c.get(s.avatar_url,headers=h('student01')).status_code==200
    settings(c,h('student01'),recruiter_enabled=True,recruiter_photo=True)
    assert c.get(s.avatar_url,headers=h('recruiter1')).status_code==200
    assert c.get(s.avatar_url).status_code==404
    send(env,photo=True)
    settings(c,h('student01'))
    assert c.get(s.avatar_url,headers=h('recruiter1')).status_code==200
    assert c.get(s.avatar_url,headers=h('recruiter2')).status_code==404

def test_private_resume_not_public(env,tmp_path,monkeypatch):
    from app.core.config import settings as config
    c,db,h,s,opp,u=env
    monkeypatch.setattr(config,'UPLOAD_DIR',str(tmp_path))
    folder=tmp_path/'resumes'/s.id;folder.mkdir(parents=True);(folder/'cv.pdf').write_bytes(b'demo')
    url=f'/uploads/resumes/{s.id}/cv.pdf'
    settings(c,h('student01'),public_enabled=True,recruiter_enabled=True)
    assert c.get(url).status_code==404
    assert c.get(url,headers=h('recruiter1')).status_code==404
    assert c.get(url,headers=h('student01')).status_code==200
