# RankAfrica all in one corrected system

This folder is the complete runnable source. All earlier source updates are already merged. You do not need any other ZIP or patch.

Start with **START_HERE.md**. On Windows, **START_LOCAL.cmd** launches both servers. Python 3.11 or 3.12 and Node.js 22 LTS are the documented prerequisites; first startup installs dependencies using internet access. Open http://localhost:5173 once both servers are ready.

## Included features
- Original logo, assets, design and core platform workflows.
- Open registration with required real name and student ID, without invitation codes or a ten-account limit. Student IDs stay private to the owner/facilitator.
- Ten assigned fictional school/grade profiles, automatic academic scoring and rankings; transcript upload is not required.
- Three fictional universities and Technology, Engineering and Law profiles.
- Account-specific synthetic PDF transcripts and ten editable Word examples with blank names.
- Independent, private-by-default public and recruiter discovery choices.
- Chosen photo upload with protected image access; photos appear beside rankings only with saved photo sharing for that audience.
- Separately optional biography and portfolio disclosure; emails and transcript contents excluded from discovery.
- Saved-choice previews, withdrawal and separately authorized opportunity applications.
- Original seven-question task questionnaire and separate logout questionnaire (three True/False questions, four 1–5 likelihood ratings, name, student ID and General comment).
- Administrator Class review, identified response exports, optional email delivery and controlled student cleanup.
- Local screenshot/test checklist and separate new Railway deployment/submission instructions.

## Responses without email
Email setup is not necessary. In Administrator > Class review, inspect the respondent's name/student ID/general comment and download identified exit reviews for all individual answers. Real email delivery is optional and requires configured sender credentials; see EXIT_QUESTIONNAIRE_SETUP.md.

## Verification and limits
43 backend tests and the frontend production build passed. Logs are under submission/. Existing-database upgrade testing preserved the prior student count. Automated tests are not observed Windows, actual-phone or live Railway tests. Complete LOCAL_TEST_CHECKLIST.md before the participant study. Do not claim synthetic academic scores are a validated cross-institution measure of real student ability.

## Files
- START_HERE.md: local startup and fictional role logins.
- SYSTEM_AND_PRIVACY.md: current system behavior and privacy boundaries.
- EXIT_QUESTIONNAIRE_SETUP.md: logout review and optional email.
- LOCAL_TEST_CHECKLIST.md: practical checks and screenshot prompts.
- NEW_RAILWAY_DEPLOYMENT.md: new hosting copy and submission guidance.
- CLASSROOM_ALLOCATION.csv: matching P01–P10 schools/programmes/grades.
- submission/word_transcripts_blank_names/: ten editable Word transcripts.
- submission/synthetic_transcript_examples/: ten PDF examples; students download their own account-specific PDF under Study tasks.
- reference_previous_drafts/: superseded historical documents; do not use old dataset/evaluation claims as current evidence.

No live GitHub repository or Railway service was changed. No local database, participant responses, private uploads, .env or SMTP secrets are shipped. The fictional demonstration staff/schools/recruiters initialize automatically; no student accounts initialize by default.
