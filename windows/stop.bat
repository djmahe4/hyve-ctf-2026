@echo off
setlocal enabledelayedexpansion

set REMOVE_DATA=false

:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="-rm" set REMOVE_DATA=true
if "%~1"=="--remove" set REMOVE_DATA=true
if "%~1"=="/rm" set REMOVE_DATA=true
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help
if "%~1"=="/?" goto show_help
shift
goto parse_args

:show_help
echo Usage: windows\stop.bat [OPTIONS]
echo.
echo Options:
echo   -rm, --remove, /rm    Remove all data (containers, volumes, team files)
echo   -h, --help, /?        Show this help message
exit /b 0

:end_parse

echo Stopping Hivye CTF 2026...
echo.

if "%REMOVE_DATA%"=="true" (
    echo [!] WARNING: This will remove all containers, volumes, and data!
    echo    - CTFd database (all users, teams, submissions)
    echo    - Generated team files
    echo.
    set /p confirm="Are you sure? (yes/no): "
    if /i "!confirm!" neq "yes" (
        echo Cancelled.
        exit /b 0
    )
    echo.
)

:: Stop CTFd
echo [*] Stopping CTFd platform...
cd ctfd
if "%REMOVE_DATA%"=="true" (
    docker-compose down -v
) else (
    docker-compose down
)
cd ..
echo     ^|-- CTFd stopped
echo.

:: Stop challenges
echo [*] Stopping challenge infrastructure...
cd deployment\docker
if "%REMOVE_DATA%"=="true" (
    docker-compose -f docker-compose.challenges.yml down -v
) else (
    docker-compose -f docker-compose.challenges.yml down
)
cd ..\..
echo     ^|-- Challenge services stopped
echo.

:: Remove generated team files if requested
if "%REMOVE_DATA%"=="true" (
    echo [*] Removing generated team files...
    if exist "challenges\teams" (
        rmdir /s /q "challenges\teams"
        echo     ^|-- Team files removed
    ) else (
        echo     ^|-- No team files to remove
    )
    echo.
    
    echo [*] Removing CTFd persistent data...
    if exist "ctfd\data" (
        rmdir /s /q "ctfd\data"
        echo     ^|-- CTFd data removed
    ) else (
        echo     ^|-- No CTFd data to remove
    )
    echo.
)

echo.
if "%REMOVE_DATA%"=="true" (
    echo All services stopped and data removed!
) else (
    echo All services stopped successfully!
    echo Data preserved. Use 'windows\stop.bat /rm' to remove all data.
)
echo.
pause
