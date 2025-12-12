# Gr8 DIY

PySide6 + QFluentWidgets 기반의 **멀티 거래소** 암호화폐 자동매매 데스크탑 애플리케이션

## 주요 특징

### 🌐 멀티 거래소 지원
- **CCXT 라이브러리 기반** - CoinGecko Top 100 거래소 지원
- Binance, Bybit, OKX, Bitget, Gate.io, KuCoin, HTX, Kraken 등
- 거래소별 독립적인 API 키 관리
- 메인넷/테스트넷 모드 지원

### 📊 데이터 수집
- 과거 데이터 백필 (최대 200일)
- 실시간 데이터 최신화 (10초 폴링)
- 거래소별 독립적인 데이터 저장
- 6개 타임프레임 지원 (1m, 5m, 15m, 1h, 4h, 1d)

### 🤖 자동매매 봇
- **마틴게일 DCA 전략**
- 심볼별 롱/숏 방향 설정
- 레버리지 조절 (1~100배)
- 익절/손절 자동 설정
- 포지션 실시간 모니터링
- 자동 재실행 모드

### 📈 백테스팅 (개발 중)
- 과거 데이터 기반 전략 시뮬레이션
- 다양한 성과 지표 (수익률, CAGR, MDD, 샤프 비율 등)
- 결과 CSV/JSON 내보내기

## 프로젝트 구조

```
free-trader/
│
├── app/                        # 애플리케이션 진입점
│   └── main.py
│
├── api/                        # 외부 API 클라이언트
│   ├── ccxt_client.py         # CCXT 통합 클라이언트
│   ├── exchange_factory.py    # 거래소 팩토리
│   └── gpt_client.py          # GPT API
│
├── config/                     # 설정
│   ├── settings.py            # 전역 설정
│   └── exchanges.py           # 거래소 메타데이터
│
├── database/                   # 데이터베이스
│   ├── schema.py              # 테이블 스키마
│   └── repository.py          # CRUD 레포지토리
│
├── backtest/                   # 백테스팅 엔진
│   ├── engine.py              # 백테스트 로직
│   └── metrics.py             # 성과 지표
│
├── ui/                         # UI 컴포넌트
│   ├── main_window.py         # 메인 윈도우
│   ├── theme.py               # 커스텀 테마
│   ├── home_page.py           # 홈
│   ├── settings_page.py       # 설정
│   ├── data_page.py           # 데이터
│   ├── bot_page.py            # 봇
│   ├── bot_conditions.py      # 봇 생성
│   ├── bot_monitoring.py      # 봇 모니터링
│   ├── bot_history.py         # 거래 내역
│   ├── backtest_page.py       # 백테스트
│   ├── exchange_selector.py   # 거래소 선택기
│   └── log_widget.py          # 시스템 로그
│
├── utils/                      # 유틸리티
│   ├── logger.py              # 로깅
│   ├── crypto.py              # 암호화 (자격증명)
│   └── time_helper.py         # 시간/타임존
│
├── workers/                    # 백그라운드 워커
│   ├── data_collector.py      # 데이터 수집
│   ├── trading_bot.py         # 봇 실행
│   └── backtest_worker.py     # 백테스트 실행
│
└── data/                       # 데이터 디렉토리
    ├── trading_bot.db         # SQLite 데이터베이스
    └── credentials.enc        # 암호화된 자격증명
```

## 기술 스택

- **UI**: PySide6 6.4.2, QFluentWidgets 1.5.1
  - 커스텀 Gr8 DIY 테마 (다크모드 + 네온 그린/블루)
- **데이터베이스**: SQLite (QtSql)
- **거래소 API**: CCXT 4.0+
- **AI**: OpenAI GPT API
- **데이터 처리**: pandas, numpy
- **암호화**: cryptography

## 설치 및 실행

### 빠른 시작 (Windows)

1. Python 3.10+ 설치
2. 가상환경 생성 및 패키지 설치:
```powershell
python -m venv env
.\env\Scripts\pip.exe install -r requirements.txt
```
3. 앱 실행:
```powershell
.\env\Scripts\python.exe .\app\main.py
```

## 데이터베이스 스키마

### 멀티 거래소 지원 테이블
- `exchanges`: 거래소 메타데이터
- `exchange_credentials`: 거래소별 API 키
- `candles`: 캔들 데이터 (exchange_id 포함)
- `indicators`: 보조지표
- `bot_configs`: 봇 설정 (거래소별)
- `orders`: 주문 내역
- `positions`: 포지션
- `bot_logs`: 봇 로그
- `trades_history`: 거래 내역
- `backtest_results`: 백테스트 결과

## 주요 설계 원칙

1. **멀티 거래소**: CCXT 기반 통합 API
2. **멀티 스레드**: UI와 워커 스레드 분리
3. **KST 기준**: 모든 시간은 한국 표준시 사용
4. **데이터 보존**: 최대 200일치 데이터 유지
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
- CCXT 멀티 거래소 지원 (Top 100)
- 거래소별 데이터 수집
- 마틴게일 DCA 봇
- 실시간 모니터링
- 거래 내역 추적
- 컴팩트 UI 디자인

🚧 개발 중:
- 백테스팅 엔진
- 고급 차트 뷰
- 알림 시스템

---

**Made with ❤️ by 유튜브 <소피아빠>와 구독자님들**

**Powered by PySide6 + QFluentWidgets + CCXT**
