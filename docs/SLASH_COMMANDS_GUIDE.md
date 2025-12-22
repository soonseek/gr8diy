# 유용한 슬래시 명령어 가이드
# Useful Slash Commands Guide

## 개요 (Overview)
Claude Code에서 사용할 수 있는 유용한 슬래시 명령어들을 정의합니다. TDD 개발 워크플로우를 포함한 Gr8 DIY 암호화폐 자동매매 프로젝트의 개발 효율성을 높이기 위한 명령어들입니다.

## TDD 관련 명령어 (TDD-Related Commands)

### `/tdd-start <feature_description>`
**용도:** 새로운 기능에 대한 TDD 개발 사이클 시작
**사용 예:**
```bash
# 바이낸스 선물 지원 기능 추가
/tdd-start 바이낸스 선물 지원 기능 구현

# 새로운 거래소 API 연동
/tdd-start 코인베이스 API 연동 구현

# 기존 기능 리팩토링
/tdd-start 수익률 계산 로직 개선
```

### `/tdd-review [file_path]`
**용도:** 코드 리뷰 및 품질 검증 요청
**사용 예:**
```bash
# 특정 파일 리뷰
/tdd-review ui/trading_bot.py

# 현재 변경사항 전체 리뷰
/tdd-review

# 특정 디렉토리 리뷰
/tdd-review api/
```

### `/tdd-refactor <scope>`
**용도:** 코드 리팩토링 및 최적화
**사용 예:**
```bash
# 전체 코드베이스 리팩토링
/tdd-refactor all

# 성능 최적화
/tdd-refactor performance

# 특정 모듈 리팩토링
/tdd-refactor trading_bot
```

### `/tdd-coverage [module]`
**용도:** 테스트 커버리지 보고 생성
**사용 예:**
```bash
# 전체 커버리지 보고
/tdd-coverage

# 특정 모듈 커버리지
/tdd-coverage trading_bot

# API 관련 커버리지
/tdd-coverage api/
```

### `/tdd-status`
**용도:** 현재 TDD 워크플로우 상태 확인
**사용 예:**
```bash
# 전체 상태 확인
/tdd-status

# 특정 에이전트 상태 확인
/tdd-status developer
```

## 프로젝트 관리 명령어 (Project Management Commands)

### `/init`
**용도:** 프로젝트 초기화 및 환경 설정
**기능:**
- 가상환경 생성
- 의존성 패키지 설치
- 데이터베이스 초기화
- 기본 설정 파일 생성

**사용 예:**
```bash
# 프로젝트 초기화
/init

# 개발 환경 설정
/init --dev

# 테스트 환경 설정
/init --test
```

### `/build`
**용도:** 애플리케이션 빌드
**기능:**
- PyInstaller를 사용한 실행 파일 생성
- 종속성 포함
- 최적화된 배포판 생성

**사용 예:**
```bash
# 기본 빌드
/build

# 릴리즈 빌드
/build --release

# 테스트 빌드
/build --debug
```

### `/test`
**용도:** 전체 테스트 스위트 실행
**기능:**
- 단위 테스트 실행
- 통합 테스트 실행
- 커버리지 보고 생성

**사용 예:**
```bash
# 전체 테스트 실행
/test

# 단위 테스트만 실행
/test --unit

# 특정 테스트 파일 실행
/test test_trading_bot.py
```

## 데이터 관리 명령어 (Data Management Commands)

### `/data-collect <exchange> <symbol> [timeframe]`
**용도:** 과거 데이터 수집
**사용 예:**
```bash
# 바이낸스 BTC/USDT 1분봉 데이터 수집
/data-collect binance BTC/USDT 1m

# 여러 심볼 데이터 수집
/data-collect okx ETH/USDT,BTC/USDT 1m

# 특정 기간 데이터 수집
/data-collect binance BTC/USDT 1d --start-date 2024-01-01
```

### `/data-backup`
**용도:** 데이터베이스 백업
**기능:**
- SQLite 데이터베이스 백업
- 설정 파일 백업
- 거래 내역 백업

**사용 예:**
```bash
# 전체 데이터 백업
/data-backup

# 설정만 백업
/data-backup --config-only

# 특정 날짜 백업
/data-backup --date 2024-12-22
```

### `/data-cleanup [days]`
**용도:** 오래된 데이터 정리
**사용 예:**
```bash
# 30일 이전 데이터 정리
/data-cleanup 30

# 설정된 보관 기간보다 오래된 데이터 정리
/data-cleanup

```

## 거래 관련 명령어 (Trading Commands)

### `/bot-start <exchange> <config>`
**용도:** 자동매 봇 시작
**사용 예:**
```bash
# 바이낸스 BTC/USDT 봇 시작
/bot-start binance btc_usdt_config.json

# 설정 파일 로드하여 봇 시작
/bot-start okx --config configs/eth_strategy.json

# 테스트넷 모드 봇 시작
/bot-start binance --testnet
```

### `/bot-stop [bot_id]`
**용도:** 자동매 봇 중지
**사용 예:**
```bash
# 모든 봇 중지
/bot-stop

# 특정 봇 중지
/bot-stop bot_12345

# 강제 중지 (즉시)
/bot-stop --force
```

### `/bot-status [bot_id]`
**용도:** 봇 상태 확인
**사용 예:**
```bash
# 모든 봇 상태 확인
/bot-status

# 특정 봇 상태 확인
/bot-status bot_12345

# 상세 정보 포함
/bot-status --detailed
```

### `/positions [exchange]`
**용도:** 현재 포지션 정보 조회
**사용 예:**
```bash
# 모든 거래소 포지션 조회
/positions

# 바이낸스 포지션만 조회
/positions binance

# 미실현 수익 포함 조회
/positions --include-unrealized
```

## 분석 및 보고 명령어 (Analysis & Reporting Commands)

### `/backtest <strategy> <start_date> <end_date>`
**용도:** 백테스팅 실행
**사용 예:**
```bash
# 마틴게일 전략 백테스팅
/backtest martingale 2024-01-01 2024-12-31

# 특정 설정으로 백테스팅
/backtest --config configs/martingale_config.json 2024-01-01 2024-12-31

# 결과 CSV로 내보내기
/backtest martingale 2024-01-01 2024-12-31 --export-csv
```

### `/report <type> [options]`
**용도:** 분석 리포트 생성
**사용 예:**
```bash
# 성과 리포트 생성
/report performance --period 2024-12

# 거래 내역 리포트
/report trades --exchange binance --symbol BTC/USDT

# 위험 분석 리포트
/report risk --include-variance
```

### `/metrics`
**용도:** 주요 지표 대시보드
**기능:**
- 총 수익률
- 승률 분석
- 최대 손실(MDD)
- 샤프 비율

**사용 예:**
```bash
# 전체 지표 확인
/metrics

# 특정 기간 지표
/metrics --period 2024-12

# 특정 거래소 지표
/metrics --exchange binance
```

## 유틸리티 명령어 (Utility Commands)

### `/compact`
**용도:** 데이터베이스 최적화
**기능:**
- 데이터베이스 파일 크기 축소
- 인덱스 재구축
- 성능 향상

**사용 예:**
```bash
# 데이터베이스 최적화
/compact

# 백업 후 최적화
/compact --backup-first
```

### `/logs [level]`
**용도:** 시스템 로그 확인
**사용 예:**
```bash
# 최근 로그 확인
/logs

# 에러 로그만 확인
/logs error

# 최근 100줄 로그
/logs --tail 100
```

### `/config <action> [key] [value]`
**용도:** 설정 관리
**사용 예:**
```bash
# 설정 조회
/config list

# 설정 변경
/config set api.rate_limit 10

# 설정 초기화
/config reset --all

# 거래소 API 설정
/config exchange add okx
```

### `/health-check`
**용도:** 시스템 건강 상태 점검
**기능:**
- API 연결 상태
- 데이터베이스 상태
- 봇 실행 상태
- 시스템 리소스 사용량

**사용 예:**
```bash
# 전체 상태 점검
/health-check

# API 연결만 점검
/health-check --api-only

# 상세 정보 포함
/health-check --detailed
```

## 고급 명령어 (Advanced Commands)

### `/debug <mode> [options]`
**용도:** 디버깅 모드 실행
**사용 예:**
```bash
# 봇 로직 디버깅
/debug trading-bot --verbose

# API 통신 디버깅
/debug api --log-requests

# 성능 프로파일링
/debug performance --profile-cpu
```

### `/export <format> <data>`
**용도:** 데이터 내보내기
**사용 예:**
```bash
# CSV로 거래 내역 내보내기
/export csv trades --exchange binance

# JSON으로 봇 설정 내보내기
/export json bot-configs

# Excel 리포트 생성
/export excel performance --month 2024-12
```

### `/import <format> <file>`
**용도:** 데이터 가져오기
**사용 예:**
```bash
# CSV 거래 내역 가져오기
/import csv historical_trades.csv

# JSON 봇 설정 가져오기
/import json backup_bot_configs.json

# 다른 거래소 데이터 가져오기
/import exchange-data other_platform_data.json
```

## 에이전트 호출 규칙 (Agent Calling Rules)

### TDD 에이전트와 슬래시 명령어 연동

```
명령어 실행 → 자동 에이전트 라우팅 → 에이전트 처리 → 결과 반환

예시:
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

### 에이전트별 전용 명령어

#### Developer Agent 전용:
```bash
# Developer Agent에 특정 작업 요청
/tdd-developer --task "거래 로직 단위 테스트 작성"
/tdd-developer --focus unit-tests
/tdd-developer --priority high
```

#### Reviewer Agent 전용:
```bash
# Reviewer Agent에 특정 리뷰 요청
/tdd-reviewer --scope security
/tdd-reviewer --file trading_bot.py
/tdd-reviewer --focus performance
```

#### Refactory Agent 전용:
```bash
# Refactory Agent에 특정 최적화 요청
/tdd-refactory --optimization performance
/tdd-refactory --code-style cleanup
/tdd-refactory --architecture improvement
```

## 사용자 정의 명령어 (Custom Commands)

프로젝트 특성에 맞춰 사용자 정의 명령어를 생성할 수 있습니다:

```bash
# 사용자 정의 명령어 설정
/custom-commands add my-custom-command --description "사용자 정의 명령어"

# 명령어 목록 조회
/custom-commands list

# 사용자 정의 명령어 실행
/my-custom-command
```

## 명령어 실행 예제 (Command Execution Examples)

### 완전한 TDD 개발 워크플로우 예시:

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

### 거래 운영 시나리오 예시:

```bash
# 1. 데이터 수집
/data-collect binance BTC/USDT 1m

# 2. 봇 실행
/bot-start binance configs/btc_martingale.json

# 3. 실시간 상태 모니터링
/bot-status --detailed
/positions binance

# 4. 성과 분석
/report performance --period today

# 5. 시스템 건강 상태 점검
/health-check
```

이 슬래시 명령어들을 활용하여 Gr8 DIY 프로젝트의 개발 및 운영 효율성을 크게 향상시킬 수 있습니다.