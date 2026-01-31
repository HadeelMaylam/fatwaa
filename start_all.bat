@echo off
echo ====================================
echo Starting Fatwa RAG Full Stack
echo ====================================
echo.

REM Start Backend in new window
echo [1/2] Starting Backend (FastAPI)...
start "Backend - FastAPI" cmd /k "venv\Scripts\activate && uvicorn app.main:app --reload"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo [2/2] Starting Frontend (Next.js)...
start "Frontend - Next.js" cmd /k "cd frontend && npm run dev"

echo.
echo ====================================
echo System Started!
echo ====================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:3000

echo.
echo To stop: Close the Backend and Frontend windows
echo.
