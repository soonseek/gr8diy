@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo Gr8 DIY 빌드 스크립트 (수동 설정)
echo ============================================

cd /d "%~dp0"

REM 환경 설정
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 기존 빌드 폴더 삭제
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM PyInstaller 실행 (Qt hook 비활성화)
echo 빌드 시작 (Qt hook 없이)...
.\env\Scripts\python.exe -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --name "Gr8 DIY" ^
    --windowed ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtSql ^
    --hidden-import=PySide6.QtNetwork ^
    --hidden-import=qfluentwidgets ^
    --hidden-import=qfluentwidgets.common ^
    --hidden-import=qfluentwidgets.components ^
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
    --collect-all=PySide6 ^
    --collect-all=qfluentwidgets ^
    --distpath "dist" ^
    --workpath "build" ^
    app\main.py

if %ERRORLEVEL% NEQ 0 (
    echo ============================================
    echo 빌드 실패! 에러 코드: %ERRORLEVEL%
    echo ============================================
    pause
    exit /b %ERRORLEVEL%
)

echo ============================================
echo 빌드 성공! PySide6 파일 복사 중...
echo ============================================

REM PySide6 DLL 및 플러그인 수동 복사
set PYSIDE6_SRC=.\env\Lib\site-packages\PySide6
set DEST=.\dist\Gr8 DIY

REM PySide6 주요 DLL 복사
echo PySide6 DLL 복사...
copy "%PYSIDE6_SRC%\*.dll" "%DEST%\" /Y >nul 2>&1
copy "%PYSIDE6_SRC%\*.pyd" "%DEST%\" /Y >nul 2>&1

REM 플러그인 복사
echo PySide6 플러그인 복사...
if not exist "%DEST%\PySide6\plugins" mkdir "%DEST%\PySide6\plugins"
xcopy /E /I /Y /Q "%PYSIDE6_SRC%\plugins\platforms" "%DEST%\PySide6\plugins\platforms"
xcopy /E /I /Y /Q "%PYSIDE6_SRC%\plugins\sqldrivers" "%DEST%\PySide6\plugins\sqldrivers"
xcopy /E /I /Y /Q "%PYSIDE6_SRC%\plugins\styles" "%DEST%\PySide6\plugins\styles"
xcopy /E /I /Y /Q "%PYSIDE6_SRC%\plugins\imageformats" "%DEST%\PySide6\plugins\imageformats"

REM qfluentwidgets 복사
echo qfluentwidgets 복사...
xcopy /E /I /Y /Q ".\env\Lib\site-packages\qfluentwidgets" "%DEST%\qfluentwidgets"

echo ============================================
echo 완료!
echo 결과물: %DEST%
echo ============================================

pause


