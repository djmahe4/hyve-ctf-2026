@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   Hivye CTF 2026 - Windows Infrastructure Setup
echo ==========================================
echo.

:: Start CTFd
echo [*] Starting CTFd platform...
cd ctfd
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo [!] Failed to start CTFd.
    exit /b %ERRORLEVEL%
)
cd ..
echo     ^|-- CTFd started
echo.

:: Start challenges
echo [*] Starting challenge infrastructure...
cd deployment\docker
docker-compose -f docker-compose.challenges.yml up -d
if %ERRORLEVEL% neq 0 (
    echo [!] Failed to start challenges.
    exit /b %ERRORLEVEL%
)
cd ..\..
echo     ^|-- Challenge services started
echo.

echo ==========================================
echo   Infrastructure Ready!
echo ==========================================
echo.
echo Information:
echo   - CTFd Platform: http://localhost:8001
echo   - Web Challenges: http://localhost:8080
echo   - File Server: http://localhost:8081
echo.
echo Next step:
echo   Run: python setup_ctf.py
echo.
echo To stop all services: windows\stop.bat
echo ==========================================
pause
