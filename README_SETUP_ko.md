# Gr8 DIY - 환경 세팅 가이드

## 📋 프로젝트 소개

**Gr8 DIY**는 PySide6 기반의 암호화폐 자동매매 봇 데스크탑 애플리케이션입니다.

**주요 기능:**
- ✅ OKX API 연동 (REST + WebSocket)
- ✅ GPT API 연동 (시장 분석)
- ✅ 실시간 데이터 수집 및 보조지표 계산
- ✅ 마틴게일 전략 기반 자동매매
- ✅ 다크모드 사이버펑크 스타일 UI

이 가이드는 **Gr8 DIY를 설치하고 실행하는 방법**을 안내합니다.

## 🎯 준비물

- **Windows 10 또는 Windows 11** (64bit)
- **인터넷 연결** (패키지 다운로드용)
- **관리자 권한** (Python 설치 시 필요할 수 있음)

## 🚀 설치 순서

### 🎯 빠른 설치 (권장) - 2단계만!

#### 1단계: Python 설치 (이미 있으면 건너뛰기)

1. `scripts` 폴더를 엽니다
2. **`1_install_python_and_deps.bat`** 파일을 더블클릭합니다
3. 설치 완료 후 **PC 재부팅** 권장

⏱️ **소요 시간**: 약 3~5분

---

#### 2단계: 자동 설치 (오류 수정 포함)

1. `scripts` 폴더에서 **`0_fix_installation_error.bat`** 파일을 더블클릭합니다
2. 자동으로 다음 작업이 진행됩니다:
   - ✓ 기존 설치 오류 수정
   - ✓ 가상환경 생성
   - ✓ 올바른 패키지 자동 설치
3. "모든 패키지 설치 완료!" 메시지가 나오면 성공!

⏱️ **소요 시간**: 약 5~10분

---

#### 3단계: 앱 실행

1. `scripts` 폴더에서 **`3_run_app.bat`** 파일을 더블클릭합니다
2. 잠시 후 GUI 창이 나타나면 성공!

이후에는 `3_run_app.bat` 파일만 더블클릭하면 프로그램이 실행됩니다.

---

### 📌 이미 Python이 설치되어 있다면?

**바로 이것만 더블클릭하세요:**

```
scripts\0_fix_installation_error.bat
```

그러면 모든 오류가 자동으로 수정됩니다!

---

### ⚠️ "QFluentWidgets" 오류가 발생했나요?

`scripts` 폴더의 **`0_fix_installation_error.bat`**을 더블클릭하면 자동으로 해결됩니다!

---

## 📁 프로젝트 폴더 구조

```
C:\Users\송민정\CursorProjects\free-trader\
│
├── env\                         # 가상환경 (자동 생성됨)
│
├── app\                         # 애플리케이션 소스 코드
│   ├── __init__.py
│   └── main.py                  # 메인 실행 파일
│
├── scripts\                     # 설치 및 실행 스크립트
│   ├── 1_install_python_and_deps.bat
│   ├── 2_create_venv_and_install_requirements.bat
│   └── 3_run_app.bat
│
├── requirements.txt             # Python 패키지 목록
└── README_SETUP_ko.md          # 이 파일
```

---

## ❓ 문제가 생겼을 때 (FAQ)

### Q1. "`winget` 명령을 찾을 수 없습니다" 오류가 나요

**원인**: Windows 10 구버전 또는 winget이 설치되지 않은 경우

**해결 방법**:

#### 방법 1: 수동으로 Python 설치 (권장)

1. https://www.python.org/downloads/ 접속
2. "Download Python 3.11.x" 버튼 클릭
3. 다운로드한 설치 파일 실행
4. ⚠️ **중요**: 설치 시 "Add Python to PATH" 옵션을 **반드시 체크**
5. "Install Now" 클릭
6. 설치 완료 후 PC 재부팅
7. `2_create_venv_and_install_requirements.bat` 부터 다시 진행

#### 방법 2: winget 설치

1. Microsoft Store에서 "앱 설치 관리자" 검색 후 설치
2. 설치 후 `1_install_python_and_deps.bat` 재실행

---

### Q2. "권한이 부족합니다" 또는 "설치할 수 없습니다" 오류

**원인**: 회사 PC, 학교 PC 등에서 관리자 권한이 제한된 경우

**해결 방법**:

1. `.bat` 파일을 **마우스 오른쪽 클릭** → "관리자 권한으로 실행"
2. 그래도 안 된다면:
   - IT 관리자에게 Python 설치 요청
   - 또는 Portable Python 사용 (https://www.python.org/downloads/windows/)
   - ZIP 버전 다운로드 후 압축 해제하여 사용

---

### Q3. "Could not find a version that satisfies the requirement" 오류

**원인**: Python 버전 불일치 또는 패키지 이름 오류

**해결 방법**:

#### 방법 1: Python 버전 확인

1. 명령 프롬프트(cmd)를 열고:
   ```
   python --version
   ```
2. Python 버전이 **3.8 ~ 3.13** 사이인지 확인
3. 버전이 맞지 않으면:
   - https://www.python.org/downloads/
   - Python 3.11.x (권장) 다운로드
   - 설치 시 "Add Python to PATH" 체크 필수!

#### 방법 2: 패키지 개별 설치

```cmd
cd C:\Users\송민정\CursorProjects\free-trader
env\Scripts\activate
pip install PySide6==6.7.2
pip install PyQt-Fluent-Widgets
pip install requests websockets openai python-dotenv pytz cryptography pandas numpy aiohttp
```

#### 방법 3: requirements.txt 수정됨

최신 버전은 올바른 패키지 이름으로 수정되었습니다:

- ❌ `QFluentWidgets` (잘못된 이름)
- ✅ `PyQt-Fluent-Widgets` (올바른 이름)

---

### Q4. 패키지 설치 중 네트워크 오류 (timeout, SSL 오류 등)

**원인**: 회사 방화벽, 프록시, 또는 인터넷 연결 불안정

**해결 방법**:

1. 안정적인 Wi-Fi에 연결
2. 회사 네트워크라면 IT팀에 PyPI(pypi.org) 접근 허용 요청
3. 또는 개인 핫스팟 사용
4. 프록시 설정이 필요한 경우:
   ```
   set HTTP_PROXY=http://proxy.company.com:8080
   set HTTPS_PROXY=http://proxy.company.com:8080
   ```
   위 명령을 `.bat` 파일 상단에 추가

---

### Q5. 앱 실행 시 "모듈을 찾을 수 없습니다" 오류

**원인**: 가상환경이 활성화되지 않았거나 패키지 설치가 불완전

**해결 방법**:

1. `2_create_venv_and_install_requirements.bat`을 다시 실행
2. 설치 중 오류 메시지가 없었는지 확인
3. 수동 확인 방법:
   - `scripts\3_run_app.bat`을 메모장으로 열기
   - `call env\Scripts\activate.bat` 줄이 있는지 확인
4. 가상환경에서 패키지 확인:
   ```cmd
   env\Scripts\activate
   pip list
   ```
   - PySide6, PyQt-Fluent-Widgets가 목록에 있는지 확인

---

### Q6. 한글이 깨져 보여요

**원인**: 콘솔 인코딩 문제

**해결 방법**:

- `.bat` 파일 상단에 `chcp 65001` 명령이 있는지 확인 (이미 포함되어 있음)
- 콘솔 창의 속성 → 글꼴을 "맑은 고딕" 또는 "Consolas"로 변경

---

### Q7. "Python 3.14 이상은 지원하지 않습니다" 오류

**원인**: 너무 최신 Python 버전 설치

**해결 방법**:

1. Python 3.11 또는 3.12 버전 재설치 (권장: 3.11.x)
2. 기존 Python 제거:
   - 제어판 → 프로그램 제거
   - Python 3.14 선택 후 제거
3. Python 3.11.x 설치:
   - https://www.python.org/downloads/
   - "Download Python 3.11.x" 클릭
4. 다시 `2_create_venv_and_install_requirements.bat` 실행

---

## 🔄 다음 단계 (개발 예정)

현재는 **환경 세팅 테스트 버전**입니다. 향후 다음 기능들이 추가될 예정입니다:

- [ ] **OKX API 연동**: 실시간 시세 조회, 주문 실행
- [ ] **자동매매 봇 로직**: 전략 설정, 백테스팅
- [ ] **GPT 연동**: AI 기반 시장 분석 및 전략 추천
- [ ] **실시간 차트**: 캔들스틱, 기술적 지표
- [ ] **알림 시스템**: 텔레그램, 이메일 알림
- [ ] **데이터베이스**: 거래 내역, 수익률 기록
- [ ] **고급 UI**: QFluentWidgets 기반 모던 인터페이스

---

## 📞 지원

- **개발자**: [당신의 이름/연락처]
- **버전**: 0.1.0 (환경 세팅 버전)
- **최종 업데이트**: 2025년 12월

---

## ⚠️ 주의사항

1. 이 프로그램은 **교육 및 테스트 목적**으로 제작되었습니다
2. 실제 자금을 사용한 거래 시 손실 위험이 있습니다
3. 투자 결정은 본인의 책임입니다
4. API 키는 절대 타인과 공유하지 마세요

---

**축하합니다! 🎉 환경 세팅이 완료되었습니다.**

이제 `3_run_app.bat`을 실행하여 프로그램을 테스트해보세요!
