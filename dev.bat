@echo off
REM ---------------------------------------------------------------------------
REM dev.bat - start the backing services (Postgres + FastAPI) for development.
REM The frontend is intentionally NOT started here so you can run it with
REM hot-reload yourself:
REM
REM     cd frontend
REM     npm install   (first time only)
REM     npm run dev
REM ---------------------------------------------------------------------------

setlocal

REM Run from this script's directory regardless of where it was invoked.
cd /d "%~dp0"

REM Create .env from the template on first run so docker compose has its vars.
if not exist ".env" (
    echo No .env found - creating one from .env.example
    copy ".env.example" ".env" >nul
    echo.
    echo   ^>^> Edit .env and set your AZURE_OPENAI_* values before generating posts.
    echo.
)

echo Starting db + backend (Ctrl+C to stop)...
docker compose up --build db backend

endlocal
