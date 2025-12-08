@echo off
chcp 65001 > nul
echo ========================================
echo 가상환경 생성 및 패키지 설치 스크립트
echo ========================================
echo.

REM 프로젝트 루트로 이동
cd /d "%~dp0\.."

echo 현재 작업 디렉토리: %CD%
echo.

REM Python 설치 확인
echo [1/4] Python 설치 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python이 설치되어 있지 않습니다.
    echo 먼저 1_install_python_and_deps.bat을 실행해주세요.
    echo.
    pause
    exit /b 1
)
echo ✓ Python이 설치되어 있습니다.
python --version

REM Python 버전 확인 (3.8 ~ 3.13 필요)
echo.
echo Python 버전 확인 중...
python -c "import sys; exit(0 if (3, 8) <= sys.version_info[:2] < (3, 14) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ⚠ 경고: Python 버전이 호환되지 않을 수 있습니다.
    echo PySide6는 Python 3.8 ~ 3.13을 요구합니다.
    echo 현재 버전:
    python --version
    echo.
    echo 계속하시겠습니까? [Y/N]
    choice /C YN /N
    if errorlevel 2 (
        echo 설치를 취소합니다.
        pause
        exit /b 1
    )
)
echo ✓ Python 버전 호환 확인 완료
echo.

REM 가상환경 생성
echo [2/4] 가상환경 생성 중...
if exist "env\Scripts\activate.bat" (
    echo ✓ 가상환경이 이미 존재합니다. (env 폴더)
) else (
    echo 가상환경을 생성합니다... (약 1~2분 소요)
    python -m venv env
    if %errorlevel% neq 0 (
        echo ✗ 가상환경 생성 중 오류가 발생했습니다.
        echo Python venv 모듈이 제대로 설치되지 않았을 수 있습니다.
        echo.
        pause
        exit /b 1
    )
    echo ✓ 가상환경 생성 완료
)
echo.

REM 가상환경 활성화
echo [3/4] 가상환경 활성화 중...
call env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ✗ 가상환경 활성화에 실패했습니다.
    echo.
    pause
    exit /b 1
)
echo ✓ 가상환경 활성화 완료
echo.

REM pip 업그레이드
echo pip 업그레이드 중...
python -m pip install --upgrade pip --quiet
echo ✓ pip 업그레이드 완료
echo.

REM requirements.txt 확인
if not exist "requirements.txt" (
    echo ✗ requirements.txt 파일을 찾을 수 없습니다.
    echo 프로젝트 루트 디렉토리에 requirements.txt가 있는지 확인해주세요.
    echo.
    pause
    exit /b 1
)

REM 패키지 설치
echo [4/4] 필요한 패키지 설치 중...
echo 이 작업은 네트워크 속도에 따라 5~10분 정도 소요될 수 있습니다.
echo 설치 중... (진행 상황이 화면에 표시됩니다)
echo.
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ✗ 패키지 설치 중 오류가 발생했습니다.
    echo.
    echo [가능한 원인]
    echo - 네트워크 연결 문제
    echo - 회사 방화벽/프록시 제한
    echo - 디스크 공간 부족
    echo.
    echo README_SETUP_ko.md의 FAQ 섹션을 참고해주세요.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 모든 설치가 완료되었습니다!
echo ========================================
echo.
echo 다음 단계: 3_run_app.bat을 실행하여 앱을 테스트해보세요.
echo.
pause

