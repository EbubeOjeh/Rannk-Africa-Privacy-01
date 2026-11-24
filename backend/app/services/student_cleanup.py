"""Preview-scoped student cleanup. Never delete schools, recruiters or staff.

Only run through super-admin API with a signed short-lived preview and typed
confirmation. Database rows are transactional; local upload removal is reported
separately after commit. This is not a whole-volume reset or backup erasure.
"""
import hashlib,json,shutil
from pathlib import Path
from sqlalchemy import select,or_
from app.db.base import Base
from app.models.student import Student
from app.models.user import User,UserRole
from app.models.ranking import RankingSnapshot
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.core.config import settings
from app.services import audit_service

SEED_EMAILS={f'student{i:02}@rankafrica.example' for i in range(1,13)}

def plan(db,scope):
    # Profile roots and login roots are determined separately so orphan student
    # records/logins are included only by the explicitly selected scope.
    users=db.query(User).filter(User.role==UserRole.STUDENT).all()
    users=[u for u in users if scope=='all_students' or u.email in SEED_EMAILS]
    user_ids={u.id for u in users}
    students=db.query(Student).all()
    students=[s for s in students if scope=='all_students' or s.user_id in user_ids]
    student_ids={s.id for s in students}
    tables=Base.metadata.tables
    selected={name:set() for name in tables}
    selected['users']=set(user_ids);selected['students']=set(student_ids)
    # Follow references FROM dependent records TO the chosen roots. Never walk
    # upward to institutions, staff, recipients or other parent records.
    changed=True
    while changed:
        changed=False
        for table in tables.values():
            if table.name in ('users','students','universities','fields','roles'):continue
            pk=list(table.primary_key.columns)
            if len(pk)!=1:continue
            predicates=[]
            for fk in table.foreign_keys:
                parent=fk.column.table.name
                if selected.get(parent) and fk.column.primary_key:
                    predicates.append(fk.parent.in_(selected[parent]))
            if not predicates:continue
            ids=set(db.execute(select(pk[0]).where(or_(*predicates))).scalars())
            new=ids-selected[table.name]
            if new:selected[table.name].update(new);changed=True
    # Historical ranking payloads contain serialized profile data, without FKs.
    # Clear every ranking snapshot only when at least one student/profile login
    # is being removed. This is disclosed explicitly in the preview.
    if student_ids or user_ids:
        selected['ranking_snapshots']=set(db.execute(select(RankingSnapshot.id)).scalars())
        entity_ids=set().union(*selected.values())
        selected['audit_logs'].update(db.execute(select(AuditLog.id).where(AuditLog.entity_id.in_(entity_ids))).scalars())
        names={s.full_name for s in students}
        for row in db.query(Notification).all():
            text=(row.body or '')+' '+(row.link or '')
            if any(sid in text for sid in student_ids) or any(name and name in (row.body or '') for name in names):
                selected['notifications'].add(row.id)
    # Digest includes selected row contents, not just IDs: changed data requires
    # a new preview. Password hashes are hashed into the digest, never returned.
    records=[]
    for name,ids in sorted(selected.items()):
        if not ids:continue
        table=tables[name];pk=list(table.primary_key.columns)[0]
        rows=db.execute(select(table).where(pk.in_(ids)).order_by(pk)).mappings().all()
        records.append((name,[dict(r) for r in rows]))
    fingerprint=hashlib.sha256(json.dumps(records,default=str,sort_keys=True).encode()).hexdigest()
    return dict(scope=scope,student_profiles=len(students),student_logins=len(users),
                accounts=[{'name':u.name,'email':u.email} for u in users],
                records_by_table={name:len(ids) for name,ids in selected.items() if ids},
                fingerprint=fingerprint,selected=selected,student_ids=student_ids,user_ids=user_ids)

def summary(p):
    return {k:v for k,v in p.items() if k not in ('fingerprint','selected','student_ids','user_ids')}

def remove_local_uploads(ids):
    root=Path(settings.UPLOAD_DIR).resolve()
    removed=0;failed=0
    if not root.is_dir():return {'directories_removed':0,'directories_failed':0}
    for path in list(root.rglob('*')):
        if path.name not in ids or not path.is_dir():continue
        resolved=path.resolve()
        if root not in resolved.parents or path.is_symlink():
            failed+=1;continue
        try:shutil.rmtree(path);removed+=1
        except OSError:failed+=1
    return {'directories_removed':removed,'directories_failed':failed}

def execute(db,p,actor):
    # Reverse metadata dependency order prevents restrictive FK failures.
    for table in reversed(Base.metadata.sorted_tables):
        ids=p['selected'].get(table.name,set())
        if ids:db.execute(table.delete().where(list(table.primary_key.columns)[0].in_(ids)))
    audit_service.record(db,actor=actor,action='students.cleanup',entity_type='cleanup',
                         metadata={'scope':p['scope'],'deleted_counts':p['records_by_table']})
    db.commit()
    files=remove_local_uploads(p['student_ids']|p['user_ids'])
    return dict(**summary(p),uploads=files,message='Selected student records removed. Staff, school and recruiter accounts were preserved.')
