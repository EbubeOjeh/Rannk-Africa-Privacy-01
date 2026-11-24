"""Short exit questionnaire and explicit, authenticated email delivery."""
import smtplib,ssl
from email.message import EmailMessage
from app.core.config import settings
QUESTIONS=[
 {'question':'Before I enabled public discovery, my profile was hidden from public rankings.','options':['True','False','Not sure']},
 {'question':'The public profile showed only the optional information I chose to share.','options':['True','False','Not sure / not tested']},
 {'question':'I could stop public discovery by switching it off and saving.','options':['True','False','Not sure / not tested']},
 {'question':'How likely are you to choose who sees your profile without needing help?','options':['1 Very unlikely','2 Unlikely','3 Neither likely nor unlikely','4 Likely','5 Very likely','Not tested']},
 {'question':'How likely are you to trust the system to show only your saved sharing choices?','options':['1 Very unlikely','2 Unlikely','3 Neither likely nor unlikely','4 Likely','5 Very likely','Not tested']},
 {'question':'How likely are you to withdraw public sharing successfully without help?','options':['1 Very unlikely','2 Unlikely','3 Neither likely nor unlikely','4 Likely','5 Very likely','Not tested']},
 {'question':'How likely are you to recommend these privacy controls to another student?','options':['1 Very unlikely','2 Unlikely','3 Neither likely nor unlikely','4 Likely','5 Very likely','Not tested']},
]
CONSENT='I agree to submit my name, student ID, answers and review to the facilitator for this classroom evaluation and have them emailed to the configured facilitator recipient. This is separate from public and recruiter sharing. I may log out without submitting.'
def mail_ready():
    return bool(settings.EXIT_FEEDBACK_RECIPIENT.strip() and settings.SMTP_HOST.strip())
def send_response(row):
    if not mail_ready():return 'not_configured'
    body=[f'Participant: {row.participant_id}',f'Name: {row.respondent_name}',f'Student ID: {row.student_identifier}','']
    for i,(q,a) in enumerate(zip(QUESTIONS,row.answers),1):body.extend([f'{i}. {q["question"]}',a or 'Unanswered',''])
    body.extend(['General privacy review:',row.general_review or '(No review provided)','',row.consent_text])
    msg=EmailMessage();msg['From']=settings.SMTP_FROM;msg['To']=settings.EXIT_FEEDBACK_RECIPIENT
    msg['Subject']=f'RankAfrica privacy exit review {row.participant_id}'
    msg.set_content('\n'.join(body))
    try:
        context=ssl.create_default_context()
        if settings.SMTP_USE_SSL:
            server=smtplib.SMTP_SSL(settings.SMTP_HOST,settings.SMTP_PORT,timeout=10,context=context)
        else:
            server=smtplib.SMTP(settings.SMTP_HOST,settings.SMTP_PORT,timeout=10)
        with server:
            server.ehlo()
            if not settings.SMTP_USE_SSL:server.starttls(context=context);server.ehlo()
            if settings.SMTP_USER:server.login(settings.SMTP_USER,settings.SMTP_PASSWORD)
            server.send_message(msg)
        return 'sent'
    except Exception:
        # Do not log names, student IDs, message content or SMTP credentials.
        return 'failed'
