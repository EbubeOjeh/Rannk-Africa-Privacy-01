# Hosting and lecturer submission

## Deployment status
NOT DEPLOYED. There is no verified public live link in this package.
The included Dockerfile packages frontend and backend into one web service.
Sites hosting runs Cloudflare Workers and cannot directly execute this Python/FastAPI application.
Use a Python/Docker host such as Render for the unchanged architecture.

## Option A: Render with a persistent disk
This option creates paid hosting resources. Review the provider's current prices before creating them.
Render free web services cannot attach persistent disks; keeping SQLite on their temporary filesystem
would lose saved choices/uploads across restarts or deployments. Do not use that arrangement as
persistent assessment hosting.

1. Create a new private GitHub repository. Upload the CONTENTS of RankAfrica-Corrected so
   Dockerfile, frontend/, backend/ and render.yaml are at the repository root. Keep .env,
   databases, uploads, .venv and node_modules out of Git; .gitignore is included.
2. Sign in to Render and connect that repository. Choose New > Web Service, select the
   repository and Docker runtime. Use the repository root and included Dockerfile.
3. Select a paid web service plan that supports a disk. Add a persistent disk mounted at
   /var/data (the supplied blueprint uses 1 GB). Use one instance and one worker for SQLite.
4. Add these environment variables before the first deployment:
   DATABASE_URL=sqlite:////var/data/rankafrica.db
   UPLOAD_DIR=/var/data/uploads
   AUTO_SEED=true
   INIT_DB_ON_STARTUP=true
   AI_ENABLED=false
   APP_ENV=assessment
   APP_DEBUG=false
   SECRET_KEY=<long random secret, generated privately>
   DEMO_PASSWORD=<private demonstration password for the seed accounts>
   Do not set Supabase credentials. Do not add real student information.
5. Set the health-check path to /health. Keep the Docker start command from the Dockerfile;
   it binds to 0.0.0.0 and Render's PORT. No separate static-site deployment is needed.
6. Deploy. Wait for the service to be Live. Open the exact HTTPS address Render supplies.
   Test the home page and /health, sign in and open /student/privacy.
7. Copy that actual HTTPS address to submission/SUBMISSION_DETAILS.txt and the report's
   Project access section. Do not copy localhost, a dashboard URL, or a build-log URL.
8. Verify on another device/network with your development laptop off. Save a consent choice,
   submit a fictional application and upload a fictional photo. Restart the hosted service;
   sign in again and verify that all three persist. Record the date and actual observations.
9. Share student and recruiter credentials privately through the lecturer's agreed channel.
   Avoid sharing the super-admin password unless the assessment requires it. Keep the service
   available for the agreed marking window. Do not reset the database during marking.

Alternative: Render > New > Blueprint can read render.yaml. It requests DEMO_PASSWORD and
creates a paid starter web service plus disk. Inspect the proposed resources and charges before
accepting. The manual route above makes every setting reviewable.

Official references, checked 14 November 2026:
https://render.com/docs/docker
https://render.com/docs/web-services
https://render.com/docs/disks
https://render.com/docs/free

## Option B: local Docker verification before hosting
Install Docker Desktop from its official source and start it. From the project root:

```powershell
docker build -t rankafrica-privacy .
docker volume create rankafrica-data
docker run --rm -p 8000:8000 -v rankafrica-data:/var/data -e DATABASE_URL=sqlite:////var/data/rankafrica.db -e UPLOAD_DIR=/var/data/uploads -e SECRET_KEY=replace-with-your-own-random-secret -e DEMO_PASSWORD=choose-a-private-demo-password rankafrica-privacy
```

Open http://localhost:8000. This local address is not a hosted assessment link.
The named Docker volume keeps data after the container stops. These Docker commands have not
been executed in the authoring environment; verify the image before deploying it.

## Prepare the lecturer ZIP
The delivered RankAfrica-Corrected.zip is already a clean source package. For your final hand-in:
1. Complete the team walkthrough register and defect log. Capture actual screenshots with no tokens.
2. Finish the report's names/student numbers, contribution record, live URL and actual results.
3. Keep runtime secrets out of the report. Deliver credentials separately.
4. Run the API tests and frontend build again on the exact submitted source.
5. From the project root, run `py -3.11 tools/package_submission.py` (or `python3 tools/package_submission.py`).
   It creates a sibling RankAfrica-Lecturer-Submission.zip and excludes environments, dependencies,
   .env secrets, databases, runtime uploads, cache folders and build output.
6. Extract that new ZIP into a fresh folder and follow README.md. Confirm it runs without relying
   on files from your original development folder.
7. Upload the ZIP, final report and presentation if requested to your course submission portal.
   Put the live URL and marking availability window in the submission text as well as the report.
   If using email instead, use the lecturer's verified address and comply with attachment limits.

Suggested portal message (replace the prompts):
Rank Africa privacy prototype — Ojeh Ebube and Naomi Pristyle, CIS*6550.
Live demonstration: [paste the actual verified HTTPS address]
Available until: [date and timezone]
Attached: source ZIP, report and required supporting evidence.
Role credentials: [state the separate private delivery method]
Local startup instructions are in README.md. The dataset is fictional and scores are illustrative.

## Before claiming completion
Hosted access and keyboard usability are NOT established by a successful build or API test suite.
Record blocked/unrun checks separately from passes. Do not invent screenshots or participant findings.
The proposal evaluates two team members' structured walkthroughs; it does not recruit classmates.
