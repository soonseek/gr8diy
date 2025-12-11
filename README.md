# Gr8 DIY

PySide6 + QFluentWidgets 기반의 OKX 암호화폐 자동매매 데스크탑 애플리케이션

## 프로젝트 구조

```
free-trader/
│
├── app/                        # 애플리케이션 진입점
│   ├── __init__.py
│   └── main.py                 # 메인 실행 파일
│
├── api/                        # 외부 API 클라이언트
│   ├── __init__.py
│   ├── okx_client.py          # OKX REST API
│   ├── okx_websocket.py       # OKX WebSocket
│   └── gpt_client.py          # GPT API
│
├── config/                     # 설정
│   ├── __init__.py
│   └── settings.py            # 전역 설정
│
├── database/                   # 데이터베이스
│   ├── __init__.py
│   ├── schema.py              # 테이블 스키마
│   └── repository.py          # CRUD 레포지토리
│
├── indicators/                 # 보조지표 계산
│   ├── __init__.py
│   └── calculator.py          # 기술적 지표
│
├── ui/                         # UI 컴포넌트
│   ├── __init__.py
│   ├── main_window.py         # 메인 윈도우
│   ├── log_widget.py          # 시스템 로그
│   ├── settings_page.py       # 설정 페이지
│   ├── data_page.py           # 데이터 페이지
│   ├── bot_page.py            # 봇 페이지
│   ├── bot_conditions.py      # 봇 조건설정
│   ├── bot_monitoring.py      # 봇 모니터링
│   └── bot_history.py         # 거래 내역
│
├── utils/                      # 유틸리티
│   ├── __init__.py
│   ├── logger.py              # 로깅
│   ├── crypto.py              # 암호화 (자격증명)
│   └── time_helper.py         # 시간/타임존
│
├── workers/                    # 백그라운드 워커
│   ├── __init__.py
│   ├── data_collector.py      # 데이터 수집
│   └── maintenance.py         # 유지보수
│
├── data/                       # 데이터 디렉토리 (자동 생성)
│   ├── trading_bot.db         # SQLite 데이터베이스
│   └── credentials.enc        # 암호화된 자격증명
│
├── scripts/                    # 설치/실행 스크립트
│   ├── 1_install_python_and_deps.bat
│   ├── 2_create_venv_and_install_requirements.bat
│   └── 3_run_app.bat
│
├── .gitignore
├── requirements.txt
├── README.md
└── README_SETUP_ko.md         # 설치 가이드 (한글)
```

## 주요 기능

### 1. 설정 메뉴
- **기본 연동**: OKX API, GPT API 자격증명 관리 및 연동 테스트
- **거래소 설정**: OKX 계정 모드/포지션 모드 확인 및 자동 변경

### 2. 데이터 메뉴
- 과거 데이터 백필 (최대 200일)
- 실시간 데이터 최신화
- 활성 심볼 관리
- 보조지표 자동 계산 (MA, MACD, RSI, Stochastic, Bollinger Bands)

### 3. 봇 메뉴
- **조건설정**
  - 심볼별 롱/숏/OFF 선택
  - 레버리지 설정 (1~20배)
  - 마틴게일 전략 설정
  - 익절/손절 오프셋 설정
- **모니터링**
  - 실시간 포지션 현황
  - 주문 체결/취소 로그
  - PnL 추적
- **내역**
  - 거래 통계 (승률, 순익, 최대 드로다운 등)
  - 트레이드 리스트

### 4. 시스템 로그
- 모든 동작 실시간 로깅
- 레벨별 필터링 (INFO, WARNING, ERROR)
- 에러 전용 뷰

## 기술 스택

- **UI**: PySide6, QFluentWidgets + 커스텀 Gr8 DIY 테마
  - 다크모드 기반
  - 네온 그린-블루 그라디언트 포인트 컬러
  - 사이버펑크 스타일 웹 디자인
- **데이터베이스**: SQLite (QtSql)
- **API**: OKX REST + WebSocket, OpenAI GPT
- **보조지표**: pandas, numpy
- **암호화**: cryptography
- **비동기**: asyncio, websockets

## 설치 및 실행

자세한 설치 방법은 **[README_SETUP_ko.md](README_SETUP_ko.md)** 를 참고하세요.

### 빠른 시작 (Windows)

1. `scripts\1_install_python_and_deps.bat` 실행 (Python 설치)
2. PC 재부팅
3. `scripts\2_create_venv_and_install_requirements.bat` 실행 (패키지 설치)
4. `scripts\3_run_app.bat` 실행 (앱 시작)

## 데이터베이스 스키마

- `candles`: 캔들 데이터
- `indicators`: 보조지표
- `bot_configs`: 봇 설정
- `orders`: 주문 내역
- `positions`: 포지션
- `bot_logs`: 봇 로그
- `system_logs`: 시스템 로그
- `active_symbols`: 활성 심볼
- `app_settings`: 앱 설정
- `trades_history`: 거래 내역

## 주요 설계 원칙

1. **멀티 스레드**: UI와 워커 스레드 분리
2. **KST 기준**: 모든 시간은 한국 표준시(KST) 사용
3. **데이터 보존**: 최대 200일치 데이터 유지
4. **Rate Limit**: OKX API rate limit 준수
5. **에러 처리**: 모든 오류 로깅 및 UI 알림

## 보안

- API 키는 로컬에 암호화 저장
- `.gitignore`에 민감 정보 제외
- 자격증명 파일은 시스템별 암호화

## 라이선스

이 프로젝트는 교육 및 개인 용도로 제작되었습니다.

## 주의사항

⚠️ **투자 경고**
- 이 소프트웨어는 교육 목적으로 제공됩니다
- 실제 거래 시 금전적 손실 위험이 있습니다
- 모든 투자 결정은 본인의 책임입니다
- API 키는 절대 타인과 공유하지 마세요

## 개발 상태

✅ 완료:
- 프로젝트 구조 및 아키텍처
- 데이터베이스 스키마
- OKX API 클라이언트 (REST + WebSocket)
- GPT API 클라이언트
- UI 프레임워크 (메인 윈도우, 네비게이션, 로그 뷰)
- 설정, 데이터, 봇 페이지 기본 구조
- 데이터 수집 및 유지보수 워커

🚧 추가 개발 필요:
- 봇 실행 워커 (자동매매 로직)
- WebSocket 실시간 연동
- 고급 차트 뷰
- 백테스팅 기능
- 알림 시스템

---

# 🛠️ DIY 개발 가이드

Gr8 DIY를 직접 커스터마이징하고 개발하고 싶으신가요? 이 섹션에서 시작하세요!

## 📖 프로그램 작동 방식

### 화면별 기능 설명

#### 🏠 홈
- 프로그램 소개 및 가이드 표시
- README 문서를 Markdown 형식으로 렌더링

#### ⚙️ 설정
- **기본 연동 탭**: OKX API 및 GPT API 키 입력/저장/테스트
- **거래소 설정 탭**: OKX 계정 정보 조회, 계정 모드 변경

#### 📊 데이터
- **설정 탭**: 데이터 수집 파라미터 설정, 백필 실행
- **데이터 조회 탭**: 수집된 캔들 데이터 및 보조지표 확인

#### 🤖 봇
- **조건설정 탭**: 심볼별 매매 방향, 레버리지, 마틴게일 설정
- **모니터링 탭**: 실시간 포지션 및 주문 상태 모니터링
- **내역 탭**: 거래 이력 및 통계 확인

#### 📝 시스템 로그 (하단)
- 모든 이벤트 실시간 로깅
- 레벨별 필터링 (전체 로그 / 에러만)

---

## 🚀 DIY 개발 시작하기

### 1️⃣ Cursor AI 설치 및 설정

#### Cursor 설치
1. [cursor.sh](https://cursor.sh) 방문
2. Windows용 다운로드 및 설치
3. Cursor 실행 후 프로젝트 폴더 열기

#### 초기 프롬프팅 가이드

Cursor와 대화를 시작할 때 **프로젝트 컨텍스트**를 먼저 알려주세요:

```
안녕! 이 프로젝트는 Gr8 DIY라는 암호화폐 자동매매 봇이야.

주요 기술 스택:
- UI: PySide6 + QFluentWidgets (다크모드 + 네온 그린-블루 테마)
- DB: SQLite (PySide6.QtSql)
- API: OKX REST/WebSocket, OpenAI GPT
- 데이터 처리: pandas, numpy
- 언어: Python 3.11

중요 규칙:
1. PySide6는 6.4.2 버전 사용 (qfluentwidgets 1.5.1 호환)
2. numpy는 2.0 미만 버전 사용
3. 모든 시간은 KST 기준
4. UI 테마는 ui/theme.py의 Gr8Theme 클래스 사용
5. 로깅은 utils/logger.py의 전역 logger 사용

프로젝트 구조:
- app/: 메인 진입점
- ui/: 모든 UI 컴포넌트 (페이지, 위젯, 테마)
- api/: OKX, GPT API 클라이언트
- database/: 스키마 및 레포지토리
- workers/: 백그라운드 스레드 작업
- config/: 전역 설정

현재 작업: [여기에 작업 내용 입력]
```

### 2️⃣ 개발 환경 구축

#### Python 가상환경 활성화

**PowerShell:**
```powershell
# 실행 정책 완화 (현재 세션만)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 가상환경 활성화
.\env\Scripts\Activate.ps1

# 또는 직접 Python 실행
.\env\Scripts\python.exe --version
```

**CMD:**
```cmd
env\Scripts\activate.bat
```

#### 의존성 설치/업데이트

```powershell
# markdown 패키지 설치 (홈 화면용)
.\env\Scripts\python.exe -m pip install markdown

# 또는 전체 재설치
.\env\Scripts\python.exe -m pip install -r requirements.txt
```

### 3️⃣ 개발 중 앱 실행 방법

#### 방법 1: 배치 파일 사용 (권장)
```powershell
.\scripts\3_run_app.bat
```

#### 방법 2: 직접 Python 실행
```powershell
# 가상환경 Python으로 직접 실행
.\env\Scripts\python.exe .\app\main.py

# 또는 가상환경 활성화 후
python app\main.py
```

#### 방법 3: Cursor에서 실행
1. Cursor 터미널 열기 (Ctrl + `)
2. 위 명령어 입력

### 4️⃣ 실행파일로 컴파일하기

#### PyInstaller 설치
```powershell
.\env\Scripts\python.exe -m pip install pyinstaller
```

#### 컴파일 실행
```powershell
# build_exe.spec 파일 사용
.\env\Scripts\python.exe -m PyInstaller build_exe.spec

# 또는 간단 명령
.\env\Scripts\pyinstaller.exe build_exe.spec
```

#### 실행파일 위치
```
dist\Gr8 DIY\
├── Gr8 DIY.exe          <- 실행 파일
├── PySide6\
├── (기타 DLL 및 의존성...)
└── ...
```

#### 컴파일 옵션 (build_exe.spec)
- `name='Gr8 DIY'`: 실행 파일 이름
- `console=False`: GUI 모드 (콘솔 숨김)
- `icon=None`: 아이콘 경로 (원하는 .ico 파일 지정 가능)

#### 아이콘 추가하기
1. `.ico` 파일 준비 (256x256 권장)
2. `build_exe.spec` 수정:
   ```python
   icon='path/to/icon.ico'
   ```
3. 재컴파일

---

## 🎨 UI 커스터마이징

### 테마 색상 변경

`ui/theme.py`의 `Gr8Theme` 클래스 수정:

```python
class Gr8Theme:
    # 네온 포인트 컬러 변경 예시
    NEON_GREEN = "#00ff9f"   # 원하는 색상으로 변경
    NEON_BLUE = "#00d4ff"    # 원하는 색상으로 변경
    
    # 배경색 변경
    BG_DARK = "#0a0e27"      # 메인 배경
```

### 새로운 페이지 추가

1. `ui/` 폴더에 새 파일 생성 (예: `my_page.py`)
2. `QWidget` 상속 클래스 작성
3. `ui/main_window.py`에서 import 및 추가:
   ```python
   from ui.my_page import MyPage
   
   # _init_pages()에 추가
   self.my_page = MyPage()
   self.stack_widget.addWidget(self.my_page)
   
   # _init_navigation()에 추가
   self.navigation.addItem(
       routeKey="my_page",
       icon=FluentIcon.DOCUMENT,
       text="내 페이지",
       onClick=lambda: self.switch_page(N),  # N은 순서
       position=NavigationItemPosition.TOP
   )
   ```

---

## 🐛 디버깅 팁

### 로그 확인
- 앱 실행 중: 하단 시스템 로그 위젯
- 터미널 출력: `[DEBUG]`, `[DEBUG-MW]` 등 디버그 메시지
- 에러 발생 시: 전체 스택 트레이스 출력

### 데이터베이스 직접 조회
```powershell
# SQLite DB 열기
.\env\Scripts\python.exe
>>> import sqlite3
>>> conn = sqlite3.connect('data/trading_bot.db')
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT * FROM candles LIMIT 5")
>>> cursor.fetchall()
```

### 패키지 버전 충돌 해결
```powershell
# 현재 설치된 버전 확인
.\env\Scripts\pip.exe list

# 특정 버전으로 재설치
.\env\Scripts\pip.exe install "PySide6==6.4.2" --force-reinstall
```

---

## 📚 추가 리소스

- [PySide6 공식 문서](https://doc.qt.io/qtforpython-6/)
- [QFluentWidgets 문서](https://qfluentwidgets.com/)
- [OKX API 문서](https://www.okx.com/docs-v5/en/)
- [OpenAI API 문서](https://platform.openai.com/docs)

---

## 💬 커뮤니티 & 기여

### Discord 커뮤니티

버그 리포트, 기능 제안, 질문, 개발 논의 등 모든 소통은 Discord에서!

**👉 [Gr8 DIY Discord 참여하기](https://discord.gg/KBvavs9F47)**

DIY 실행이든 컴파일된 실행파일 사용이든, 모든 피드백을 환영합니다!

### GitHub 레포지토리

소스 코드, 이슈 트래킹, Pull Request는 GitHub에서!

**👉 [Gr8 DIY GitHub 레포지토리](https://github.com/soonseek/gr8diy)**

```bash
# 레포지토리 클론
git clone https://github.com/soonseek/gr8diy.git
```

### 기여 방법
- 🐛 **버그 발견 시**: Discord에서 공유하거나 [GitHub Issue](https://github.com/soonseek/gr8diy/issues) 등록
- 💡 **기능 제안**: Discord에서 아이디어 공유
- 🔧 **코드 기여**: [Pull Request](https://github.com/soonseek/gr8diy/pulls) 환영
- 📖 **문서 개선**: README, 가이드 문서 수정 제안

---

**Made with ❤️ by 유튜브 <소피아빠>와 구독자님들**

**Powered by PySide6 + QFluentWidgets**


