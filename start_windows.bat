@echo off
REM Double-click to start the Copilot Agent Builder training app.
cd /d "%~dp0"
where py >nul 2>nul && (py -3 app.py %*) || (python app.py %*)
pause
