# Gr8 DIY: 다중 거래소 암호화폐 자동매매 시스템
# Gr8 DIY: Multi-Exchange Cryptocurrency Automated Trading System

<div align="center">

![Gr8 DIY Logo](https://via.placeholder.com/400x200/0a0e27/00ff9f?text=Gr8+DIY)

**TDD 기반의 확장 가능한 암호화폐 자동거래 플랫폼**

[Test-Driven Development based Scalable Crypto Trading Platform]

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

</div>

## 목차 (Table of Contents)

- [프로젝트 개요 (Project Overview)](#프로젝트-개요-project-overview)
- [주요 특징 (Key Features)](#주요-특징-key-features)
- [시스템 아키텍처 (System Architecture)](#시스템-아키텍처-system-architecture)
- [TDD 개발 방법론 (TDD Development Methodology)](#tdd-개발-방법론-tdd-development-methodology)
- [설치 가이드 (Installation Guide)](#설치-가이드-installation-guide)
- [빠른 시작 (Quick Start)](#빠른-시작-quick-start)
- [사용법 (Usage)](#사용법-usage)
- [슬래시 명령어 가이드 (Slash Commands Guide)](#슬래시-명령어-가이드-slash-commands-guide)
- [TDD 서브-에이전트 시스템 (TDD Sub-Agent System)](#tdd-서브-에이전트-시스템-tdd-sub-agent-system)
- [개발 기여 가이드 (Development Contributing Guide)](#개발-기여-가이드-development-contributing-guide)
- [라이선스 (License)](#라이선스-license)

## 프로젝트 개요 (Project Overview)

**Gr8 DIY**는 다중 거래소를 지원하는 암호화폐 자동매매 시스템입니다. TDD(Test-Driven Development) 방법론을 기반으로 개발되어 안정성과 유지보수성을 최우선으로 고려합니다. 마틴게일 DCA 전략을 기본으로 하며, 38개 주요 거래소와의 연동을 지원합니다.

**Gr8 DIY** is a multi-exchange cryptocurrency automated trading system. Built on Test-Driven Development (TDD) methodology, it prioritizes stability and maintainability. It implements a Martingale DCA strategy as default and supports integration with 38 major exchanges.

### 핵심 가치 (Core Values)

- 🔒 **안정성 (Stability)**: TDD를 통한 높은 코드 품질과 테스트 커버리지 보장
- 🔄 **확장성 (Scalability)**: 모듈화된 아키텍처로 쉬운 기능 확장
- 🌍 **다중 거래소 (Multi-Exchange)**: 38개 거래소 API 통합 지원
- 🎯 **사용자 친화적 (User-Friendly)**: 직관적인 UI와 쉬운 설정
- 🔐 **보안 (Security)**: 암호화된 자격 증명 관리와 안전한 거래

- 🔒 **Stability**: High code quality and test coverage through TDD
- 🔄 **Scalability**: Easy feature extension with modular architecture
- 🌍 **Multi-Exchange**: Support for 38 exchange API integrations
- 🎯 **User-Friendly**: Intuitive UI and easy configuration
- 🔐 **Security**: Encrypted credential management and secure trading

## 주요 특징 (Key Features)

### 🔄 거래소 지원 (Exchange Support)
- **38개 주요 거래소**: 바이낸스, OKX, 비트겟, 바이빗, 쿠코인, 바이팅, 후오비, 크라켄 등
- **실시간 데이터**: WebSocket을 통한 가격 데이터 수신
- **API 레이트 리밋**: 거래소별 제한 준수
- **테스트넷 지원**: 안전한 테스트 환경 제공

**38 Major Exchanges**: Binance, OKX, Bitget, Bybit, KuCoin, Bithumb, Huobi, Kraken, etc.
**Real-time Data**: Price data reception via WebSocket
**API Rate Limiting**: Compliance with exchange-specific limits
**Testnet Support**: Safe testing environment provided

### 🤖 자동거래 전략 (Automated Trading Strategy)
- **마틴게일 DCA**: 평균 단가 낮추기 전략
- **손절/익절**: 자동 손실 제한 및 수익 실현
- **실시간 모니터링**: 포지션 추적 및 성과 분석
- **위험 관리**: 자본 관리 및 리스크 제어

**Martingale DCA**: Average cost reduction strategy
**Stop-Loss/Take-Profit**: Automatic loss limitation and profit realization
**Real-time Monitoring**: Position tracking and performance analysis
**Risk Management**: Capital management and risk control

### 📊 데이터 분석 (Data Analysis)
- **과거 데이터 수집**: 다중 타임프레임 지원
- **기술적 지표**: RSI, MACD, 볼린저밴드 등 50+ 지표
- **백테스팅**: 과거 데이터 기반 전략 검증
- **성과 리포트**: 수익률, MDD, 샤프 비율 분석

**Historical Data Collection**: Multi-timeframe support
**Technical Indicators**: 50+ indicators including RSI, MACD, Bollinger Bands
**Backtesting**: Strategy validation based on historical data
**Performance Reports**: Return rate, MDD, Sharpe ratio analysis

### 🎨 사용자 인터페이스 (User Interface)
- **현대적 UI**: PySide6 + QFluentWidgets 기반
- **다크 테마**: 사용자 친화적인 다크 모드
- **실시간 대시보드**: 현재 상태 및 성과 시각화
- **간편한 설정**: 마법사 기반 초기 설정

**Modern UI**: Based on PySide6 + QFluentWidgets
**Dark Theme**: User-friendly dark mode
**Real-time Dashboard**: Current status and performance visualization
**Easy Configuration**: Wizard-based initial setup

## 시스템 아키텍처 (System Architecture)

```
Gr8 DIY System Architecture
┌─────────────────────────────────────────────────────────────┐
│                    Gr8 DIY Application                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   UI Layer      │ │  Business Layer │ │   Data Layer    │ │
│  │                 │ │                 │ │                 │ │
│  │ • Main Window   │ │ • Trading Bot   │ │ • SQLite DB     │ │
│  │ • Settings      │ │ • Strategies    │ │ • File Storage  │ │
│  │ • Data Viewer   │ │ • Risk Manager  │ │                 │ │
│  │ • Bot Control   │ │                 │ │                 │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   Exchange API  │ │   Data Workers  │ │  Maintenance    │ │
│  │                 │ │                 │ │                 │ │
│  │ • CCXT Library  │ │ • Collector     │ │ • Cleanup       │ │
│  │ • WebSocket     │ │ • Processor     │ │ • Backup        │ │
│  │ • Rate Limit    │ │ • Monitor       │ │ • Optimization  │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    TDD Framework                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │  Developer      │ │   Reviewer      │ │   Refactory     │ │
│  │  Agent          │ │  Agent          │ │  Agent          │ │
│  │                 │ │                 │ │                 │ │
│  │ • Test Writing  │ │ • Code Review   │ │ • Optimization  │ │
│  │ • Implementation│ │ • Security      │ │ • Refactoring   │ │
│  │ • Unit Testing  │ │ • Performance   │ │ • Documentation│ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 기술 스택 (Tech Stack)

- **Frontend**: PySide6, QFluentWidgets
- **Backend**: Python 3.8+, asyncio
- **Database**: SQLite (다중 거래소 스키마)
- **Exchange Integration**: CCXT
- **Testing**: pytest, unittest
- **Documentation**: Markdown (한글/영어 이중 지원)

**Frontend**: PySide6, QFluentWidgets
**Backend**: Python 3.8+, asyncio
**Database**: SQLite (multi-exchange schema)
**Exchange Integration**: CCXT
**Testing**: pytest, unittest
**Documentation**: Markdown (Korean/English dual support)

## TDD 개발 방법론 (TDD Development Methodology)

Gr8 DIY는 TDD(Test-Driven Development) 방법론을 채택하여 소프트웨어의 품질과 안정성을 보장합니다. 세 개의 전문화된 서브-에이전트 시스템을 통해 체계적인 개발 프로세스를 운영합니다.

**Gr8 DIY adopts TDD (Test-Driven Development) methodology to ensure software quality and stability. It operates a systematic development process through three specialized sub-agent systems.**

### TDD 사이클 (TDD Cycle)

1. **Red 단계**: 실패하는 테스트 작성
   - Developer Agent가 새로운 기능에 대한 실패 테스트 작성
   - 기능 명세를 기반으로 테스트 케이스 정의

2. **Green 단계**: 테스트 통과하는 최소 코드 작성
   - Developer Agent가 테스트 통과를 위한 최소 구현
   - 기본 기능 동작 검증

3. **Refactor 단계**: 코드 최적화 및 개선
   - Reviewer Agent의 코드 리뷰 후 Refactory Agent가 최적화
   - 성능 개선 및 코드 품질 향상

**1. Red Phase**: Write failing tests
   - Developer Agent writes failing tests for new features
   - Define test cases based on feature specifications

**2. Green Phase**: Write minimal code to pass tests
   - Developer Agent implements minimal code for test passing
   - Basic functionality verification

**3. Refactor Phase**: Code optimization and improvement
   - Refactory Agent optimizes after Reviewer Agent's code review
   - Performance improvement and code quality enhancement**

### 서브-에이전트 시스템 (Sub-Agent System)

#### Developer Agent (개발자 에이전트)
- **역할**: 테스트 우선 개발 및 최소한의 구현
- **전문 분야**: 단위 테스트, 통합 테스트, API 모킹
- **주요 책임**: Red/Green 단계, 기본 기능 검증

**Role**: Test-first development and minimal implementation
**Expertise**: Unit testing, integration testing, API mocking
**Key Responsibilities**: Red/Green phases, basic functionality verification**

#### Reviewer Agent (리뷰어 에이전트)
- **역할**: 코드 및 테스트 품질 검증
- **전문 분야**: 암호화폐 거래 로직, 보안, 성능 분석
- **주요 책임**: 코드 리뷰, 에지 케이스 검증, 아키텍처 준수

**Role**: Code and test quality verification
**Expertise**: Crypto trading logic, security, performance analysis
**Key Responsibilities**: Code review, edge case validation, architecture compliance**

#### Refactory Agent (리팩토리 에이전트)
- **역할**: 코드 최적화 및 개선
- **전문 분야**: 성능 최적화, 리팩토링, 기술 부채 해소
- **주요 책임**: 코드 리팩토링, 중복 제거, 설계 패턴 적용

**Role**: Code optimization and improvement
**Expertise**: Performance optimization, refactoring, technical debt resolution
**Key Responsibilities**: Code refactoring, duplication removal, design pattern application**

자세한 내용은 [TDD 서브-에이전트 라우팅 규칙](docs/TDD_SUB_AGENT_ROUTING.md)을 참조하세요.

For details, see [TDD Sub-Agent Routing Rules](docs/TDD_SUB_AGENT_ROUTING.md).

## 설치 가이드 (Installation Guide)

### 시스템 요구사항 (System Requirements)

- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 이상
- **RAM**: 최소 4GB, 권장 8GB
- **저장 공간**: 최소 1GB

**OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)
**Python**: 3.8 or higher
**RAM**: Minimum 4GB, Recommended 8GB
**Storage**: Minimum 1GB

### 설치 단계 (Installation Steps)

#### 1. 리포지토리 복제 (Clone Repository)
```bash
git clone https://github.com/your-username/gr8diy.git
cd gr8diy
```

#### 2. 가상환경 생성 (Create Virtual Environment)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 3. 의존성 설치 (Install Dependencies)
```bash
pip install -r requirements.txt
```

#### 4. 데이터베이스 초기화 (Initialize Database)
```bash
python scripts/init_database.py
```

#### 5. 설정 파일 생성 (Create Configuration)
```bash
# 설정 파일 복사
cp config/settings_template.json config/settings.json

# API 키 설정 (각 거래소에서 발급받은 API 키)
# 설정 파일에 API 키를 안전하게 입력하세요
```

## 빠른 시작 (Quick Start)

### 1. 애플리케이션 실행 (Run Application)
```bash
python app/main.py
```

### 2. 초기 설정 (Initial Setup)

#### 거래소 API 설정 (Exchange API Setup)
1. **애플리케이션 실행** 후 Settings 페이지로 이동
2. **Exchange Integration** 탭에서 사용할 거래소 선택
3. **API Key**와 **Secret** 입력 (거래소 웹사이트에서 발급)
4. **Test Connection** 버튼으로 연결 확인
5. **Save** 버튼으로 설정 저장

**After running the application**, go to Settings page
Select exchange in **Exchange Integration** tab
Input **API Key** and **Secret** (issued from exchange website)
Verify connection with **Test Connection** button
Save settings with **Save** button

#### 봇 설정 (Bot Configuration)
1. **Bot 페이지**로 이동
2. **거래소**와 **거래할 종목** 선택
3. **전략 파라미터** 설정 (초기 투자금, 손절/익절 등)
4. **Start Bot** 버튼으로 자동거래 시작

Go to **Bot page**
Select **exchange** and **trading symbol**
Configure **strategy parameters** (initial investment, stop-loss/take-profit, etc.)
Start automated trading with **Start Bot** button

### 3. 데이터 수집 (Data Collection)

```bash
# 슬래시 명령어를 통한 데이터 수집
/data-collect binance BTC/USDT 1m

# 또는 UI에서 데이터 페이지로 이동하여 수집 시작
```

## 사용법 (Usage)

### 기본 워크플로우 (Basic Workflow)

1. **거래소 연동**: API 키를 통한 거래소 연결 설정
2. **데이터 수집**: 과거 데이터 수집 및 실시간 데이터 구독
3. **전략 설정**: 마틴게일 DCA 파라미터 설정
4. **봇 실행**: 자동거래 시작 및 모니터링
5. **성과 분석**: 거래 결과 및 수익률 확인

**1. Exchange Integration**: Setup exchange connection via API keys
**2. Data Collection**: Collect historical data and subscribe real-time data
**3. Strategy Setup**: Configure Martingale DCA parameters
**4. Bot Execution**: Start automated trading and monitoring
**5. Performance Analysis**: Review trading results and returns**

### 주요 기능 (Key Features)

#### 데이터 수집 및 관리 (Data Collection & Management)
```bash
# 바이낸스 BTC/USDT 1분봉 데이터 수집
/data-collect binance BTC/USDT 1m

# 여러 종목 데이터 수집
/data-collect okx ETH/USDT,BTC/USDT 1m

# 데이터베이스 최적화
/compact

# 데이터 백업
/data-backup
```

#### 봇 운영 (Bot Operations)
```bash
# 봇 시작
/bot-start binance btc_config.json

# 봇 상태 확인
/bot-status

# 포지션 정보 조회
/positions

# 봇 중지
/bot-stop
```

#### 분석 및 보고 (Analysis & Reporting)
```bash
# 백테스팅
/backtest martingale 2024-01-01 2024-12-31

# 성과 리포트
/report performance --period 2024-12

# 주요 지표 확인
/metrics
```

## 슬래시 명령어 가이드 (Slash Commands Guide)

Gr8 DIY는 강력한 슬래시 명령어 시스템을 제공하여 빠르고 효율적인 시스템 제어를 지원합니다.

**Gr8 DIY provides a powerful slash command system for fast and efficient system control.**

### TDD 관련 명령어 (TDD-Related Commands)
```bash
# TDD 개발 시작
/tdd-start "새로운 기능 구현"

# 코드 리뷰 요청
/tdd-review ui/trading_bot.py

# 코드 리팩토링
/tdd-refactor performance

# 테스트 커버리지 확인
/tdd-coverage trading-bot

# TDD 상태 확인
/tdd-status
```

### 프로젝트 관리 (Project Management)
```bash
# 프로젝트 초기화
/init

# 애플리케이션 빌드
/build

# 전체 테스트 실행
/test

# 시스템 상태 점검
/health-check
```

### 데이터 관리 (Data Management)
```bash
# 데이터 수집
/data-collect <exchange> <symbol> [timeframe]

# 데이터 백업
/data-backup

# 오래된 데이터 정리
/data-cleanup [days]
```

전체 명령어 목록은 [슬래시 명령어 가이드](docs/SLASH_COMMANDS_GUIDE.md)를 참조하세요.

For the complete command list, see [Slash Commands Guide](docs/SLASH_COMMANDS_GUIDE.md).

## TDD 서브-에이전트 시스템 (TDD Sub-Agent System)

### 에이전트 호출 규칙 (Agent Calling Rules)

```
명령어 실행 → 자동 에이전트 라우팅 → 에이전트 처리 → 결과 반환

Command Execution → Auto Agent Routing → Agent Processing → Result Return

예시 (Example):
/tdd-start "새로운 기능 구현"
    ↓
Developer Agent 활성화
    ↓
Developer Agent: 테스트 작성 및 구현
    ↓
Reviewer Agent 활성화 (자동)
    ↓
Refactory Agent 활성화 (자동)
    ↓
최종 결과 반환
```

### 우선순위 기반 라우팅 (Priority-Based Routing)

#### 높음 (High Priority)
1. **보안 관련 변경**: 보안 취약점 수정, API 키 처리
2. **거래 로직 변경**: 수익/손실 로직, 포지션 관리
3. **데이터 무결성**: 데이터베이스 스키마 변경, 데이터 검증
4. **금융 계산**: 이익 계산, 수수료 처리

**Security-related changes**: Security vulnerability fixes, API key handling
**Trading logic changes**: Profit/loss logic, position management
**Data integrity**: Database schema changes, data validation
**Financial calculations**: Profit calculation, fee processing

#### 중간 (Medium Priority)
1. **UI/UX 개선**: 사용자 인터페이스 변경, 사용자 경험
2. **API 연동**: 새로운 거래소 추가, API 변경
3. **성능 최적화**: 응답 속도 개선, 메모리 사용량
4. **테스트 인프라**: 테스트 프레임워크 개선

**UI/UX improvements**: User interface changes, user experience
**API integration**: New exchange additions, API changes
**Performance optimization**: Response speed improvement, memory usage
**Test infrastructure**: Test framework improvements

#### 낮음 (Low Priority)
1. **문서화**: 주석 추가, README 업데이트
2. **코드 스타일**: 포맷팅, 명명 규칙
3. **리팩토링**: 코드 구조 개선, 변수명 변경

**Documentation**: Comment additions, README updates
**Code style**: Formatting, naming conventions
**Refactoring**: Code structure improvements, variable name changes

## 개발 기여 가이드 (Development Contributing Guide)

### 개발 환경 설정 (Development Environment Setup)

1. **Fork** 리포지토리
2. **Feature 브랜치** 생성
3. **TDD 사이클** 따르기
4. **Pull Request** 제출

**1. Fork** repository
**2. Create feature branch**
**3. Follow TDD cycle**
**4. Submit Pull Request**

### TDD 기여 프로세스 (TDD Contribution Process)

```bash
# 1. 새 기능 TDD 개발 시작
/tdd-start "새로운 코인베이스 선물 지원 기능"

# 2. 개발 진행 상태 확인
/tdd-status

# 3. 코드 리뷰 요청
/tdd-review

# 4. 테스트 커버리지 확인
/tdd-coverage

# 5. 성능 최적화
/tdd-refactor performance

# 6. 최종 결과 확인
/tdd-status --detailed
```

### 코드 컨벤션 (Code Conventions)

- **Python**: PEP 8 따르기
- **문자열**: UTF-8 인코딩, 영문/한글 주석 병행
- **테스트**: pytest 사용, 최소 80% 커버리지
- **문서**: Markdown, 한글 우선 영문 병행

**Python**: Follow PEP 8
**Strings**: UTF-8 encoding, parallel Korean/English comments
**Testing**: Use pytest, minimum 80% coverage
**Documentation**: Markdown, Korean primary with English secondary

### 커밋 메시지 규칙 (Commit Message Rules)

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드/유틸리티 작업

feat: Add new feature
fix: Fix bug
docs: Modify documentation
style: Code formatting
refactor: Code refactoring
test: Add/modify tests
chore: Build/utility tasks
```

## 프로젝트 구조 (Project Structure)

```
gr8diy/
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
│   ├── exchanges.py           # 거래소 메타데이터
│   └── ui_settings.json       # UI 설정
│
├── database/                   # 데이터베이스
│   ├── schema.py              # 테이블 스키마
│   └── repository.py          # CRUD 레포지토리
│
├── docs/                       # 문서
│   ├── TDD_SUB_AGENT_ROUTING.md    # TDD 서브-에이전트 규칙
│   └── SLASH_COMMANDS_GUIDE.md     # 슬래시 명령어 가이드
│
├── indicators/                  # 기술적 지표
│   └── calculator.py          # 지표 계산기
│
├── ui/                         # UI 컴포넌트
│   ├── main_window.py         # 메인 윈도우
│   ├── theme.py               # 커스텀 테마
│   ├── home_page.py           # 홈
│   ├── settings_page.py       # 설정
│   ├── data_page.py           # 데이터
│   ├── bot_conditions.py      # 봇 생성 조건
│   ├── exchange_selector.py   # 거래소 선택기
│   └── [other UI files...]    # 기타 UI 파일
│
├── utils/                      # 유틸리티
│   ├── logger.py              # 로깅
│   ├── crypto.py              # 암호화 (자격증명)
│   └── time_helper.py         # 시간/타임존
│
├── workers/                    # 백그라운드 워커
│   ├── data_collector.py      # 데이터 수집
│   ├── trading_bot.py         # 봇 실행
│   └── maintenance.py         # 유지보수
│
├── data/                       # 데이터 디렉토리
│   └── trading_bot.db         # SQLite 데이터베이스
│
├── scripts/                    # 스크립트
│   ├── 1_create_venv.bat      # 가상환경 생성
│   ├── 2_install_packages.bat # 패키지 설치
│   ├── 3_run_app.bat          # 앱 실행
│   └── init_database.py       # 데이터베이스 초기화
│
└── [other files...]           # 기타 파일
```

## 주요 설계 원칙 (Key Design Principles)

1. **멀티 거래소**: CCXT 기반 통합 API
2. **TDD 기반 개발**: 높은 코드 품질과 테스트 커버리지
3. **모듈화 아키텍처**: 독립적인 컴포넌트와 느슨한 결합
4. **KST 기준**: 모든 시간은 한국 표준시 사용
5. **데이터 보존**: 최대 200일치 데이터 유지
6. **에러 처리**: 모든 오류 로깅 및 UI 알림
7. **보안**: 암호화된 자격 증명 관리

**1. Multi-Exchange**: CCXT based integrated API
**2. TDD-Based Development**: High code quality and test coverage
**3. Modular Architecture**: Independent components and loose coupling
**4. KST Based**: All times use Korean Standard Time
**5. Data Retention**: Maximum 200 days data retention
**6. Error Handling**: All errors logged and UI notifications
**7. Security**: Encrypted credential management

## 보안 (Security)

- API 키는 로컬에 암호화 저장 (PBKDF2 + Fernet)
- `.gitignore`에 민감 정보 제외
- 자격증명 파일은 시스템별 암호화
- 거래소 연결 시 항상 테스트넷 우선 지원

- API keys are encrypted and stored locally (PBKDF2 + Fernet)
- Exclude sensitive information in `.gitignore`
- Credential files are system-encrypted
- Always support testnet first for exchange connections

## 라이선스 (License)

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 주의사항 (Disclaimer)

⚠️ **투자 경고 (Investment Warning)**
- 이 소프트웨어는 교육 목적으로 제공됩니다
- 실제 거래 시 금전적 손실 위험이 있습니다
- 모든 투자 결정은 본인의 책임입니다
- API 키는 절대 타인과 공유하지 마세요

- This software is provided for educational purposes
- Actual trading involves risk of financial loss
- All investment decisions are your own responsibility
- Never share your API keys with others

## 개발 상태 (Development Status)

✅ **완료 (Completed)**:
- CCXT 멀티 거래소 지원 (38개 거래소)
- 거래소별 데이터 수집
- 마틴게일 DCA 봇
- 실시간 모니터링
- 거래 내역 추적
- 컴팩트 UI 디자인
- TDD 서브-에이전트 시스템 설계

🚧 **개발 중 (In Development)**:
- 백테스팅 엔진
- 고급 차트 뷰
- 알림 시스템
- 웹 인터페이스

**✅ Completed**:
- CCXT multi-exchange support (38 exchanges)
- Exchange-specific data collection
- Martingale DCA bot
- Real-time monitoring
- Trade history tracking
- Compact UI design
- TDD sub-agent system design

**🚧 In Development**:
- Backtesting engine
- Advanced chart view
- Notification system
- Web interface

---

## 지원 및 문의 (Support & Contact)

- **GitHub Issues**: [버그 리포트 및 기능 요청](https://github.com/your-username/gr8diy/issues)
- **Discord**: [커뮤니티 채널](https://discord.gg/gr8diy)
- **Email**: support@gr8diy.com

**GitHub Issues**: [Bug reports and feature requests](https://github.com/your-username/gr8diy/issues)
**Discord**: [Community channel](https://discord.gg/gr8diy)
**Email**: support@gr8diy.com

---

<div align="center">

**⭐ Star this repository if it helps you!**

**Made with ❤️ for the crypto trading community**

**Powered by PySide6 + QFluentWidgets + CCXT**

</div>