@echo off
cd /d "%~dp0..\backend"
if exist .venv\Scripts\python.exe goto install
py -3.11 -m venv .venv
if exist .venv\Scripts\python.exe goto install
py -3.12 -m venv .venv
if exist .venv\Scripts\python.exe goto install
python -c "import sys; assert sys.version_info[:2] in [(3,11),(3,12)]" && python -m venv .venv
if not exist .venv\Scripts\python.exe (
echo Install Python 3.11 or 3.12 with Add Python to PATH selected, then retry.
exit /b 1
)
:install
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe ..\tools\prepare_local.py
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
