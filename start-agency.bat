@echo off
title AI Agent Agency - Autonomous Command Center
cd /d "%~dp0"
echo ===================================================================
echo   🏢 AI AGENT AGENCY (agency_master) - LangGraph Edition
echo ===================================================================
echo.

echo [1/3] Checking PostgreSQL Database Service...
sc query postgresql-x64-18 | findstr /i "RUNNING" >nul
if %errorlevel% neq 0 (
    echo Starting PostgreSQL service...
    net start postgresql-x64-18 >nul 2>&1
) else (
    echo PostgreSQL service is already RUNNING.
)

echo.
echo [2/3] Starting Background Auto-Scheduler Daemon in separate window...
start "AI Agency Auto-Scheduler Daemon" cmd /k "title AI Agency Daemon & python scheduler_daemon.py"

echo.
echo [3/3] Starting FastAPI + LangGraph Web Dashboard Server...
echo Opening Web Dashboard in your default browser...
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000/"

python run_server.py
pause

