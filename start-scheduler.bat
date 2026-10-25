@echo off
REM NGAME-CM scheduler — repository root. Starts at sign-in. Not a daily Task Scheduler job.
REM Double-click to test; for sign-in auto-start prefer start-scheduler-silent.vbs in shell:startup.
cd /d "%~dp0"
if not exist "logs" mkdir logs
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set NGAME_UNATTENDED=1
"%~dp0.venv\Scripts\pythonw.exe" "%~dp0ngame_scheduler.py" >> "%~dp0logs\scheduler.log" 2>> "%~dp0logs\scheduler.err.log"
