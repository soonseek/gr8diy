# TDD 워크플로우 가이드
# TDD Workflow Guide

## 개요 (Overview)

이 문서는 Gr8 DIY 프로젝트의 TDD(Test-Driven Development) 워크플로우를 상세히 설명합니다. 세 개의 전문화된 서브-에이전트 시스템과 슬래시 명령어를 통한 체계적인 개발 프로세스를 안내합니다.

This document provides detailed instructions for the TDD (Test-Driven Development) workflow in the Gr8 DIY project. It guides you through a systematic development process using three specialized sub-agent systems and slash commands.

## TDD 사이클 상세 설명 (Detailed TDD Cycle)

### 1. Red 단계: 실패하는 테스트 작성
### 1. Red Phase: Write Failing Tests

#### 목표 (Objective)
새로운 기능에 대한 **실패하는 테스트**를 먼저 작성하여 기능의 명세를 명확히 정의합니다.

Write **failing tests** for new features first to clearly define feature specifications.

#### 프로세스 (Process)
1. **기능 분석**: 구현할 기능의 요구사항과 명세 분석
2. **테스트 케이스 설계**: 정상 케이스, 예외 케이스, 엣지 케이스 정의
3. **테스트 작성**: 실패를 확인하는 테스트 코드 작성
4. **실행 확인**: 모든 테스트가 실패하는지 확인

**1. Feature Analysis**: Analyze requirements and specifications of the feature to implement
**2. Test Case Design**: Define normal, exception, and edge cases
**3. Test Writing**: Write test code that fails
**4. Execution Verification**: Confirm all tests fail

#### Developer Agent 역할 (Developer Agent Role)
```bash
# TDD 개발 시작 명령어
/tdd-start "새로운 거래소 API 연동 기능 구현"

# Developer Agent가 수행하는 작업:
# 1. 기능 명세 분석
# 2. 테스트 케이스 설계
# 3. 단위 테스트 작성
# 4. 통합 테스트 설계
# 5. API 모킹 설정
```

**TDD development start command**
```bash
/tdd-start "Implement new exchange API integration feature"
```

**Tasks performed by Developer Agent:**
**1. Feature specification analysis**
**2. Test case design**
**3. Unit test writing**
**4. Integration test design**
**5. API mocking setup**

#### 테스트 작성 예시 (Test Writing Example)

```python
# tests/test_exchange_api.py
import pytest
from unittest.mock import Mock, patch
from api.ccxt_client import CCXTClient

class TestExchangeAPIIntegration:
    """새로운 거래소 API 연동 테스트"""

    def test_connect_to_binance_success(self):
        """바이낸스 연동 성공 테스트"""
        # Arrange (준비)
        api_key = "test_key"
        secret = "test_secret"

        # Act (실행)
        client = CCXTClient("binance", api_key, secret)
        result = client.test_connection()

        # Assert (검증)
        assert result is True

    def test_connect_with_invalid_credentials(self):
        """잘못된 자격증명으로 연결 실패 테스트"""
        # Arrange
        api_key = "invalid_key"
        secret = "invalid_secret"

        # Act
        client = CCXTClient("binance", api_key, secret)
        result = client.test_connection()

        # Assert
        assert result is False

    @patch('api.ccxt_client.ccxt.binance')
    def test_api_rate_limit_handling(self, mock_binance):
        """API 레이트 리밋 처리 테스트"""
        # Arrange
        mock_exchange = Mock()
        mock_exchange.create_order.side_effect = ccxt.RateLimit("Rate limit exceeded")
        mock_binance.return_value = mock_exchange

        # Act & Assert
        client = CCXTClient("binance", "key", "secret")
        with pytest.raises(ccxt.RateLimit):
            client.create_market_order("BTC/USDT", "buy", 0.001)
```

### 2. Green 단계: 테스트 통과하는 최소 코드 작성
### 2. Green Phase: Write Minimal Code to Pass Tests

#### 목표 (Objective)
작성된 테스트를 **통과하는 최소한의 코드**를 구현합니다. 과도한 최적화나 추가 기능은 피합니다.

Implement **minimal code** that passes the written tests. Avoid excessive optimization or additional features.

#### 프로세스 (Process)
1. **최소 구현**: 테스트 통화에 필요한 최소한의 코드만 작성
2. **점진적 개발**: 하나의 테스트씩 통과시키며 진행
3. **리팩토링 금지**: 이 단계에서는 리팩토링을 하지 않음
4. **지속적 확인**: 각 코드 변경 후 테스트 실행

**1. Minimal Implementation**: Write only the minimum code needed to pass tests
**2. Progressive Development**: Progress by passing one test at a time
**3. No Refactoring**: Do not refactor in this phase
**4. Continuous Verification**: Run tests after each code change**

#### Developer Agent 역할 (Developer Agent Role)
```python
# api/ccxt_client.py - 최소 구현 예시
import ccxt
import asyncio

class CCXTClient:
    """CCXT 통합 클라이언트"""

    def __init__(self, exchange_id: str, api_key: str = None, secret: str = None):
        """클라이언트 초기화"""
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.secret = secret
        self.exchange = None
        self._initialize_exchange()

    def _initialize_exchange(self):
        """거래소 초기화 - 최소 구현"""
        try:
            if self.exchange_id == "binance":
                self.exchange = ccxt.binance({
                    'apiKey': self.api_key,
                    'secret': self.secret,
                    'sandbox': True  # 테스트넷 기본 설정
                })
            else:
                raise ValueError(f"지원하지 않는 거래소: {self.exchange_id}")
        except Exception as e:
            print(f"거래소 초기화 실패: {e}")
            self.exchange = None

    def test_connection(self) -> bool:
        """연결 테스트 - 최소 구현"""
        try:
            if self.exchange is None:
                return False

            # 기본 정보 조회로 연결 확인
            self.exchange.fetch_balance()
            return True
        except Exception:
            return False

    def create_market_order(self, symbol: str, side: str, amount: float):
        """시장가 주문 생성 - 최소 구현"""
        try:
            return self.exchange.create_market_order(symbol, side, amount)
        except ccxt.RateLimit as e:
            raise e  # 레이트 리밋은 그대로 전달
        except Exception as e:
            raise Exception(f"주문 생성 실패: {e}")
```

### 3. Refactor 단계: 코드 최적화 및 개선
### 3. Refactor Phase: Code Optimization and Improvement

#### 목표 (Objective)
**테스트가 통과된 상태를 유지**하면서 코드의 품질을 개선하고 최적화합니다.

Improve code quality and optimize **while maintaining passing test status**.

#### 프로세스 (Process)
1. **Reviewer Agent 검토**: 코드 리뷰 및 개선점 식별
2. **Refactory Agent 최적화**: 성능, 가독성, 유지보수성 개선
3. **테스트 재실행**: 모든 테스트가 여전히 통과하는지 확인
4. **문서화**: 코드와 테스트 문서화

**1. Reviewer Agent Review**: Code review and improvement point identification
**2. Refactory Agent Optimization**: Improve performance, readability, maintainability
**3. Test Re-execution**: Confirm all tests still pass
**4. Documentation**: Document code and tests**

#### Reviewer Agent 역할 (Reviewer Agent Role)
```bash
# 코드 리뷰 요청
/tdd-review api/ccxt_client.py

# Reviewer Agent 검토 항목:
# 1. 보안 취약점 분석
# 2. 암호화폐 거래 로직 검증
# 3. 성능 병목 식별
# 4. 테스트 커버리지 분석
# 5. 아키텍처 일관성 검사
```

**Code review request**
```bash
/tdd-review api/ccxt_client.py
```

**Reviewer Agent review items:**
**1. Security vulnerability analysis**
**2. Crypto trading logic verification**
**3. Performance bottleneck identification**
**4. Test coverage analysis**
**5. Architecture consistency check**

#### Refactory Agent 역할 (Refactory Agent Role)
```bash
# 코드 리팩토링 요청
/tdd-refactor performance

# Refactory Agent 개선 작업:
# 1. 성능 최적화
# 2. 코드 리팩토링
# 3. 중복 코드 제거
# 4. 설계 패턴 적용
# 5. 문서화 개선
```

**Code refactoring request**
```bash
/tdd-refactor performance
```

**Refactory Agent improvement tasks:**
**1. Performance optimization**
**2. Code refactoring**
**3. Duplicate code removal**
**4. Design pattern application**
**5. Documentation improvement**

#### 리팩토링 예시 (Refactoring Example)

```python
# api/ccxt_client.py - 리팩토링된 버전
import ccxt
import asyncio
from typing import Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ExchangeType(Enum):
    """지원하는 거래소 타입"""
    BINANCE = "binance"
    OKX = "okx"
    BITGET = "bitget"
    # 추가 거래소...

class CCXTClient:
    """
    CCXT 통합 클라이언트

    다중 거래소 연동을 위한 통합 인터페이스 제공
    API 레이트 리밋, 에러 핸들링, 보안 기능 포함
    """

    # 클래스 변수로 지원 거래소 정의
    SUPPORTED_EXCHANGES = {
        ExchangeType.BINANCE: ccxt.binance,
        ExchangeType.OKX: ccxt.okx,
        ExchangeType.BITGET: ccxt.bitget,
    }

    def __init__(self,
                 exchange_id: str,
                 api_key: Optional[str] = None,
                 secret: Optional[str] = None,
                 sandbox: bool = True):
        """
        클라이언트 초기화

        Args:
            exchange_id: 거래소 ID
            api_key: API 키
            secret: API 시크릿
            sandbox: 테스트넷 모드 여부
        """
        self.exchange_id = exchange_id.lower()
        self.api_key = api_key
        self.secret = secret
        self.sandbox = sandbox
        self.exchange: Optional[ccxt.Exchange] = None

        self._initialize_exchange()
        self._setup_rate_limiting()

    def _initialize_exchange(self) -> None:
        """거래소 초기화"""
        try:
            exchange_type = ExchangeType(self.exchange_id)
            exchange_class = self.SUPPORTED_EXCHANGES.get(exchange_type)

            if not exchange_class:
                raise ValueError(f"지원하지 않는 거래소: {self.exchange_id}")

            config = {
                'apiKey': self.api_key,
                'secret': self.secret,
                'sandbox': self.sandbox,
                'enableRateLimit': True,
            }

            self.exchange = exchange_class(config)
            logger.info(f"거래소 초기화 성공: {self.exchange_id}")

        except ValueError as e:
            logger.error(f"거래소 초기화 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"거래소 초기화 중 예외 발생: {e}")
            self.exchange = None

    def _setup_rate_limiting(self) -> None:
        """API 레이트 리밋 설정"""
        if self.exchange:
            # 거래소별 레이트 리밋 설정
            if self.exchange_id == "binance":
                self.exchange.rateLimit = 1200  # 밀리초
            elif self.exchange_id == "okx":
                self.exchange.rateLimit = 100

    async def test_connection_async(self) -> bool:
        """비동기 연결 테스트"""
        try:
            if not self.exchange:
                return False

            # balance 조회로 연결 확인
            await self.exchange.fetch_balance()
            logger.info(f"{self.exchange_id} 연결 성공")
            return True

        except ccxt.AuthenticationError:
            logger.error(f"{self.exchange_id} 인증 실패")
            return False
        except ccxt.NetworkError:
            logger.error(f"{self.exchange_id} 네트워크 오류")
            return False
        except Exception as e:
            logger.error(f"{self.exchange_id} 연결 테스트 실패: {e}")
            return False

    def test_connection(self) -> bool:
        """동기 연결 테스트"""
        try:
            return asyncio.run(self.test_connection_async())
        except Exception as e:
            logger.error(f"연결 테스트 중 예외 발생: {e}")
            return False

    async def create_market_order_async(self,
                                      symbol: str,
                                      side: str,
                                      amount: float) -> Dict[str, Any]:
        """
        비동기 시장가 주문 생성

        Args:
            symbol: 거래 심볼 (예: BTC/USDT)
            side: 매수/매도 (buy/sell)
            amount: 수량

        Returns:
            주문 결과 딕셔너리

        Raises:
            ccxt.RateLimit: API 레이트 리밋 초과
            ccxt.InsufficientFunds: 잔액 부족
            Exception: 기타 오류
        """
        try:
            if not self.exchange:
                raise Exception("거래소가 초기화되지 않았습니다")

            # 주문 파라미터 검증
            if side not in ['buy', 'sell']:
                raise ValueError(f"잘못된 주문 방향: {side}")

            if amount <= 0:
                raise ValueError(f"잘못된 주문 수량: {amount}")

            # 주문 생성
            order = await self.exchange.create_market_order(symbol, side, amount)

            logger.info(f"주문 생성 성공: {symbol} {side} {amount}")
            return order

        except ccxt.RateLimit as e:
            logger.warning(f"API 레이트 리밋 초과: {e}")
            raise
        except ccxt.InsufficientFunds as e:
            logger.error(f"잔액 부족: {e}")
            raise
        except Exception as e:
            logger.error(f"주문 생성 실패: {e}")
            raise

    def create_market_order(self, symbol: str, side: str, amount: float) -> Dict[str, Any]:
        """동기 시장가 주문 생성"""
        try:
            return asyncio.run(self.create_market_order_async(symbol, side, amount))
        except Exception as e:
            logger.error(f"주문 생성 중 예외 발생: {e}")
            raise
```

## 슬래시 명령어 기반 워크플로우 (Slash Command-Based Workflow)

### 완전한 TDD 개발 사이클 예시
### Complete TDD Development Cycle Example

```bash
# 1. 새 기능 TDD 개발 시작
/tdd-start "바이낸스 선물 지원 기능 구현"

# Developer Agent 활성화됨
# - 기능 분석 및 명세 정의
# - 실패 테스트 작성
# - 최소 구현 코드 작성
# - 단위 테스트 통과 확인

# 2. 개발 진행 상태 확인
/tdd-status

# 출력 예시:
# TDD 워크플로우 상태:
# - 현재 단계: GREEN
# - 활성 에이전트: Developer Agent
# - 테스트 통과률: 85%
# - 보류 중인 작업: 코드 리뷰 요청

# 3. 코드 리뷰 요청
/tdd-review

# Reviewer Agent 활성화됨
# - 코드 품질 검토
# - 보안 취약점 분석
# - 성능 병목 식별
# - 개선 제안서 작성

# 4. 테스트 커버리지 확인
/tdd-coverage

# 출력 예시:
# 테스트 커버리지 리포트:
# - 전체 커버리지: 92%
# - api/ccxt_client.py: 95%
# - tests/test_exchange_api.py: 100%
# - 커버리지 목표 달성

# 5. 성능 최적화
/tdd-refactor performance

# Refactory Agent 활성화됨
# - 코드 리팩토링
# - 성능 최적화
# - 중복 코드 제거
# - 문서화 개선

# 6. 최종 결과 확인
/tdd-status --detailed

# 출력 예시:
# TDD 개발 사이클 완료:
# - 상태: COMPLETED
# - 소요 시간: 2h 15m
# - 테스트 커버리지: 94%
# - 코드 품질 점수: A+
# - 성능 개선: 23% 향상
```

**1. New feature TDD development start**
```bash
/tdd-start "Implement Binance futures support feature"
```

**Developer Agent activated:**
- Feature analysis and specification definition
- Failing test writing
- Minimal implementation code writing
- Unit test passing confirmation

**2. Development progress check**
```bash
/tdd-status
```

**Example output:**
**TDD workflow status:**
**- Current phase: GREEN**
**- Active agent: Developer Agent**
**- Test pass rate: 85%**
**- Pending tasks: Code review request**

**3. Code review request**
```bash
/tdd-review
```

**Reviewer Agent activated:**
- Code quality review
- Security vulnerability analysis
- Performance bottleneck identification
- Improvement proposal writing

**4. Test coverage check**
```bash
/tdd-coverage
```

**Example output:**
**Test coverage report:**
**- Total coverage: 92%**
**- api/ccxt_client.py: 95%**
**- tests/test_exchange_api.py: 100%**
**- Coverage target achieved**

**5. Performance optimization**
```bash
/tdd-refactor performance
```

**Refactory Agent activated:**
- Code refactoring
- Performance optimization
- Duplicate code removal
- Documentation improvement

**6. Final result check**
```bash
/tdd-status --detailed
```

**Example output:**
**TDD development cycle completed:**
**- Status: COMPLETED**
**- Time taken: 2h 15m**
**- Test coverage: 94%**
**- Code quality score: A+**
**- Performance improvement: 23% enhancement**

## 에이전트별 전문 분야와 도구 (Agent-Specific Expertise and Tools)

### Developer Agent 도구 모음 (Developer Agent Tool Kit)

```python
# 테스트 작성 템플릿
class TestTemplate:
    """Developer Agent 테스트 작성 템플릿"""

    @staticmethod
    def create_api_test_template():
        """API 테스트 템플릿 생성"""
        return '''
import pytest
from unittest.mock import Mock, patch
import ccxt

class Test{FeatureName}:
    """{feature_description} 테스트"""

    def setup_method(self):
        """테스트 설정"""
        self.mock_exchange = Mock()
        self.test_data = {...}

    def test_success_case(self):
        """정상 동작 테스트"""
        # Arrange
        # Act
        # Assert

    def test_error_case(self):
        """에러 상황 테스트"""
        # Arrange
        # Act
        # Assert

    @patch('module.path')
    def test_integration(self, mock_path):
        """통합 테스트"""
        # Arrange
        # Act
        # Assert
'''

    @staticmethod
    def create_minimal_implementation_template():
        """최소 구현 템플릿 생성"""
        return '''
class {ClassName}:
    """{class_description}"""

    def __init__(self):
        """초기화 - 최소 구현"""
        pass

    def {method_name}(self):
        """메소드 - 최소 구현"""
        # 테스트 통과에 필요한 최소한의 로직만 구현
        return expected_result
'''
```

### Reviewer Agent 체크리스트 (Reviewer Agent Checklist)

```markdown
## 코드 리뷰 체크리스트 (Code Review Checklist)

### 보안 (Security)
- [ ] API 키와 시크릿이 안전하게 처리되는가?
- [ ] 입력값 검증이 충분한가?
- [ ] SQL 인젝션, XSS 등 보안 취약점이 없는가?
- [ ] 암호화가 필요한 데이터는 적절히 암호화되는가?

### 성능 (Performance)
- [ ] 불필요한 데이터베이스 쿼리가 없는가?
- [ ] 루프 내에서 비효율적인 연산이 없는가?
- [ ] 메모리 누수 가능성이 있는가?
- [ ] 비동기 처리가 적절히 사용되는가?

### 테스트 (Testing)
- [ ] 테스트 커버리지가 충분한가? (목표: 80% 이상)
- [ ] 엣지 케이스가 모두 테스트되는가?
- [ ] 통합 테스트가 포함되는가?
- [ ] 모킹이 적절하게 사용되는가?

### 코드 품질 (Code Quality)
- [ ] PEP 8 스타일 가이드를 따르는가?
- [ ] 함수와 클래스의 책임이 명확한가?
- [ ] 중복 코드가 없는가?
- [ ] 의미 있는 변수명과 함수명이 사용되는가?

### 아키텍처 (Architecture)
- [ ] SOLID 원칙이 지켜지는가?
- [ ] 모듈 간 결합도가 낮은가?
- [ ] 의존성 역전이 적절히 적용되는가?
- [ ] 확장 가능한 구조인가?
```

### Refactory Agent 최적화 기법 (Refactory Agent Optimization Techniques)

```python
class RefactoryTechniques:
    """Refactory Agent 최적화 기법 모음"""

    @staticmethod
    def extract_method():
        """메소드 추출 기법"""
        # Before: 긴 메소드
        def process_order(self, order_data):
            # 검증 로직 (20줄)
            # 데이터 변환 (15줄)
            # 데이터베이스 저장 (10줄)
            # 알림 전송 (8줄)
            pass

        # After: 메소드 분리
        def process_order(self, order_data):
            self._validate_order(order_data)
            transformed_data = self._transform_order_data(order_data)
            self._save_order(transformed_data)
            self._send_notification(transformed_data)

    @staticmethod
    def apply_strategy_pattern():
        """전략 패턴 적용"""
        class TradingStrategy:
            def execute(self, data):
                raise NotImplementedError

        class MartingaleStrategy(TradingStrategy):
            def execute(self, data):
                # 마틴게일 로직
                pass

        class GridStrategy(TradingStrategy):
            def execute(self, data):
                # 그리드 로직
                pass

    @staticmethod
    def optimize_database_queries():
        """데이터베이스 쿼리 최적화"""
        # Before: N+1 문제
        for order in orders:
            user = db.get_user(order.user_id)  # N번 쿼리

        # After: 조인 사용
        orders_with_users = db.get_orders_with_users()  # 1번 쿼리
```

## 품질 보증 절차 (Quality Assurance Process)

### 자동화된 품질 검사 (Automated Quality Checks)

```yaml
# .github/workflows/tdd-quality-check.yml
name: TDD Quality Check

on: [push, pull_request]

jobs:
  tdd-quality-check:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black mypy

    - name: Run tests with coverage
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html

    - name: Check code style (Black)
      run: black --check .

    - name: Lint with flake8
      run: flake8 --max-line-length=88 .

    - name: Type checking with mypy
      run: mypy .

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

### 코드 품질 게이트 (Code Quality Gates)

```python
# scripts/quality_gate.py
"""
코드 품질 게이트 시스템
아래 기준을 모두 충족해야 메인 브랜치에 머지 가능
"""

QUALITY_REQUIREMENTS = {
    "test_coverage": 80,  # 최소 80% 커버리지
    "code_smells": 5,     # 최대 5개 코드 스멜
    "security_issues": 0,  # 보안 이슈 0개
    "duplicated_lines": 3, # 최대 3% 중복 코드
    "maintainability": "A", # 유지보수성 등급 A
}

def run_quality_gate():
    """품질 게이트 실행"""
    results = {
        "test_coverage": get_test_coverage(),
        "code_smells": count_code_smells(),
        "security_issues": count_security_issues(),
        "duplicated_lines": get_duplication_percentage(),
        "maintainability": get_maintainability_grade(),
    }

    for metric, requirement in QUALITY_REQUIREMENTS.items():
        current_value = results[metric]

        if isinstance(requirement, (int, float)):
            if metric == "test_coverage":
                if current_value < requirement:
                    return False, f"테스트 커버리지 부족: {current_value}% < {requirement}%"
            else:
                if current_value > requirement:
                    return False, f"{metric} 초과: {current_value} > {requirement}"
        else:
            if current_value != requirement:
                return False, f"{metric} 불일치: {current_value} != {requirement}"

    return True, "모든 품질 요구사항 충족"
```

## 성과 측정 및 모니터링 (Performance Measurement and Monitoring)

### TDD 워크플로우 메트릭스 (TDD Workflow Metrics)

```python
class TDDMetrics:
    """TDD 워크플로우 성과 측정"""

    def calculate_development_velocity(self):
        """개발 속도 계산 (스토리 포인트/스프린트)"""
        completed_stories = get_completed_story_points()
        sprint_duration = get_sprint_duration()
        return completed_stories / sprint_duration

    def calculate_test_coverage_trend(self):
        """테스트 커버리지 추세 분석"""
        coverage_history = get_historical_coverage()
        return {
            "current": coverage_history[-1],
            "trend": calculate_trend(coverage_history),
            "improvement": coverage_history[-1] - coverage_history[0]
        }

    def calculate_bug_density(self):
        """버그 밀도 계산 (버그 수/1000 LOC)"""
        bug_count = get_bug_count()
        loc = get_lines_of_code()
        return (bug_count / loc) * 1000

    def calculate_code_quality_score(self):
        """종합 코드 품질 점수"""
        metrics = {
            "coverage": self.get_coverage_score(),
            "complexity": self.get_complexity_score(),
            "duplication": self.get_duplication_score(),
            "security": self.get_security_score(),
        }
        return sum(metrics.values()) / len(metrics)
```

### 대시보드 보고 (Dashboard Reporting)

```python
# scripts/tdd_dashboard.py
"""
TDD 워크플로우 대시보드
실시간 성과 모니터링 및 리포팅
"""

def generate_tdd_dashboard():
    """TDD 대시보드 생성"""

    dashboard_data = {
        "overview": {
            "active_agents": get_active_agent_count(),
            "ongoing_cycles": get_ongoing_tdd_cycles(),
            "completed_today": get_completed_cycles_today(),
        },
        "quality_metrics": {
            "test_coverage": get_average_test_coverage(),
            "code_quality": get_average_quality_score(),
            "bug_density": get_current_bug_density(),
        },
        "agent_performance": {
            "developer_agent": get_developer_agent_metrics(),
            "reviewer_agent": get_reviewer_agent_metrics(),
            "refactory_agent": get_refactory_agent_metrics(),
        },
        "trends": {
            "coverage_trend": get_coverage_trend(),
            "velocity_trend": get_velocity_trend(),
            "quality_trend": get_quality_trend(),
        }
    }

    # 대시보드 HTML 생성
    html_dashboard = render_dashboard_html(dashboard_data)
    save_dashboard(html_dashboard, "tdd_dashboard.html")

    return dashboard_data
```

이 TDD 워크플로우 가이드를 통해 Gr8 DIY 프로젝트의 품질과 생산성을 체계적으로 관리할 수 있습니다. 세 개의 전문화된 에이전트가 협력하여 높은 품질의 코드를 생산하고, 지속적인 개선을 통해 프로젝트의 성공을 보장합니다.

This TDD workflow guide enables systematic management of quality and productivity in the Gr8 DIY project. Three specialized agents collaborate to produce high-quality code and ensure project success through continuous improvement.