# OKX Trading Bot

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

- **UI**: PySide6, QFluentWidgets
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

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

**Made with ❤️ using PySide6 + QFluentWidgets**


