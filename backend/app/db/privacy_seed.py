"""Small fictional assessment dataset; never auto-reset existing data."""
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User, UserRole, UserApprovalStatus
from app.models.university import University, SchoolApprovalStatus
from app.models.student import Student, ApprovalStatus
from app.models.field import Field
from app.models.opportunity import Opportunity, OpportunityType
from app.models.employer_profile import EmployerProfile
from app.models.site_content import SiteContent
from app.core.security import hash_password

def run():
    password=settings.DEMO_PASSWORD
    with SessionLocal() as db:
        if db.query(University).first():return
        hashed=hash_password(password)
        def user(name,email,role,**kwargs):
            u=User(name=name,email=email,password_hash=hashed,role=role,is_email_verified=True,
                   approval_status=UserApprovalStatus.APPROVED,is_active=True,**kwargs)
            db.add(u);db.flush();return u
        user('Demo Administrator','admin@rankafrica.example',UserRole.SUPER_ADMIN)
        schools=[]
        for i,name in enumerate(['Demo Coast University','Demo Hills University','Demo River University'],1):
            school=University(name=name,slug=f'demo-school-{i}',short_name=f'DS{i}',country='Nigeria',state='Demo State',approval_status=SchoolApprovalStatus.APPROVED)
            db.add(school);db.flush();schools.append(school)
            user(f'School {i} Reviewer',f'school{i}@rankafrica.example',UserRole.SCHOOL_ADMIN,university_id=school.id)
        fields=[]
        for name,slug in [('Technology','technology'),('Engineering','engineering'),('Law','law')]:
            f=Field(name=name,slug=slug,color='#d4af37',icon='BookOpen');db.add(f);db.flush();fields.append(f)
        for i in range(1,13) if settings.SEED_DEMO_STUDENTS else []:
            u=user(f'Demo Student {i:02}',f'student{i:02}@rankafrica.example',UserRole.STUDENT)
            db.add(Student(full_name=u.name,email=u.email,user_id=u.id,is_self_registered=True,
                           university_id=schools[(i-1)//4].id,field_id=fields[(i-1)%3].id,
                           course=fields[(i-1)%3].name,bio=f'Fictional biography for assessment student {i:02}.',
                           portfolio_url='https://example.com/portfolio',final_score=95-i,standardized_score=95-i,
                           approval_status=ApprovalStatus.APPROVED,is_publicly_visible=True))
        recruiters=[]
        for i in (1,2):
            u=user(f'Demo Recruiter {i}',f'recruiter{i}@rankafrica.example',UserRole.EMPLOYER,organization=f'Demo Employer {i}')
            db.add(EmployerProfile(user_id=u.id,company_name=u.organization,is_verified=True,is_featured=True));recruiters.append(u)
        pending=user('Pending Recruiter','pending@rankafrica.example',UserRole.EMPLOYER,organization='Pending Demo Employer')
        pending.approval_status=UserApprovalStatus.PENDING
        for i in range(6):
            r=recruiters[i%2]
            db.add(Opportunity(title=f'Demo Opportunity {i+1}',description='Fictional opportunity for privacy evaluation. No real recruitment.',
                               type=OpportunityType.INTERNSHIP,organization=r.organization,posted_by_id=r.id,is_active=True,field_id=fields[i%3].id))
        db.add(SiteContent(key='rankings',data={'released':True,'message':'Fictional privacy demonstration; scores are illustrative.'}))
        db.commit()
