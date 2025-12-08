@echo off
chcp 65001 > nul
color 0E
cls
echo ========================================
echo 긴급 패키지 재설치 스크립트
echo ========================================
echo.
echo 문제: PyQt-Fluent-Widgets는 PyQt6용입니다!
echo 해결: PySide6-Fluent-Widgets로 변경합니다.
echo.
echo 이 작업은 약 2~3분 소요됩니다.
echo.
pause

cd /d "%~dp0\.."

echo.
echo [1/3] 가상환경 활성화...
call env\Scripts\activate.bat

echo.
echo [2/3] 기존 PyQt-Fluent-Widgets 제거...
pip uninstall PyQt-Fluent-Widgets -y

echo.
echo [3/3] PySide6-Fluent-Widgets 설치...
echo (PySide6와 호환되는 버전)
pip install PySide6-Fluent-Widgets>=1.5.0

if %errorlevel% equ 0 (
    color 0A
    echo.
    echo ========================================
    echo ✓ 패키지 교체 완료!
    echo ========================================
    echo.
    echo 설치된 패키지:
    pip list | findstr -i "fluent"
    echo.
    echo 이제 3_run_app.bat을 실행하세요!
    echo.
) else (
    color 0C
    echo.
    echo ========================================
    echo ✗ 설치 실패
    echo ========================================
    echo.
    echo 수동으로 설치해보세요:
    echo.
    echo   env\Scripts\activate
    echo   pip uninstall PyQt-Fluent-Widgets -y
    echo   pip install PySide6-Fluent-Widgets
    echo.
)

pause

