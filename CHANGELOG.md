# 변경 이력

모든 주목할 만한 변경 사항이 이 파일에 문서화됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 준수합니다.

## [Unreleased]

### 추가 예정
- 봇 실행 워커 (자동매매 로직)
- WebSocket 실시간 포지션 동기화
- 백테스팅 기능
- 차트 시각화
- 텔레그램 알림
- 다크/라이트 테마 커스터마이징

## [0.1.0] - 2025-12-08

### 추가
- ✅ 프로젝트 기본 구조 생성
- ✅ PySide6 + QFluentWidgets 기반 UI 프레임워크
- ✅ SQLite 데이터베이스 스키마
  - candles, indicators, bot_configs, orders, positions
  - bot_logs, system_logs, active_symbols, app_settings, trades_history
- ✅ OKX REST API 클라이언트
  - 인증 및 서명 생성
  - Rate Limiting 처리
  - 계정/시장/거래 API
- ✅ OKX WebSocket 클라이언트 (구조)
  - 자동 재연결 로직
  - 가격/포지션/주문 채널 구독
- ✅ GPT API 클라이언트
  - 연동 테스트
  - 시장 분석 기본 구조
- ✅ 보조지표 계산기
  - MA (20, 50, 100, 200)
  - MACD (12, 26, 9)
  - RSI (14)
  - Stochastic (14, 3)
  - Bollinger Bands (20, 2)
- ✅ 데이터 수집 워커
  - 과거 데이터 백필
  - 실시간 최신화
  - 자동 지표 계산
- ✅ 유지보수 워커
  - 1분 주기 실행
  - 200일 초과 데이터 삭제
- ✅ UI 페이지
  - 설정 페이지 (기본 연동, 거래소 설정)
  - 데이터 페이지 (수집 관리, 심볼 관리)
  - 봇 페이지 (조건설정, 모니터링, 내역)
- ✅ 시스템 로그 위젯
  - 레벨별 필터링
  - 실시간 로그 표시
- ✅ 자격증명 암호화 관리
  - PBKDF2 + Fernet 암호화
  - 로컬 파일 저장
- ✅ KST 기준 시간 처리
- ✅ Windows용 설치 스크립트
  - Python 자동 설치
  - 가상환경 생성
  - 패키지 설치
  - 앱 실행

### 문서
- ✅ README.md (프로젝트 소개)
- ✅ README_SETUP_ko.md (설치 가이드)
- ✅ ARCHITECTURE.md (아키텍처 문서)
- ✅ CONTRIBUTING.md (기여 가이드)
- ✅ CHANGELOG.md (변경 이력)

### 보안
- API 키 암호화 저장
- .gitignore에 민감 정보 제외
- Rate Limit 준수

## [0.0.1] - 2025-12-08 (환경 세팅 버전)

### 추가
- 프로젝트 초기 구조
- 환경 세팅 테스트용 GUI
- Windows 설치 스크립트

---

## 버전 규칙

- **Major (X.0.0)**: 호환되지 않는 API 변경
- **Minor (0.X.0)**: 하위 호환 기능 추가
- **Patch (0.0.X)**: 하위 호환 버그 수정

## 링크
- [Unreleased]: https://github.com/your-username/free-trader/compare/v0.1.0...HEAD
- [0.1.0]: https://github.com/your-username/free-trader/releases/tag/v0.1.0
- [0.0.1]: https://github.com/your-username/free-trader/releases/tag/v0.0.1


