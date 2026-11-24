"""Synthetic templates shared by registration, profile validation and PDF output."""
import json
from pathlib import Path
DATA=json.loads((Path(__file__).parent/'classroom_data.json').read_text())
TERMS=('This is an assignment demonstration, not a real academic ranking or recruitment service. '
       'Your selected school, programme and grades are fictional study data. Do not submit real transcripts or grades. '
       'You may upload a profile photograph if you wish. A CV is not required. '
       'Creating an account does not make your profile public or visible to recruiters. You control these audiences '
       'separately and choose whether to share your photograph, biography or portfolio. Your name is part of your '
       'profile when you enable sharing; your student ID is kept private for the facilitator. '
       'Public sharing makes your selected information visible on the internet. Withdrawing sharing stops future '
       'discovery but cannot recall downloaded copies or previously submitted applications. Participation and feedback '
       'follow the lecturer-approved study information and consent process. Use a password you do not use elsewhere.')
ACADEMIC_FIELDS={'course','faculty','department_id','academic_level','year_of_study','raw_cgpa','raw_gpa','gpa_scale','credits_earned'}
COURSES={
 'Technology':['Programming Fundamentals','Data Structures','Database Systems','Computer Networks','Software Design','Cybersecurity Basics'],
 'Engineering':['Engineering Mathematics','Engineering Mechanics','Materials Science','Thermodynamics','Engineering Design','Fluid Mechanics'],
 'Law':['Legal Methods','Constitutional Law','Law of Contract','Criminal Law','Law of Torts','Legal Research']}
MARKS=[[85,78,73,68,65,62],[79,74,67,63,58,54],[76,65,61,57,52,47],[68,62,58,54,48,44],[88,81,75,71,68,64],[77,69,66,59,55,51],[65,61,56,52,48,43],[86,78,74,69,65,61],[74,68,63,59,54,49],[64,58,53,48,44,41]]
def grade(m):return ('A',5) if m>=70 else ('B',4) if m>=60 else ('C',3) if m>=50 else ('D',2) if m>=45 else ('E',1) if m>=40 else ('F',0)

def transcript_pdf(enrollment,student):
    from io import BytesIO
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from xml.sax.saxutils import escape
    record=enrollment.academic_record;styles=getSampleStyleSheet();buffer=BytesIO()
    # Embed the fonts bundled with ReportLab for consistent phone/PDF rendering.
    import reportlab
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fonts=Path(reportlab.__file__).parent/'fonts'
    for name,file in [('StudyVera','Vera.ttf'),('StudyVeraBold','VeraBd.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    for name in ['Normal','Title','Heading2']:
        styles[name].fontName='StudyVera' if name=='Normal' else 'StudyVeraBold'
    # No real institution branding, seal or signature is used.
    story=[Paragraph('SYNTHETIC ACADEMIC RECORD',styles['Title']),Paragraph('CLASSROOM TEST ONLY - NOT AN OFFICIAL TRANSCRIPT',styles['Heading2'])]
    for text in [f'Profile: {student.full_name}',f'Participant: {enrollment.participant_id}',f'Template: {enrollment.template_id}',f'Fictional school: {record["fictional_school"]}',f'Programme: {record["programme"]}',f'Field: {record["field"]}']:
        story.append(Paragraph(escape(text),styles['Normal']))
    story.append(Spacer(1,18));index=int(enrollment.template_id[1:])-1;marks=MARKS[index]
    rows=[['Fictional course','Credits','Mark /100','Grade','Points']]
    for course,mark in zip(COURSES[record['field']],marks):
        g,gp=grade(mark);rows.append([course,3,mark,g,gp])
    table=Table(rows,colWidths=[215,50,75,50,50]);table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'StudyVera'),('FONTNAME',(0,0),(-1,0),'StudyVeraBold'),('GRID',(0,0),(-1,-1),.4,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('FONTSIZE',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]));story.append(table);story.append(Spacer(1,18))
    points=sum(grade(m)[1]*3 for m in marks)
    assert round(points/18,2)==record['cgpa']
    for text in [f'Total credits: 18. Weighted grade points: {points}.',f'Simulated CGPA: {record["cgpa"]:.2f} / 5.00','Study rubric: A 70-100 = 5 points; B 60-69 = 4; C 50-59 = 3; D 45-49 = 2; E 40-44 = 1; F 0-39 = 0. CGPA = weighted grade points / total credits.','All profile details, grades and institution labels are fictional. This record is not a qualification, verified institutional result or credential. Do not use it for admissions, employment or real academic decisions.']:
        story.append(Paragraph(escape(text),styles['Normal']));story.append(Spacer(1,10))
    SimpleDocTemplate(buffer,pagesize=A4,leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=40).build(story)
    return buffer.getvalue()
