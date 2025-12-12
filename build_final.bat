@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo Gr8 DIY 최종 빌드 스크립트
echo ============================================
echo.

set BUILD_DIR=C:\Temp\gr8diy
set CURRENT_DIR=%~dp0
set CURRENT_DIR=%CURRENT_DIR:~0,-1%

echo [1/5] 기존 빌드 폴더 정리...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%" 2>nul
mkdir "%BUILD_DIR%"

echo [2/5] 프로젝트 복사 중 (robocopy)...
robocopy "%CURRENT_DIR%" "%BUILD_DIR%" /E /NFL /NDL /NJH /NJS /NC /NS /NP /XD __pycache__ .git build dist >nul

if %ERRORLEVEL% GEQ 8 (
    echo 복사 실패! 에러코드: %ERRORLEVEL%
    pause
    exit /b 1
)

echo [3/5] 빌드 환경 설정...
cd /d "%BUILD_DIR%"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo [4/5] PyInstaller 빌드 시작...
"%BUILD_DIR%\env\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --name "Gr8 DIY" ^
    --windowed ^
    --add-data "env\Lib\site-packages\PySide6\plugins\platforms;PySide6/plugins/platforms" ^
    --add-data "env\Lib\site-packages\PySide6\plugins\sqldrivers;PySide6/plugins/sqldrivers" ^
    --add-data "env\Lib\site-packages\PySide6\plugins\styles;PySide6/plugins/styles" ^
    --add-data "env\Lib\site-packages\PySide6\plugins\imageformats;PySide6/plugins/imageformats" ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtSql ^
    --hidden-import=PySide6.QtNetwork ^
    --hidden-import=qfluentwidgets ^
    --hidden-import=cryptography ^
    --hidden-import=cryptography.fernet ^
    --hidden-import=requests ^
    --hidden-import=numpy ^
    --hidden-import=pandas ^
    --hidden-import=markdown ^
    --exclude-module=PyQt5 ^
    --exclude-module=PyQt6 ^
    --exclude-module=PySide2 ^
    --exclude-module=tkinter ^
    --exclude-module=matplotlib ^
    --exclude-module=scipy ^
    app\main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo 빌드 실패! 에러 코드: %ERRORLEVEL%
    echo 빌드 폴더: %BUILD_DIR%
    echo ============================================
    cd /d "%CURRENT_DIR%"
    pause
    exit /b %ERRORLEVEL%
)

echo [5/5] 결과물 복사...
if exist "%CURRENT_DIR%\dist" rmdir /s /q "%CURRENT_DIR%\dist"
robocopy "%BUILD_DIR%\dist" "%CURRENT_DIR%\dist" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul

echo.
echo ============================================
echo 빌드 성공!
echo 결과물: %CURRENT_DIR%\dist\Gr8 DIY\
echo ============================================

cd /d "%CURRENT_DIR%"
pause


