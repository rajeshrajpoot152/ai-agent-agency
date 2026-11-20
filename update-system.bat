@echo off
title AI Agent Agency - Official LangGraph Auto-Updater
cd /d "%~dp0"
echo ========================================================
echo   Updating Official LangGraph & Core AI Engine...
echo ========================================================
echo.

echo Checking and pulling latest LangGraph releases from PyPI...
pip install --upgrade langgraph langchain-core langchain-google-genai fastapi uvicorn

echo.
echo ========================================================
echo [SUCCESS] LangGraph and dependencies updated to latest version!
echo ========================================================
echo.
pause
