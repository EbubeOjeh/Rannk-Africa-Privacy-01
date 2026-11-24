@echo off
cd /d "%~dp0..\frontend"
where node >nul 2>nul
if errorlevel 1 (
echo Install Node.js 22 LTS, reopen the launcher, and retry.
exit /b 1
)
if exist node_modules\.package-lock.json goto run
call npm.cmd ci
if errorlevel 1 exit /b 1
:run
call npm.cmd run dev -- --host 127.0.0.1 --port 5173 --strictPort
