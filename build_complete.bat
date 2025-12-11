@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo Gr8 DIY 완전 빌드 스크립트
echo (한글 경로 문제 완전 해결)
echo ============================================
echo.

set BUILD_DIR=C:\Temp\gr8diy_build
set CURRENT_DIR=%~dp0
set CURRENT_DIR=%CURRENT_DIR:~0,-1%

echo [1/7] 기존 빌드 폴더 정리...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%" 2>nul
mkdir "%BUILD_DIR%"

echo [2/7] 소스 코드 복사 중...
robocopy "%CURRENT_DIR%\app" "%BUILD_DIR%\app" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
robocopy "%CURRENT_DIR%\api" "%BUILD_DIR%\api" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
robocopy "%CURRENT_DIR%\config" "%BUILD_DIR%\config" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
robocopy "%CURRENT_DIR%\database" "%BUILD_DIR%\database" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
robocopy "%CURRENT_DIR%\indicators" "%BUILD_DIR%\indicators" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
robocopy "%CURRENT_DIR%\ui" "%BUILD_DIR%\ui" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
robocopy "%CURRENT_DIR%\utils" "%BUILD_DIR%\utils" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
robocopy "%CURRENT_DIR%\workers" "%BUILD_DIR%\workers" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
copy "%CURRENT_DIR%\requirements_build.txt" "%BUILD_DIR%\requirements.txt" >nul

echo [3/7] 가상환경 생성 중...
cd /d "%BUILD_DIR%"
python -m venv env
if %ERRORLEVEL% NEQ 0 (
    echo Python venv 생성 실패!
    pause
    exit /b 1
)

echo [4/7] 패키지 설치 중 (시간이 좀 걸립니다)...
"%BUILD_DIR%\env\Scripts\pip.exe" install --quiet --upgrade pip
"%BUILD_DIR%\env\Scripts\pip.exe" install --quiet -r requirements.txt
"%BUILD_DIR%\env\Scripts\pip.exe" install --quiet pyinstaller==5.13.2

echo [5/7] PyInstaller 빌드 시작...
"%BUILD_DIR%\env\Scripts\pyinstaller.exe" ^
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

echo [6/7] 결과물 복사...
if exist "%CURRENT_DIR%\dist" rmdir /s /q "%CURRENT_DIR%\dist"
robocopy "%BUILD_DIR%\dist" "%CURRENT_DIR%\dist" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul

echo [7/7] 정리...
cd /d "%CURRENT_DIR%"

echo.
echo ============================================
echo 빌드 성공!
echo 결과물: %CURRENT_DIR%\dist\Gr8 DIY\
echo 실행 파일: %CURRENT_DIR%\dist\Gr8 DIY\Gr8 DIY.exe
echo ============================================

pause

