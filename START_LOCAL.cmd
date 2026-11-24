@echo off
cd /d "%~dp0"
start "RankAfrica Backend" /D "%~dp0" cmd /k CALL tools\start_backend.cmd
start "RankAfrica Frontend" /D "%~dp0" cmd /k CALL tools\start_frontend.cmd
echo Keep both new windows open. First startup installs dependencies.
echo When both servers are ready, open http://localhost:5173
pause
