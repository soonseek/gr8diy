@echo off
chcp 65001 > nul
cls
echo ========================================
echo Gr8 DIY Starting...
echo ========================================
echo.

REM 프로젝트 루트로 이동
cd /d "%~dp0\.."

REM 가상환경 확인
if not exist "env\Scripts\activate.bat" (
    color 0C
    echo [ERROR] Virtual environment not found.
    echo.
    echo Please run: 0_fix_installation_error.bat
    echo.
    pause
    exit /b 1
)

REM 가상환경 활성화
echo [INFO] Activating virtual environment...
call env\Scripts\activate.bat
echo.

REM 앱 실행
echo [INFO] Starting application...
echo.
echo ========================================
echo.
env\Scripts\python.exe app\main.py

REM 종료 처리
echo.
echo ========================================
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Application terminated with error.
    echo Error code: %errorlevel%
    echo.
    echo Check TROUBLESHOOTING.md for help.
) else (
    color 0A
    echo [SUCCESS] Application closed normally.
)
echo ========================================
echo.
pause

