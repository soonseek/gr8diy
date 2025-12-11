# 문제 해결 가이드 (Troubleshooting)

## 🚨 설치 중 발생한 오류?

### 증상 1: "Could not find a version that satisfies the requirement QFluentWidgets"

```
ERROR: Could not find a version that satisfies the requirement QFluentWidgets>=1.5.0
ERROR: No matching distribution found for QFluentWidgets>=1.5.0
```

**원인**: 
- 패키지 이름 오류 (구버전 requirements.txt)
- Python 버전 불일치

**해결 방법**:

#### 1단계: Python 버전 확인
```cmd
python --version
```

**필요한 버전**: Python 3.8 ~ 3.13 (권장: 3.11.x)

- ❌ Python 3.7 이하: 너무 오래됨
- ❌ Python 3.14 이상: 너무 최신
- ✅ Python 3.11.x: 완벽!

#### 2단계: 최신 requirements.txt 사용
프로젝트의 `requirements.txt`가 최신 버전인지 확인:

```txt
# 올바른 패키지 이름
PySide6==6.4.2
PySide6-Fluent-Widgets==1.5.1
numpy<2
```

❌ 잘못된 조합: `PySide6>=6.6.0` + `QFluentWidgets`  
✅ 올바른 조합: `PySide6==6.4.2` + `PySide6-Fluent-Widgets==1.5.1` + `numpy<2`

#### 3단계: 수동으로 재설치

```cmd
# 프로젝트 디렉토리로 이동
cd C:\Users\송민정\CursorProjects\free-trader

# 기존 가상환경 삭제 (있다면)
rmdir /s /q env

# 새 가상환경 생성
python -m venv env

# 가상환경 활성화
env\Scripts\activate

# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 개별 설치 (호환 버전)
pip install "PySide6==6.4.2"
pip install "PySide6-Fluent-Widgets==1.5.1"
pip install "numpy<2"
pip install requests websockets openai python-dotenv pytz cryptography pandas aiohttp

# 설치 확인
pip list
```

---

### 증상 2: Python 버전이 호환되지 않음

```
ERROR: Ignored the following versions that require a different python version: ...
```

**해결 방법**:

#### 옵션 A: Python 3.11 재설치 (권장)

1. **기존 Python 제거**
   - 시작 메뉴 → 설정 → 앱 → Python 검색
   - 설치된 모든 Python 버전 제거

2. **Python 3.11 설치**
   - https://www.python.org/downloads/
   - "Download Python 3.11.x" 클릭
   - 설치 시 **"Add Python to PATH" 체크 필수!**

3. **설치 확인**
   ```cmd
   python --version
   # 출력: Python 3.11.x
   ```

4. **처음부터 다시**
   - `1_install_python_and_deps.bat` 건너뛰기
   - `2_create_venv_and_install_requirements.bat` 실행

#### 옵션 B: 호환 가능한 버전으로 설치

현재 Python 버전이 3.8 ~ 3.13이지만 오류가 난다면:

```cmd
# 특정 버전 지정 설치
pip install PySide6==6.7.2 --force-reinstall
pip install PyQt-Fluent-Widgets==1.5.0 --force-reinstall
```

---

### 증상 3: 네트워크 오류 (연결 시간 초과, SSL 오류)

```
WARNING: Retrying ... after connection broken
ERROR: Could not find a version that satisfies the requirement ...
```

**원인**:
- 방화벽/프록시 차단
- 불안정한 네트워크
- PyPI 서버 일시적 문제

**해결 방법**:

#### 방법 1: 다른 PyPI 미러 사용

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

또는

```cmd
pip install -r requirements.txt -i https://pypi.org/simple --trusted-host pypi.org
```

#### 방법 2: 타임아웃 시간 늘리기

```cmd
pip install -r requirements.txt --default-timeout=100
```

#### 방법 3: 프록시 설정 (회사망)

```cmd
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080
pip install -r requirements.txt
```

---

### 증상 4: 가상환경 생성 실패

```
Error: Command '...\python.exe' ... returned non-zero exit status 1
```

**해결 방법**:

```cmd
# Python venv 모듈 재설치 (관리자 권한 cmd)
python -m pip install --upgrade pip setuptools

# 수동으로 가상환경 생성
cd C:\Users\송민정\CursorProjects\free-trader
python -m venv env --clear
```

---

## 🏃 실행 중 발생한 오류?

### 증상 5: "No module named 'PySide6'"

**원인**: 가상환경이 활성화되지 않았거나 패키지 미설치

**해결 방법**:

```cmd
# 가상환경 활성화 확인
cd C:\Users\송민정\CursorProjects\free-trader
env\Scripts\activate

# 프롬프트가 (env)로 시작하는지 확인
(env) C:\Users\...>

# 패키지 설치 확인
pip list | findstr PySide6

# 없으면 재설치
pip install PySide6==6.7.2
```

---

### 증상 6: "ImportError: DLL load failed"

**원인**: Visual C++ 재배포 패키지 누락

**해결 방법**:

1. **Visual C++ Redistributable 설치**
   - https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 다운로드 후 실행
   - PC 재부팅

2. **재시도**
   ```cmd
   scripts\3_run_app.bat
   ```

---

### 증상 7: 앱이 바로 종료됨 (검은 창만 깜빡)

**원인**: Python 경로 문제 또는 코드 오류

**해결 방법**:

```cmd
# 직접 실행해서 에러 메시지 확인
cd C:\Users\송민정\CursorProjects\free-trader
env\Scripts\activate
python app/main.py

# 에러 메시지를 읽고 해당 문제 해결
```

---

## 🔧 기타 문제

### 한글이 깨져 보임

```cmd
# cmd 인코딩 변경
chcp 65001
scripts\3_run_app.bat
```

### DB 초기화 실패

```cmd
# data 폴더 삭제 후 재시작
rmdir /s /q data
scripts\3_run_app.bat
```

### 완전히 처음부터 다시 시작

```cmd
cd C:\Users\송민정\CursorProjects\free-trader

# 가상환경 삭제
rmdir /s /q env

# 데이터 삭제
rmdir /s /q data

# 다시 시작
scripts\2_create_venv_and_install_requirements.bat
```

---

## 📞 그래도 안 된다면?

1. **로그 확인**
   - 앱 실행 후 `data` 폴더의 로그 파일 확인
   - 에러 메시지 전체 복사

2. **이슈 등록**
   - GitHub Issues에 다음 정보와 함께 등록:
     - Windows 버전
     - Python 버전 (`python --version`)
     - 에러 메시지 전체
     - 실행한 단계

3. **임시 해결책**
   - Python 3.11.7 버전 명시적 설치
   - 패키지를 하나씩 설치
   - 관리자 권한으로 cmd 실행

---

**이 가이드로 대부분의 문제가 해결됩니다! 🎉**

