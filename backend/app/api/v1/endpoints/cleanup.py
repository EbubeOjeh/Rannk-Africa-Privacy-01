"""Super-admin-only preview and explicit confirmation for student cleanup."""
from datetime import datetime,timedelta,timezone
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,StrictBool
from jose import jwt,JWTError
from sqlalchemy.orm import Session
from app.api.deps import require_super_admin
from app.db.session import get_db
from app.models.user import User
from app.core.config import settings
from app.services import student_cleanup
router=APIRouter()
class Preview(BaseModel):
 model_config=ConfigDict(extra='forbid')
 scope:Literal['seeded_students','all_students']='seeded_students'
class Confirm(Preview):
 preview_token:str
 confirmation:str
 backup_acknowledged:StrictBool

def check():
 if not settings.ENABLE_STUDENT_CLEANUP:raise HTTPException(403,'Set ENABLE_STUDENT_CLEANUP=true to enable this administrator operation.')

@router.post('/preview')
def preview(payload:Preview,db:Session=Depends(get_db),actor:User=Depends(require_super_admin)):
 check();p=student_cleanup.plan(db,payload.scope)
 phrase='DELETE PRELOADED STUDENTS' if payload.scope=='seeded_students' else 'DELETE ALL STUDENT DATA'
 token=jwt.encode({'sub':actor.id,'purpose':'student-cleanup','scope':payload.scope,'digest':p['fingerprint'],
                   'exp':datetime.now(timezone.utc)+timedelta(minutes=10)},settings.SECRET_KEY,algorithm=settings.ALGORITHM)
 return dict(**student_cleanup.summary(p),preview_token=token,required_confirmation=phrase,
             notice='Permanent deletion. All ranking archives are cleared when students are removed. Local student upload folders are removed after the database transaction. Backups, external files, exports and manually entered website content are not erased.')

@router.post('/execute')
def execute(payload:Confirm,db:Session=Depends(get_db),actor:User=Depends(require_super_admin)):
 check()
 phrase='DELETE PRELOADED STUDENTS' if payload.scope=='seeded_students' else 'DELETE ALL STUDENT DATA'
 if not payload.backup_acknowledged or payload.confirmation!=phrase:raise HTTPException(400,'Backup acknowledgement and exact confirmation phrase are required.')
 try:claims=jwt.decode(payload.preview_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
 except JWTError:raise HTTPException(409,'Preview expired or invalid. Generate a fresh preview.')
 if claims.get('sub')!=actor.id or claims.get('purpose')!='student-cleanup' or claims.get('scope')!=payload.scope:
  raise HTTPException(409,'Preview does not match this administrator and scope.')
 p=student_cleanup.plan(db,payload.scope)
 if claims.get('digest')!=p['fingerprint']:raise HTTPException(409,'Selected records changed. Review a fresh preview before deleting.')
 return student_cleanup.execute(db,p,actor)
