# Create a separate new Railway deployment

Keep the old service and database intact. Test locally first.

1. Agree your actual study contact, retention/deletion date and withdrawal process with your lecturer.
2. Create a NEW private GitHub repository without an initial README. In this extracted source root run one command at a time, substituting your new repository URL:
```
git init
git add .
git commit -m "Corrected open classroom privacy study"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-NEW-REPOSITORY.git
git push -u origin main
```
The .gitignore excludes .env, databases, uploads, virtual environments and node_modules. Never commit real student information, passwords or feedback exports.
3. Create a NEW Railway project/service from that GitHub repository. Use the repository ROOT, where the Dockerfile is. The Dockerfile builds the React frontend and serves it with the backend on one domain.
4. Attach a NEW persistent volume mounted at `/var/data`. Do not reuse the old service's volume. SQLite needs persistent storage across deployments. Use one replica; the Dockerfile uses one worker. Check your account's current Railway plan, volume availability and charges; free hosting is not promised.
5. Set variables BEFORE the first successful startup:

| Variable | Value |
|---|---|
| DATABASE_URL | sqlite:////var/data/rankafrica.db |
| UPLOAD_DIR | /var/data/uploads |
| SECRET_KEY | A new long random secret |
| DEMO_PASSWORD | A new private strong password for seeded staff/recruiters |
| AUTO_SEED | true |
| INIT_DB_ON_STARTUP | true |
| SEED_DEMO_STUDENTS | false |
| ENABLE_STUDENT_CLEANUP | false |
| AI_ENABLED | false |
| APP_ENV | assessment |
| APP_DEBUG | false |
| STUDY_CONTACT | Your real approved facilitator contact |
| STUDY_RETENTION_NOTICE | Your actual agreed retention period and withdrawal instructions |
| PORT | 8000 |

Registration in assessment mode is blocked until contact and retention information are set. DEMO_PASSWORD affects first creation only, not existing account passwords. No email service is needed for generated classroom logins.
6. Deploy. Set health check path `/health`. Generate a public domain for port 8000 in service networking. Single-domain requests use relative API URLs. Set CORS_ORIGINS to the exact HTTPS origin if cross-origin requests are required.
7. Test the new domain, administrator login, initial zero students, registration, PDF download, public/recruiter consent, withdrawal and questionnaire. Repeat on an actual phone. Local tests do not prove hosted or phone behavior.
8. If you created preliminary test accounts, use the administrator preview-and-confirm cleanup before real participants begin; see SYSTEM_AND_PRIVACY.md. Disable cleanup afterwards.
9. Send classmates **https://YOUR-DOMAIN/student-register** and assign templates using CLASSROOM_ALLOCATION.csv. Anyone with the link can register, with no invitation code or ten-person limit. Count only your ten agreed participants in the study; record any extra accounts/exclusions.

Later pushes to the connected branch rebuild automatically when automatic deployment is enabled. Live consent changes are saved to the LIVE database and need no GitHub push. Local consent does not copy to Railway. Closing your local folder/computer does not stop the hosted service; availability depends on deployment, account limits and storage. Back up before destructive cleanup.

## Submit
Add the new live URL, tested date, your own screenshots and actual participant results to your report. Export the report to PDF. Zip source without .env, database, uploads, .venv or node_modules; submit source ZIP, report and live URL through your lecturer's specified channel. Do not submit passwords or identifiable feedback publicly.

## Latest consolidated features
The complete package already includes chosen-photo sharing, General comment and identified logout reviews. No separate patch ZIP is needed. Use Administrator > Class review without email configuration; identified exit-review exports contain name, student ID, all answers and comments. If email is desired later, configure the optional sender/recipient variables in EXIT_QUESTIONNAIRE_SETUP.md.
