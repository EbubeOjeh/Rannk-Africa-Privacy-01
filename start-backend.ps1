Set-Location "$PSScriptRoot/backend"
if (!(Test-Path .venv)) { py -3.11 -m venv .venv }
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& ./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
