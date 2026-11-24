# Run the complete all in one system locally on Windows

All discussed updates are already included. No separate patch is needed. Email is optional: use Administrator > Class review to review and export responses.

1. Extract the ZIP fully into a NEW folder, preferably C:\Projects\RankAfrica-Final. Do not merge into the old project or run inside the ZIP.
2. Install Python **3.11 or 3.12** (select Add Python to PATH) and Node.js **22 LTS**, if missing. First dependency installation needs internet access.
3. In VS Code choose File > Open Folder and select the folder containing START_LOCAL.cmd.
4. In Windows File Explorer, double-click **START_LOCAL.cmd**. Two command windows open. These .cmd launchers avoid PowerShell's script execution restriction.
5. Wait for the backend to show port 8000 and the frontend port 5173; installation can take several minutes the first time.
6. Open **http://localhost:5173**. Do not use Live Server: both React and the Python API must run.
7. Register a student at **http://localhost:5173/student-register**. Enter your real name and student ID, select a fictional academic profile and choose a password. No invitation code is needed. Save the generated login shown under Study tasks: it looks like an email but is not a working inbox. There is no ten-account cap.
8. Administrator login at http://localhost:5173/login: **admin@rankafrica.example**, password **DemoPrivacy2026!**. These are local demonstration credentials.
9. Follow LOCAL_TEST_CHECKLIST.md. To stop, press Ctrl+C in both server windows. Closing VS Code alone may leave them running. Restarting preserves your data.

A fresh copy creates three fictional schools, demonstration staff/recruiters and opportunities, but ZERO student accounts. Data is stored in backend/rankafrica.db. No existing database is erased. Do not copy your old .env or database into this new folder.

If ports are in use, stop the old servers. If Python is missing, install the specified runtime first; the launcher cannot execute Python without it. Reopen VS Code/the launcher after installing runtimes.

## Manual/non-Windows start
Create a Python 3.11/3.12 virtual environment at backend/.venv and activate it. Run `pip install -r backend/requirements.txt` from the root, then `python tools/prepare_local.py`. Inside backend run `python -m uvicorn app.main:app --port 8000`. In a second terminal inside frontend run `npm ci` then `npm run dev -- --port 5173 --strictPort`.

Localhost is visible only on your own computer. After local testing, follow NEW_RAILWAY_DEPLOYMENT.md and send classmates the hosted HTTPS registration link.

## Other fictional roles
School reviewers: school1@rankafrica.example, school2@rankafrica.example and school3@rankafrica.example. Approved recruiters: recruiter1@rankafrica.example and recruiter2@rankafrica.example. Pending recruiter: pending@rankafrica.example. All use the local demonstration password above. They are fictional test accounts, not your classmates. Hosted first-start passwords use your DEMO_PASSWORD variable.

The ten template PDF examples are in submission/synthetic_transcript_examples. Participants should download their account-specific PDF from Study tasks so the generated participant ID matches.

For the optional logout review and email setup, see EXIT_QUESTIONNAIRE_SETUP.md. The original task questionnaire remains separate.

## Test the complete flow
Register P01, save your generated login, upload a chosen photo in My Profile, then enable selected public fields in Privacy and Save. Inspect rankings in a private browser window. Return as the student and click Sign out to complete the optional short exit review with name, student ID and General comment. Finish logging out, sign in as administrator and open Class review. Download identified exit reviews for each respondent's seven answers. No email configuration is necessary for this flow.

This fresh folder starts with a new, empty student dataset. It does not include trial accounts from your previous local copy or live Railway database. Keep your old folder if you need its data. If you intentionally transfer an existing local database/uploads, stop both copies first and retain a backup; do not run both systems against one SQLite database at once.
