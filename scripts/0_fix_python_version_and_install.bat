@echo off
chcp 65001 > nul
color 0E
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║     Python 버전 자동 수정 및 완전 자동 설치              ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 이 스크립트는 다음을 자동으로 수행합니다:
echo.
echo  1. 현재 Python 버전 확인
echo  2. Python 3.14 등 호환되지 않는 버전 자동 제거
echo  3. Python 3.11 자동 설치 (winget 사용)
echo  4. 가상환경 생성 및 패키지 설치
echo.
echo ⏱️  전체 소요 시간: 약 10~15분
echo.
echo ⚠️  관리자 권한이 필요할 수 있습니다.
echo     (권한 요청 창이 뜨면 "예"를 클릭하세요)
echo.
pause

REM 프로젝트 루트로 이동
cd /d "%~dp0\.."

color 0A
echo.
echo ════════════════════════════════════════════════════════════
echo [1/6] Python 버전 확인 중...
echo ════════════════════════════════════════════════════════════
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python이 설치되어 있지 않습니다.
    goto install_python_311
)

echo 현재 설치된 Python:
python --version
echo.

REM Python 버전 체크 (3.8 ~ 3.13)
python -c "import sys; v=sys.version_info; exit(0 if (3,8)<=v[:2]<(3,14) else 1)" 2>nul
if %errorlevel% == 0 (
    color 0A
    echo ✓ Python 버전이 호환됩니다!
    echo.
    goto skip_python_install
)

REM 호환되지 않는 버전
color 0E
echo.
echo ⚠️  호환되지 않는 Python 버전입니다!
echo.
echo 필요: Python 3.8 ~ 3.13
echo 현재: 
python --version
echo.
echo 자동으로 Python 3.11을 설치하겠습니다.
echo.

:remove_incompatible_python
echo ════════════════════════════════════════════════════════════
echo [2/6] 기존 Python 제거 중...
echo ════════════════════════════════════════════════════════════
echo.

REM winget으로 Python 제거 시도
echo winget을 사용하여 기존 Python을 제거합니다...
echo (이 작업은 몇 분 소요될 수 있습니다)
echo.

winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  winget을 찾을 수 없습니다.
    goto manual_uninstall_guide
)

REM Python 3.14 제거
echo Python 3.14를 제거하는 중...
winget uninstall --id Python.Python.3.14 --silent >nul 2>&1
timeout /t 2 >nul

REM Python 3.13 제거 (혹시 있을 경우)
winget uninstall --id Python.Python.3.13 --silent >nul 2>&1
timeout /t 2 >nul

echo ✓ 기존 Python 제거 완료
echo.
goto install_python_311

:manual_uninstall_guide
color 0C
echo.
echo ════════════════════════════════════════════════════════════
echo 수동 제거 필요
echo ════════════════════════════════════════════════════════════
echo.
echo winget을 사용할 수 없으므로 수동으로 제거해야 합니다.
echo.
echo 📌 다음 단계를 따라하세요:
echo.
echo 1️⃣  Windows 키를 누릅니다
echo.
echo 2️⃣  "프로그램 추가/제거" 또는 "앱" 검색 후 실행
echo.
echo 3️⃣  검색창에 "Python" 입력
echo.
echo 4️⃣  "Python 3.14" 또는 "Python 3.13" 찾기
echo.
echo 5️⃣  클릭 후 "제거" 버튼 클릭
echo.
echo 6️⃣  제거 완료 후 이 창으로 돌아와서 아무 키나 누르세요
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause

:install_python_311
color 0B
echo.
echo ════════════════════════════════════════════════════════════
echo [3/6] Python 3.11 자동 설치 중...
echo ════════════════════════════════════════════════════════════
echo.

REM winget 확인
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    goto manual_install_guide
)

echo winget을 사용하여 Python 3.11을 설치합니다...
echo (이 작업은 5~10분 소요될 수 있습니다)
echo.
echo ⏳ 잠시만 기다려주세요...
echo.

winget install -e --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  자동 설치 실패
    goto manual_install_guide
)

echo.
echo ✓ Python 3.11 설치 완료!
echo.
echo 🔄 PATH 환경 변수를 새로고침하는 중...
echo.

REM PATH 새로고침
call refreshenv >nul 2>&1

echo ✓ 환경 변수 새로고침 완료
echo.
echo ⚠️  중요: 이 창을 닫은 후 PC를 재부팅해주세요.
echo          재부팅 후 이 스크립트를 다시 실행하세요.
echo.
pause
exit /b 0

:manual_install_guide
color 0E
echo.
echo ════════════════════════════════════════════════════════════
echo Python 3.11 수동 설치 가이드
echo ════════════════════════════════════════════════════════════
echo.
echo winget을 사용할 수 없으므로 수동 설치가 필요합니다.
echo.
echo 지금 자동으로 다운로드 페이지를 열어드리겠습니다.
echo 3초 후 브라우저가 열립니다...
echo.
timeout /t 3 >nul

start https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

color 0A
echo.
echo ════════════════════════════════════════════════════════════
echo 📌 설치 방법 (중요!)
echo ════════════════════════════════════════════════════════════
echo.
echo 브라우저가 열리고 Python 3.11.9가 다운로드됩니다.
echo.
echo 1️⃣  다운로드된 파일을 더블클릭하여 실행
echo.
echo 2️⃣  ⚠️  중요: 하단에 있는 체크박스를 반드시 체크!
echo     ☑ Add Python 3.11 to PATH  ← 이것을 체크!
echo.
echo 3️⃣  "Install Now" 클릭
echo.
echo 4️⃣  설치 완료 후 "Close" 클릭
echo.
echo 5️⃣  PC 재부팅
echo.
echo 6️⃣  재부팅 후 이 스크립트를 다시 실행
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 설치 완료 후 재부팅하고 다시 이 파일을 더블클릭하세요!
echo.
pause
exit /b 0

:skip_python_install
color 0A
echo Python 설치를 건너뜁니다.
echo.

echo ════════════════════════════════════════════════════════════
echo [4/6] 기존 가상환경 정리 중...
echo ════════════════════════════════════════════════════════════
echo.
if exist "env\" (
    echo 기존 env 폴더를 삭제합니다...
    rmdir /s /q env
    echo ✓ 삭제 완료
) else (
    echo ✓ 삭제할 가상환경이 없습니다
)
echo.

echo ════════════════════════════════════════════════════════════
echo [5/6] 새 가상환경 생성 및 패키지 설치 중...
echo ════════════════════════════════════════════════════════════
echo.
echo 가상환경 생성 중...
python -m venv env
if %errorlevel% neq 0 (
    color 0C
    echo ✗ 가상환경 생성 실패!
    pause
    exit /b 1
)
echo ✓ 가상환경 생성 완료
echo.

echo 가상환경 활성화 중...
call env\Scripts\activate.bat
echo.

echo pip 업그레이드 중...
python -m pip install --upgrade pip --quiet
echo ✓ pip 업그레이드 완료
echo.

echo ════════════════════════════════════════════════════════════
echo [6/6] 패키지 설치 중... (5~10분 소요)
echo ════════════════════════════════════════════════════════════
echo.

echo [1/9] PySide6 설치 중...
pip install "PySide6>=6.6.0,<6.8.0" --quiet
if %errorlevel% neq 0 goto install_error
echo ✓ PySide6 설치 완료

echo [2/9] PyQt-Fluent-Widgets 설치 중...
pip install "PyQt-Fluent-Widgets>=1.5.0" --quiet
if %errorlevel% neq 0 goto install_error
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
echo ════════════════════════════════════════════════════════════
echo ✓ 모든 설치가 완료되었습니다!
echo ════════════════════════════════════════════════════════════
echo.
echo 설치된 패키지:
pip list | findstr /I "PySide6 PyQt requests websockets openai python-dotenv pytz cryptography pandas numpy aiohttp"
echo.
echo ════════════════════════════════════════════════════════════
echo 🎉 성공!
echo ════════════════════════════════════════════════════════════
echo.
echo Python 버전:
python --version
echo.
echo 다음 단계:
echo  → scripts\3_run_app.bat을 더블클릭하면 앱이 실행됩니다!
echo.
pause
exit /b 0

:install_error
color 0C
echo.
echo ✗ 패키지 설치 중 오류 발생
echo.
echo 가능한 원인:
echo  - 네트워크 연결 문제
echo  - 방화벽 차단
echo.
echo TROUBLESHOOTING.md 파일을 참고하세요.
echo.
pause
exit /b 1

