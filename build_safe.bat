@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo Gr8 DIY 빌드 스크립트 (영문 경로 우회)
echo ============================================

REM 영문 임시 빌드 경로
set BUILD_PATH=C:\Temp\gr8diy_build
set CURRENT_PATH=%~dp0

echo 현재 경로: %CURRENT_PATH%
echo 빌드 경로: %BUILD_PATH%

REM 기존 빌드 폴더 삭제
if exist "%BUILD_PATH%" (
    echo 기존 빌드 폴더 삭제 중...
    rmdir /s /q "%BUILD_PATH%"
)

REM 임시 폴더 생성 및 프로젝트 복사
echo 프로젝트 복사 중...
mkdir "%BUILD_PATH%"
xcopy /E /I /Y /Q "%CURRENT_PATH%app" "%BUILD_PATH%\app"
xcopy /E /I /Y /Q "%CURRENT_PATH%api" "%BUILD_PATH%\api"
xcopy /E /I /Y /Q "%CURRENT_PATH%config" "%BUILD_PATH%\config"
xcopy /E /I /Y /Q "%CURRENT_PATH%database" "%BUILD_PATH%\database"
xcopy /E /I /Y /Q "%CURRENT_PATH%indicators" "%BUILD_PATH%\indicators"
xcopy /E /I /Y /Q "%CURRENT_PATH%ui" "%BUILD_PATH%\ui"
xcopy /E /I /Y /Q "%CURRENT_PATH%utils" "%BUILD_PATH%\utils"
xcopy /E /I /Y /Q "%CURRENT_PATH%workers" "%BUILD_PATH%\workers"
xcopy /E /I /Y /Q "%CURRENT_PATH%env" "%BUILD_PATH%\env"

echo 프로젝트 복사 완료!

REM 빌드 경로로 이동
cd /d "%BUILD_PATH%"

REM 환경 설정
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM PyInstaller 실행
echo 빌드 시작...
"%BUILD_PATH%\env\Scripts\python.exe" -m PyInstaller ^
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
    --distpath "%BUILD_PATH%\dist" ^
    --workpath "%BUILD_PATH%\build" ^
    app\main.py

if %ERRORLEVEL% EQU 0 (
    echo ============================================
    echo 빌드 성공!
    echo ============================================
    
    REM 결과물을 원래 경로로 복사
    echo 결과물 복사 중...
    if exist "%CURRENT_PATH%dist" rmdir /s /q "%CURRENT_PATH%dist"
    xcopy /E /I /Y /Q "%BUILD_PATH%\dist" "%CURRENT_PATH%dist"
    
    echo ============================================
    echo 결과물: %CURRENT_PATH%dist\Gr8 DIY\
    echo ============================================
) else (
    echo ============================================
    echo 빌드 실패! 에러 코드: %ERRORLEVEL%
    echo 임시 빌드 폴더: %BUILD_PATH%
    echo ============================================
)

REM 원래 경로로 복귀
cd /d "%CURRENT_PATH%"

pause

