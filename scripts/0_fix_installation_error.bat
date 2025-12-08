@echo off
chcp 65001 > nul
color 0A
echo ========================================
echo 설치 오류 자동 수정 스크립트
echo ========================================
echo.
echo 이 스크립트는 다음 작업을 자동으로 수행합니다:
echo 1. Python 버전 확인 및 자동 설치
echo 2. 기존 가상환경 삭제
echo 3. 새 가상환경 생성
echo 4. 수정된 패키지 목록으로 재설치
echo.
echo 약 5~15분 정도 소요됩니다...
echo.
pause

REM 프로젝트 루트로 이동
cd /d "%~dp0\.."

echo.
echo ========================================
echo [1/6] Python 버전 확인 중...
echo ========================================

REM Python 설치 여부 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python이 설치되어 있지 않습니다.
    echo Python 3.11을 자동으로 설치합니다...
    goto auto_install_python
)

echo ✓ Python 발견:
python --version
echo.

REM Python으로 버전 체크 (더 안전한 방법)
python -c "import sys; exit(0 if (3,8) <= sys.version_info[:2] < (3,14) else 1)" 2>nul
if %errorlevel% equ 0 (
    echo ✓ Python 버전 호환 확인 완료
    goto continue_install
)

REM 버전 호환되지 않음
color 0E
echo.
echo ========================================
echo ⚠ Python 버전 문제 발견!
echo ========================================
echo.
python --version
echo.
echo 이 프로그램은 Python 3.8 ~ 3.13이 필요합니다.
echo (PySide6가 Python 3.14를 아직 지원하지 않습니다)
echo.
echo ========================================
echo 자동으로 Python 3.11을 설치하시겠습니까?
echo ========================================
echo.
echo 선택지:
echo.
echo [1] 자동 설치 (권장)
echo     → Python 3.11이 자동으로 설치됩니다
echo     → 기존 Python은 그대로 유지됩니다
echo     → 약 5~10분 소요
echo.
echo [2] 수동 설치 안내
echo     → 단계별 설명을 보여드립니다
echo     → 직접 설치 파일을 다운로드합니다
echo.
echo [3] 그냥 계속 진행
echo     → 설치를 시도하지만 실패할 수 있습니다
echo.
set /p USER_CHOICE="선택 (1, 2, 또는 3): "

if "%USER_CHOICE%"=="1" goto auto_install_python
if "%USER_CHOICE%"=="2" goto manual_install_guide
if "%USER_CHOICE%"=="3" goto continue_anyway

echo 잘못된 입력입니다. 다시 시도해주세요.
pause
exit /b 1

:auto_install_python
cls
color 0B
echo ========================================
echo Python 3.11 자동 설치 중...
echo ========================================
echo.
echo 방법 1: winget 사용 시도...
echo.

REM winget으로 Python 3.11 설치 시도
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ winget 발견! Python 3.11 설치 중...
    echo 이 작업은 5~10분 정도 걸릴 수 있습니다...
    echo 진행 중... 기다려주세요...
    echo.
    
    winget install -e --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    
    if %errorlevel% equ 0 (
        color 0A
        echo.
        echo ========================================
        echo ✓ Python 3.11 설치 완료!
        echo ========================================
        echo.
        echo 중요: 설치를 완료하려면 PC를 재부팅해야 합니다.
        echo.
        echo 지금 PC를 재부팅하시겠습니까?
        echo.
        set /p REBOOT_CHOICE="[Y] 예 / [N] 아니오: "
        
        if /i "%REBOOT_CHOICE%"=="Y" (
            echo.
            echo 5초 후 PC가 재부팅됩니다...
            echo 재부팅 후 이 스크립트를 다시 실행해주세요!
            timeout /t 5
            shutdown /r /t 0
            exit /b 0
        ) else (
            echo.
            echo 나중에 PC를 재부팅한 후 이 스크립트를 다시 실행해주세요.
            pause
            exit /b 0
        )
    ) else (
        echo ✗ winget 설치 실패
        echo.
    )
)

echo winget을 사용할 수 없습니다.
echo 방법 2: 직접 다운로드 방식 사용...
echo.

REM PowerShell로 Python 3.11 설치 파일 다운로드
echo Python 3.11 설치 파일을 다운로드합니다...
echo 다운로드 위치: %TEMP%\python-3.11-installer.exe
echo 약 30MB, 1~3분 소요...
echo.

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.10/python-3.11.10-amd64.exe' -OutFile '%TEMP%\python-3.11-installer.exe'}" 2>nul

if exist "%TEMP%\python-3.11-installer.exe" (
    echo ✓ 다운로드 완료!
    echo.
    echo Python 3.11 설치를 시작합니다...
    echo 설치 창이 나타나면 잠시 기다려주세요...
    echo.
    
    REM 자동 설치 (PATH 추가 옵션 포함)
    start /wait "" "%TEMP%\python-3.11-installer.exe" /passive InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo.
    echo 설치가 완료되었습니다!
    echo.
    
    REM 설치 파일 삭제
    del "%TEMP%\python-3.11-installer.exe" 2>nul
    
    color 0A
    echo ========================================
    echo ✓ Python 3.11 설치 완료!
    echo ========================================
    echo.
    echo PC를 재부팅해야 합니다.
    echo.
    set /p REBOOT_CHOICE="지금 재부팅하시겠습니까? [Y/N]: "
    
    if /i "%REBOOT_CHOICE%"=="Y" (
        echo.
        echo 5초 후 재부팅됩니다...
        timeout /t 5
        shutdown /r /t 0
        exit /b 0
    ) else (
        echo.
        echo 나중에 PC를 재부팅한 후 이 스크립트를 다시 실행해주세요.
        pause
        exit /b 0
    )
) else (
    echo ✗ 다운로드 실패
    echo.
    goto manual_install_guide
)

:manual_install_guide
cls
color 0E
echo ========================================
echo 수동 설치 안내
echo ========================================
echo.
echo Python 3.11을 직접 설치하는 방법:
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 1단계: 다운로드
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   10초 후 브라우저가 자동으로 열립니다...
echo   페이지에서 "Download Python 3.11.10" 버튼 클릭
echo.

timeout /t 10
start https://www.python.org/downloads/release/python-31110/

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 2단계: 설치
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   1. 다운로드한 파일 실행
echo.
echo   2. ⚠ 매우 중요! ⚠
echo      설치 첫 화면에서 반드시 체크:
echo.
echo      ☑ Add Python 3.11 to PATH
echo.
echo   3. "Install Now" 클릭
echo.
echo   4. 설치 완료까지 기다리기 (3~5분)
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 3단계: 확인
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   1. PC 재부팅
echo   2. 이 스크립트를 다시 실행
echo.
pause
exit /b 0

:continue_anyway
echo.
echo ⚠ 호환되지 않는 Python 버전으로 계속 진행합니다...
echo 패키지 설치가 실패할 수 있습니다.
echo.
pause

:continue_install
echo.
echo ========================================
echo [2/6] 기존 가상환경 삭제 중...
echo ========================================
if exist "env\" (
    echo 기존 env 폴더를 삭제합니다...
    rmdir /s /q env
    echo ✓ 삭제 완료
) else (
    echo ✓ 삭제할 가상환경이 없습니다
)
echo.

echo ========================================
echo [3/6] 새 가상환경 생성 중...
echo ========================================
echo 가상환경을 생성합니다... (약 1~2분)
python -m venv env
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ✗ 가상환경 생성 실패!
    echo.
    pause
    exit /b 1
)
echo ✓ 가상환경 생성 완료
echo.

echo ========================================
echo [4/6] pip 업그레이드 중...
echo ========================================
call env\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
echo ✓ pip 업그레이드 완료
echo.

echo ========================================
echo [5/6] 패키지 설치 중...
echo ========================================
echo 수정된 패키지 목록으로 설치합니다...
echo 이 작업은 5~10분 정도 소요됩니다.
echo.
echo 진행 상황:
echo.

echo [1/9] PySide6 설치 중...
pip install "PySide6>=6.6.0,<6.8.0" --quiet
if %errorlevel% neq 0 (
    echo ✗ PySide6 설치 실패
    goto installation_error
)
echo ✓ PySide6 설치 완료

echo [2/9] PyQt-Fluent-Widgets 설치 중...
pip install "PyQt-Fluent-Widgets>=1.5.0" --quiet
if %errorlevel% neq 0 (
    echo ✗ PyQt-Fluent-Widgets 설치 실패
    goto installation_error
)
echo ✓ PyQt-Fluent-Widgets 설치 완료

echo [3/9] requests 설치 중...
pip install "requests>=2.31.0" --quiet
echo ✓ requests 설치 완료

echo [4/9] websockets 설치 중...
pip install "websockets>=12.0" --quiet
echo ✓ websockets 설치 완료

echo [5/9] openai 설치 중...
pip install "openai>=1.0.0" --quiet
echo ✓ openai 설치 완료

echo [6/9] python-dotenv, pytz 설치 중...
pip install "python-dotenv>=1.0.0" "pytz>=2023.3" --quiet
echo ✓ python-dotenv, pytz 설치 완료

echo [7/9] cryptography 설치 중...
pip install "cryptography>=41.0.0" --quiet
echo ✓ cryptography 설치 완료

echo [8/9] pandas, numpy 설치 중...
pip install "pandas>=2.0.0" "numpy>=1.24.0" --quiet
echo ✓ pandas, numpy 설치 완료

echo [9/9] aiohttp 설치 중...
pip install "aiohttp>=3.9.0" --quiet
echo ✓ aiohttp 설치 완료

echo.
color 0A
echo ========================================
echo ✓ 모든 패키지 설치 완료!
echo ========================================
echo.
echo [6/6] 설치 확인 중...
echo.
echo 설치된 패키지 목록:
pip list | findstr /I "PySide6 PyQt requests websockets openai python-dotenv pytz cryptography pandas numpy aiohttp"
echo.
echo ========================================
echo 🎉 설치 오류가 수정되었습니다!
echo ========================================
echo.
echo 다음 단계:
echo 1. 이 창을 닫습니다
echo 2. scripts\3_run_app.bat을 더블클릭하여 앱을 실행합니다
echo.
pause
exit /b 0

:installation_error
color 0C
echo.
echo ========================================
echo ✗ 패키지 설치 중 오류 발생
echo ========================================
echo.
echo 가능한 원인:
echo 1. Python 버전 불일치
echo 2. 네트워크 연결 문제
echo 3. 방화벽/프록시 차단
echo.
echo 해결 방법:
echo 1. Python 3.11을 설치하세요
echo 2. 인터넷 연결을 확인하세요
echo 3. TROUBLESHOOTING.md 파일을 참고하세요
echo.
pause
exit /b 1
