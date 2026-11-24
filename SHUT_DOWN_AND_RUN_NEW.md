# Stop the old servers and run this complete copy

1. Find each old Backend/Frontend command window. Press Ctrl+C in both. If asked Terminate batch job (Y/N), type Y. Keep your old project folder if you need its saved data.
2. In PowerShell check for remaining listeners:
```powershell
Get-NetTCPConnection -LocalPort 5173,8000 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalPort,OwningProcess
```
3. If no rows are returned, both ports are free. If a row appears, note its OwningProcess number. Check that process first:
```powershell
Get-Process -Id 12345
```
Replace 12345 with the actual number. If it is the old Node frontend or Python backend, stop that process:
```powershell
Stop-Process -Id 12345
```
Repeat for the other old listener if necessary. Do not type the example number literally or stop an unrelated application. This stops the server process and does not delete accounts or project files.
4. Fully extract RankAfrica-All-In-One-Name-and-ID.zip into a NEW folder. Open the contained RankAfrica-Final folder where START_LOCAL.cmd is visible. Do not run an earlier project's launcher.
5. Double-click START_LOCAL.cmd, or open a VS Code terminal in that same folder and run:
```powershell
cmd /c START_LOCAL.cmd
```
6. First launch installs dependencies. Wait for backend port 8000 and frontend port 5173; keep both windows open. Open http://localhost:5173 and refresh the page. Register at http://localhost:5173/student-register.
7. Admin login is admin@rankafrica.example with local password DemoPrivacy2026!. The fresh folder starts with zero students and does not import your old copy's accounts. Everything is included; no earlier patch or CV is needed. Email is optional: responses can be reviewed/exported in Administrator > Class review.

Python 3.11 or 3.12 and Node.js are required. The launcher selects Python 3.11 first, then 3.12. First dependency installation needs internet access. Do not use VS Code Live Server for this application.
