@echo off
chcp 65001 > nul
echo ========================================
echo Python 설치 스크립트
echo ========================================
echo.

REM Python 설치 여부 확인
echo [1/3] Python 설치 여부 확인 중...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Python이 이미 설치되어 있습니다.
    python --version
    echo.
    goto :check_pip
) else (
    echo ✗ Python이 설치되어 있지 않습니다.
    echo.
    goto :install_python
)

:install_python
echo [2/3] Python 설치 시도 중...
echo winget을 사용하여 Python 3.11을 설치합니다.
echo 이 작업은 몇 분 정도 소요될 수 있습니다...
echo.

REM winget 사용 가능 여부 확인
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ winget을 찾을 수 없습니다.
    echo.
    echo [수동 설치 안내]
    echo 1. 프로젝트 폴더의 README_SETUP_ko.md 파일을 열어주세요.
    echo 2. "문제가 생겼을 때" 섹션에서 Python 수동 설치 방법을 확인하세요.
    echo 3. 또는 https://www.python.org/downloads/ 에서 Python 3.11을 다운로드하세요.
    echo 4. ⚠ 중요: Python 3.8 ~ 3.13 버전이 필요합니다 (PySide6 호환)
    echo.
    pause
    exit /b 1
)

REM Python 3.11 설치
winget install -e --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 (
    echo ✗ Python 설치 중 오류가 발생했습니다.
    echo 관리자 권한이 필요하거나, 회사 정책으로 인해 설치가 제한될 수 있습니다.
    echo README_SETUP_ko.md의 FAQ 섹션을 참고해주세요.
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Python 설치가 완료되었습니다!
echo.
echo [중요] 설치 완료 후 다음 단계:
echo 1. 이 창을 닫아주세요.
echo 2. PC를 재부팅하거나 로그아웃 후 다시 로그인해주세요.
echo 3. 재부팅 후 2_create_venv_and_install_requirements.bat을 실행해주세요.
echo.
pause
exit /b 0

:check_pip
echo [2/3] pip 업그레이드 중...
python -m pip install --upgrade pip --quiet
if %errorlevel% == 0 (
    echo ✓ pip 업그레이드 완료
) else (
    echo ⚠ pip 업그레이드 중 경고가 있었지만 계속 진행합니다.
)
echo.

echo [3/3] 완료!
echo Python과 pip이 준비되었습니다.
echo 다음 단계: 2_create_venv_and_install_requirements.bat을 실행해주세요.
echo.
pause

