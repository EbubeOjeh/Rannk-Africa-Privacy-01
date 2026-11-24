import os,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 os.environ['DATABASE_URL']='sqlite:///'+str(Path(tmp)/'smoke.db')
 os.environ['UPLOAD_DIR']=str(Path(tmp)/'uploads')
 os.environ['AI_ENABLED']='false'
 os.environ['DEMO_PASSWORD']='DemoPrivacy2026!'
 sys.path.insert(0,str(root/'backend'))
 from app.main import create_app
 from fastapi.testclient import TestClient
 def login(c):
  r=c.post('/api/v1/auth/login',json={'email':'student01@rankafrica.example','password':'DemoPrivacy2026!'})
  assert r.status_code==200
  return {'Authorization':'Bearer '+r.json()['tokens']['access_token']}
 with TestClient(create_app()) as c:
  assert c.get('/').status_code==200
  assert c.get('/student/privacy').status_code==200
  assert c.get('/api/v1/not-a-route').status_code==404
  assert c.get('/health').json()['status']=='ok'
  h=login(c)
  assert c.put('/api/v1/privacy/me',headers=h,json={'public_enabled':True}).status_code==200
  o=c.get('/api/v1/opportunities').json()[0]
  review=c.get('/api/v1/privacy/opportunities/'+o['id']+'/review',headers=h).json()
  r=c.post('/api/v1/opportunities/'+o['id']+'/apply',headers=h,json={'confirmed':True,'recipient_id':review['recipient_id']});assert r.status_code==201
  appid=r.json()['id']
  r=c.post('/api/v1/me/avatar',headers=h,files={'file':('demo.png',b'fictional-image-bytes','image/png')});assert r.status_code==200
  photo=r.json()['avatar_url']
 with TestClient(create_app()) as c:
  h=login(c)
  assert c.get('/api/v1/privacy/me',headers=h).json()['choices']['public_enabled']
  assert c.get('/api/v1/privacy/applications/'+appid,headers=h).status_code==200
  assert c.get(photo,headers=h).content==b'fictional-image-bytes'
print('PASS: startup and controlled seed; root and React deep-link HTML; health; unknown API 404; real sign-in; consent, application and uploaded bytes persist across application lifecycle restart. In-process TestClient only; not Docker/remote hosting evidence.')
