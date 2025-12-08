# OKX Trading Bot - 아키텍처 문서

## 개요

이 문서는 OKX Trading Bot의 전체 아키텍처와 설계 결정 사항을 설명합니다.

## 레이어 구조

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│         (UI: main_window, pages, widgets)               │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│        (Workers: data_collector, maintenance)           │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│                     Domain Layer                         │
│      (Indicators, Business Logic - 추후 확장)           │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                    │
│     (API Clients, Database, Utils, Config)              │
└─────────────────────────────────────────────────────────┘
```

## 모듈별 책임

### 1. UI Layer (`ui/`)
**책임**: 사용자 인터페이스 렌더링 및 사용자 입력 처리

- `main_window.py`: 메인 윈도우, 네비게이션
- `settings_page.py`: API 자격증명, 거래소 설정
- `data_page.py`: 데이터 수집 관리
- `bot_page.py`: 봇 메뉴 컨테이너
- `bot_conditions.py`: 봇 매매 조건 설정
- `bot_monitoring.py`: 실시간 포지션/로그 모니터링
- `bot_history.py`: 거래 내역 및 통계
- `log_widget.py`: 시스템 로그 뷰

**설계 원칙**:
- Qt Signal/Slot 패턴 사용
- 비즈니스 로직은 최소화, 워커/서비스에 위임
- QFluentWidgets로 모던 UI 구현

### 2. Workers (`workers/`)
**책임**: 백그라운드 작업 처리 (UI 스레드와 분리)

- `data_collector.py`: 
  - OKX API를 통한 캔들 데이터 수집
  - 백필 및 실시간 최신화
  - 보조지표 계산 및 저장
  
- `maintenance.py`:
  - 1분 주기 실행
  - 200일 초과 데이터 삭제
  - 통계 캐시 업데이트

**설계 원칙**:
- QThread 기반 워커 패턴
- Signal로 UI에 상태 전달
- 재연결 로직 포함 (resilience)

### 3. API Clients (`api/`)
**책임**: 외부 서비스와 통신

- `okx_client.py`:
  - OKX REST API 래퍼
  - Rate Limiting 처리
  - 인증 및 서명 생성
  
- `okx_websocket.py`:
  - OKX WebSocket 클라이언트
  - 실시간 가격/포지션/주문 구독
  - 자동 재연결
  
- `gpt_client.py`:
  - OpenAI GPT API 클라이언트
  - 시장 분석 (추후 확장)

**설계 원칙**:
- 각 API별 클라이언트 클래스 분리
- Rate Limit 준수 (OKX 429 에러 방지)
- Exponential Backoff 재시도

### 4. Database (`database/`)
**책임**: 데이터 영속성 관리

- `schema.py`: 
  - SQLite 테이블 스키마 정의
  - 초기화 함수
  
- `repository.py`:
  - Repository 패턴으로 CRUD 추상화
  - 각 테이블별 레포지토리 클래스

**테이블**:
```
candles          → 캔들 데이터
indicators       → 보조지표
bot_configs      → 봇 설정
orders           → 주문 내역
positions        → 포지션
bot_logs         → 봇 로그
system_logs      → 시스템 로그
active_symbols   → 활성 심볼
app_settings     → 앱 설정
trades_history   → 거래 완료 내역
```

**설계 원칙**:
- QtSql 사용 (PySide6 내장)
- 모든 timestamp는 KST 기준
- 인덱스로 쿼리 최적화

### 5. Indicators (`indicators/`)
**책임**: 기술적 지표 계산

- `calculator.py`:
  - MA, MACD, RSI, Stochastic, Bollinger Bands
  - pandas 기반 벡터 연산

**설계 원칙**:
- Stateless 함수형 설계
- 파라미터는 `config/settings.py`에서 관리

### 6. Utils (`utils/`)
**책임**: 공통 유틸리티

- `logger.py`:
  - 전역 로거
  - Signal로 UI에 로그 전달
  
- `crypto.py`:
  - API 키 암호화/복호화
  - PBKDF2 + Fernet 사용
  
- `time_helper.py`:
  - KST ↔ UTC 변환
  - Timestamp 포맷팅

**설계 원칙**:
- 싱글톤 패턴 (logger, time_helper)
- 플랫폼 독립적 구현

### 7. Config (`config/`)
**책임**: 전역 설정 및 상수

- `settings.py`:
  - API 엔드포인트
  - Rate Limit 설정
  - 보조지표 파라미터
  - UI 설정

**설계 원칙**:
- 환경별 설정 분리 가능하도록 구조화
- 하드코딩 최소화

## 데이터 흐름

### 1. 데이터 수집 플로우
```
[OKX REST API]
      ↓
[data_collector.py]
      ↓
[CandlesRepository] → [DB: candles]
      ↓
[IndicatorCalculator]
      ↓
[IndicatorsRepository] → [DB: indicators]
```

### 2. 봇 실행 플로우 (추후 구현)
```
[bot_worker.py]
      ↓
[DB: indicators] → 조건 검사
      ↓
[OKX REST API] → 주문 생성
      ↓
[OrdersRepository] → [DB: orders]
      ↓
[OKX WebSocket] → 실시간 체결 확인
      ↓
[PositionsRepository] → [DB: positions]
```

### 3. UI 업데이트 플로우
```
[Worker Thread]
      ↓ (Signal)
[Main Thread: UI]
      ↓
[Qt Widget 업데이트]
```

## 스레드 모델

```
Main Thread (UI)
├─ QApplication
├─ MainWindow
└─ All UI Widgets

Worker Thread 1: DataCollector
├─ 캔들 데이터 수집
├─ 보조지표 계산
└─ DB 저장

Worker Thread 2: Maintenance
├─ 1분 주기 실행
└─ 오래된 데이터 삭제

Worker Thread 3: OKX WebSocket
├─ 실시간 가격 구독
├─ 포지션 업데이트
└─ 주문 체결 알림

Worker Thread 4: Bot (추후)
├─ 인터벌마다 실행
├─ 조건 검사
└─ 주문 생성/취소
```

## 보안 설계

1. **자격증명 저장**
   - API 키는 로컬 파일에 Fernet 암호화
   - PBKDF2로 파생된 키 사용
   - Windows 환경: 파일 숨김 속성 적용

2. **네트워크 통신**
   - HTTPS/WSS만 사용
   - OKX API 서명 검증

3. **로깅**
   - 민감 정보 로그 출력 금지
   - 에러 로그는 DB + 파일 양쪽 저장

## 에러 처리 전략

1. **Network Errors**
   - Rate Limit (429): 60초 Cooldown
   - Connection Error: Exponential Backoff
   - WebSocket 끊김: 자동 재연결

2. **Data Errors**
   - 데이터 검증 실패: 로그 기록 후 스킵
   - DB 오류: 트랜잭션 롤백

3. **UI Errors**
   - InfoBar로 사용자 알림
   - 시스템 로그에 기록

## 성능 최적화

1. **Database**
   - 인덱스: (symbol, timeframe, timestamp)
   - Batch Insert로 대량 데이터 처리
   - 페이지네이션으로 메모리 절약

2. **UI**
   - 가상 스크롤 (대량 리스트)
   - 로그 최대 1000줄 제한
   - Lazy Loading

3. **API**
   - Rate Limit 여유있게 설정
   - 캐싱 (필요 시)

## 확장성 고려사항

### 추가 거래소 지원
- `api/` 하위에 거래소별 클라이언트 추가
- 공통 인터페이스 정의 (ABC)

### 추가 전략
- `strategies/` 모듈 생성
- Strategy 패턴으로 다양한 전략 구현

### 백테스팅
- 히스토리 데이터 기반 시뮬레이션
- `backtesting/` 모듈 추가

## 테스트 전략

### Unit Tests (추후)
- Repository 메서드
- Indicator 계산
- API 클라이언트 (Mock)

### Integration Tests
- DB 스키마 생성
- API 연동 테스트

### UI Tests
- 수동 E2E 테스트

## 배포

### 패키징 (추후)
- PyInstaller로 단일 실행 파일 생성
- NSIS로 인스톨러 제작

### 업데이트
- GitHub Releases 활용
- 자동 업데이트 체커 (선택)

---

## 주요 설계 결정 근거

### 왜 QtSql?
- PySide6 내장, 추가 의존성 없음
- 경량 SQLite에 적합
- Qt 생태계와 통합

### 왜 QThread?
- Qt의 공식 멀티스레딩 방식
- Signal/Slot과 자연스러운 통합
- UI 스레드 안전성 보장

### 왜 Repository 패턴?
- DB 로직과 비즈니스 로직 분리
- 테스트 용이성
- 나중에 ORM으로 전환 가능

### 왜 KST 기준?
- 한국 사용자 대상
- 타임존 혼동 방지
- 일관된 시간 표시

---

**이 아키텍처는 확장과 유지보수를 고려하여 설계되었습니다.**


