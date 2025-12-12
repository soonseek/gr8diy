@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo Gr8 DIY 빌드 스크립트
echo ============================================

cd /d "%~dp0"

REM 환경 설정 (한글 경로 문제 우회)
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 기존 빌드 폴더 삭제
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM PyInstaller 실행 (hook 우회)
echo 빌드 시작...
.\env\Scripts\python.exe -m PyInstaller ^
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
    --distpath "dist" ^
    --workpath "build" ^
    app\main.py

if %ERRORLEVEL% EQU 0 (
    echo ============================================
    echo 빌드 성공!
    echo 결과물: dist\Gr8 DIY\
    echo ============================================
) else (
    echo ============================================
    echo 빌드 실패! 에러 코드: %ERRORLEVEL%
    echo ============================================
)

pause


