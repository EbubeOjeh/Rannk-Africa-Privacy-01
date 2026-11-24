# Rank Africa privacy assessment prototype

Corrected local demonstration derived from the supplied Rank Africa source.
Original Logo.jsx, global styling, branding assets and existing page shells are retained.
New privacy screens use the existing cards, buttons, colours and typography.
Discovery profile content is intentionally limited to the proposal's allowed fields.

## Start in VS Code (Windows PowerShell)
Install Python 3.11 and Node.js 22 LTS. Extract the ZIP and open this folder in VS Code.
Do not open index.html using the Live Server extension: this is React/Vite + FastAPI.

Terminal 1, from this folder:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Terminal 2, from this folder:

```powershell
cd frontend
Copy-Item .env.example .env
npm ci
npm run dev
```

Open http://localhost:5173. API documentation: http://localhost:8000/docs.
Keep both terminals open. Ctrl+C stops a server. Script shortcuts are also included:
`powershell -File .\start-backend.ps1` and `powershell -File .\start-frontend.ps1`.
If PowerShell blocks scripts, use the explicit terminal commands above.

macOS/Linux backend: `python3.11 -m venv .venv`, then `.venv/bin/python -m pip install -r requirements.txt`
and `.venv/bin/python -m uvicorn app.main:app --reload --port 8000` from backend.
Frontend commands are the same, except use `cp .env.example .env`.

## Fictional demonstration accounts
Default password for these seed accounts: `DemoPrivacy2026!`.
For hosting, set DEMO_PASSWORD to a private password BEFORE the first startup.
Changing DEMO_PASSWORD later does not change passwords already stored in the database.

| Account | Email | Destination |
|---|---|---|
| Student 1 | student01@rankafrica.example | /student/privacy |
| Other students | student02@rankafrica.example through student12@rankafrica.example | /student |
| Recruiter 1 | recruiter1@rankafrica.example | /employer/search and /employer/applications |
| Recruiter 2 | recruiter2@rankafrica.example | /employer/applications |
| Unapproved recruiter | pending@rankafrica.example | discovery denied |
| School 1 | school1@rankafrica.example | /school |
| Schools 2 and 3 | school2@rankafrica.example, school3@rankafrica.example | /school |
| Administrator | admin@rankafrica.example | /admin |

There are 12 fictional students, 3 fictional schools and 6 fictional opportunities.
All discovery and optional consent choices start OFF. The public leaderboard is
therefore empty initially. Academic eligibility is enabled for the seed students,
but it never supplies discovery consent. Student 01 belongs to School 1.
These accounts are not marked as expiring legacy test accounts.

Refresh requires sign-in again because authentication is held in memory. Saved
privacy choices and application snapshots remain in SQLite. Use different browsers
or private sessions for each role; do not reload to switch roles.

## Main demonstration
1. Sign in as student01, open My Profile > Privacy (or Privacy in the navigation).
2. Enable only recruiter discovery and biography, then Save. Inspect saved previews.
3. As a public visitor, the profile remains unavailable. As recruiter1, it appears.
4. Save the candidate as recruiter1. Withdraw recruiter discovery as student01.
   Refresh the recruiter search, saved list and known profile URL: they no longer disclose it.
5. With all discovery OFF, browse Opportunities as student01. Click Apply.
   Review the named recipient and core fields. Leave extras unchecked, confirm, send.
6. Open Applications as the named recruiter. Recruiter2 must not see Recruiter1's application.
7. Change the live biography and repeat an application: the original snapshot is retained.
8. School1 can release/withdraw only its own roster; school2 cannot operate on student01.
9. Follow submission/MANUAL_TEST_REGISTER.csv for the remaining walkthrough evidence.

## Automated checks
From backend:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q --disable-warnings
```

From frontend: `npm run build`.
The supplied result logs are development-environment evidence, not your own walkthrough results.
The test database is temporary and isolated; the normal demonstration database is not reset.
LOCAL_STARTUP_SMOKE.txt records a separate in-process startup/restart check. To repeat it, copy
frontend/dist to frontend_dist at the project root after building, then run tools/local_smoke_check.py
using the backend virtual-environment Python from the project root. This is not a Docker or hosted check.

## Hosting and lecturer hand-in
Read HOSTING_AND_SUBMISSION.md and the documents in submission/.
A Dockerfile and render.yaml provide one-service hosting: React build + FastAPI + SQLite.
A working public assessment link must be copied from the successful hosting deployment;
none has been deployed by this package. Never submit localhost as an internet link.

## Scope and limitations
This is a bounded fictional academic prototype, not a production privacy/security certification.
AI scoring and SMTP are off by default. Scores are illustrative. Direct contact relay is disabled.
The privacy policy router is registered first to override legacy discovery and application reads.
Legacy staff management screens are retained; they are not a read-only assessor role.
Public profiles intentionally omit old score breakdowns, CVs, contact details and achievements
because those are outside the proposal's discovery fields. Owners retain the profile builder.
Saved preview responses share the same disclosure function as audience profile responses.
Archived discovery uses current permitted fields and scores for archived member IDs, not a frozen
historical profile. Withdrawal cannot recall copies already received by a visitor.
Application snapshots are retained until a deliberate demo database reset; automatic retention/deletion
is not implemented. New uploads use protected local storage; public Supabase uploads are disabled.
Public external photo/portfolio links may be independently accessible outside this prototype.
Browser visual and keyboard walkthroughs and a real hosting restart test must be recorded by the team.

## Source reuse
Original source supplied by the user; preserve existing author attribution. The original repository's
license is an unresolved placeholder, so do not represent it as a confirmed MIT licence.
Disclose AI-assisted code/document preparation according to your course policy and explain
what each team member reviewed, implemented and evaluated.
