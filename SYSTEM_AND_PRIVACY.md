# Current system and privacy study

The supplied deployed-project ZIP is the base. Original logo, assets, styling, staff/recruiter workflows, opportunities and academic scoring engine are retained. The classroom path evaluates whether people understand and can operate privacy controls. It does not establish fair real-world inter-university ranking or authenticate transcripts.

## Registration and school matching
Anyone with the registration link can choose a template and password using their real name and student ID, without an invitation code, real email or transcript upload. The generated email-shaped login is not deliverable: save it and the password; email recovery is not configured. Multiple accounts can choose the same template. Ten templates are not a registration limit.

Assign P01-P04 Technology, P05-P07 Engineering and P08-P10 Law. CLASSROOM_ALLOCATION.csv lists the exact fictional school and CGPA. Demo Coast, Demo Hills and Demo River are fictional universities at the same tier. Registration links each account to its assigned school and automatically evaluates its synthetic academic record. Its downloadable PDF uses the same school, programme, profile and CGPA. Assigned academic fields and academic uploads are protected against participant changes.

Your ten real classmates supply usability observations, not genuine academic records. Do not request real academic documents. Students may optionally upload a chosen profile picture and choose whether each discovery audience receives it. Biography and portfolio are also separately optional. The registration name identifies the real participant; the school and grades remain fictional. The name is disclosed as a core profile field only when the relevant discovery audience is enabled. The student ID is stored in a separate private registration record and excluded from public and recruiter discovery. Participant IDs and free-text responses can still identify people indirectly: restrict exports and follow your agreed retention plan.

## Privacy controls
Public discovery and recruiter discovery both default OFF and are independent. Public visibility requires saved public consent plus academic eligibility and platform ranking release. Approved recruiters require separate recruiter discovery consent. Core discovery includes profile name, school, field and score; biography/photo/portfolio are separately optional. Email and transcript are excluded. Academic approval is not consent.

Unsaved checkbox changes do not alter disclosure. Withdrawing saved sharing stops future discovery. It does not delete previously authorized application snapshots. Students may browse opportunities and send separately confirmed fictional applications with discovery OFF. Only the named recipient with current approval can access that application; other recruiters cannot.

Records are pre-approved for the demonstration. The existing field-specific engine computes academic scores; AI and unassessed nonacademic components are not fabricated. AI is OFF, so scores may be partial. Do not present them as validated overall student ability or a validated comparison between real institutions.

## Evaluation and review
Student navigation includes Study tasks, Privacy and Questionnaire. Seven custom questions address registration, defaults, selective disclosure, private applications, saved choices, snapshot retention and withdrawal ease. An optional general review and separate response-submission consent are included; answers may be skipped. This is not a validated SUS instrument. No participant responses are generated.

Administrator > Class review lists participant IDs and submission status and exports response JSON. Report actual sample size/completions, extra registrations/exclusions and observed results. Template count does not equal evaluated participant count. The in-app form is authoritative; a printable fallback is in submission/.

## Administrator cleanup
Student cleanup is disabled by default. To use locally set ENABLE_STUDENT_CLEANUP=true in backend/.env and restart backend. The administrator previews either seeded_students (the original twelve exact demonstration email accounts only) or all_students (all Student-role accounts, including study participants). This fresh package creates none of those original twelve students.

Execution requires a current signed preview, the displayed exact phrase and backup acknowledgement. Related consents, enrollment, feedback, applications and ranking snapshots are removed. Staff, schools, recruiters and opportunities remain. Associated local uploads are attempted after commit and failures are reported. Backups, screenshots, earlier exports and external files are not automatically erased. Disable cleanup after use; follow the agreed process for actual participant data.

## Evidence and submission
43 backend tests passed and the production frontend build passed. Logs are in submission/FINAL_API_TEST_RESULTS.txt and FINAL_BUILD_RESULTS.txt. Coverage includes privacy, authorization, school/transcript matching, registration, response consent and cleanup. These are not observed Windows-launcher, hosted Railway or phone tests; use LOCAL_TEST_CHECKLIST.md for those.

No live repository, Railway service or database was changed. Historical drafts under reference_previous_drafts are superseded, including their old dataset counts. Add actual screenshots, participant findings, live URL, agreed study contact/retention details and course-required material to your final report. Do not describe planned features as observed evaluation results.

## Identified logout review
Students are also offered an optional short review when clicking logout: three True/False questions, four 1–5 likelihood ratings, general privacy review, name and student ID. This is a different questionnaire from the original task review. Name and student ID are required only to submit, with a separate agreement that the responses will be stored for the facilitator and emailed to the configured recipient. Students may log out without answering. Review identity is excluded from public and recruiter discovery. Responses are saved before SMTP delivery; failed/unconfigured delivery stays available to the administrator for retry. Actual inbox delivery requires working sender configuration. Existing email copies and exports are not recalled by database cleanup. See EXIT_QUESTIONNAIRE_SETUP.md.

Registration identity is visible to the super administrator in Class review, and pre-fills the identified logout questionnaire. It is linked to the original task-review export too. Automatic name/ID verification against university records is not provided. CV uploads remain disabled; CVs are not required. The stated after-grades deletion is a manual facilitator responsibility, not an automatic timer.
