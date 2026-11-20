@echo off
title AI Agent Agency - LangGraph Enterprise Control Center
cd /d "%~dp0"
echo ========================================================
echo   AI AGENT AGENCY (agency_master) - LangGraph Edition
echo ========================================================
echo.
echo Starting FastAPI + LangGraph Server on http://127.0.0.1:8000 ...
echo Opening Dashboard in browser in 2 seconds...
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000/"
python run_server.py
pause
