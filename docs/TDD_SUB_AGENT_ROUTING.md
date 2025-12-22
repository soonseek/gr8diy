# TDD 서브-에이전트 라우팅 규칙 및 프로토콜
# TDD Sub-Agent Routing Rules and Protocols

## 개요 (Overview)
Gr8 DIY 암호화폐 자동매매 프로젝트를 위한 TDD(Test-Driven Development) 방법론 구현을 위한 서브-에이전트 시스템의 라우팅 규칙과 프로토콜을 정의합니다.

## 서브-에이전트 아키텍처 (Sub-Agent Architecture)

### 1. Developer Agent (개발자 에이전트)
**역할 (Role):** 테스트 우선 개발 및 최소한의 구현

**전문 분야 (Expertise):**
- 단위 테스트(Unit Test) 작성
- 통합 테스트(Integration Test) 설계
- 거래소 API 모킹(Mocking)
- 데이터베이스 테스트 환경 구축
- UI 컴포넌트 테스트

**주요 책임 (Key Responsibilities):**
- Red 단계: 실패하는 테스트 작성
- Green 단계: 테스트를 통과하는 최소한의 코드 구현
- 기본 기능 검증 및 단위 테스트 커버리지 확보
- Mock 데이터 및 테스트 픽스처 생성

### 2. Reviewer Agent (리뷰어 에이전트)
**역할 (Role):** 코드 및 테스트 품질 검증

**전문 분야 (Expertise):**
- 암호화폐 거래 로직 검증
- 보안 취약점 분석
- 성능 병목 식별
- 테스트 커버리지 분석
- 코드 품질 및 아키텍처 준수 검사

**주요 책임 (Key Responsibilities):**
- 코드 리뷰 및 품질 평가
- 누락된 테스트 케이 식별
- 에지 케이(Edge Case) 검증
- 보안 및 성능 분석
- 아키텍처 일관성 검사

### 3. Refactory Agent (리팩토리 에이전트)
**역할 (Role):** 코드 최적화 및 개선

**전문 분야 (Expertise):**
- 성능 최적화
- 코드 리팩토링
- 테스트 스위트 개선
- 기술 부채 해소
- 유지보수성 향상

**주요 책임 (Key Responsibilities):**
- 코드 리팩토링 및 최적화
- 테스트 성능 개선
- 중복 코드 제거
- 설계 패턴 적용
- 문서화 개선

## 라우팅 규칙 (Routing Rules)

### 자동 라우팅 조건 (Automatic Routing Conditions)

#### Developer Agent 활성화:
```
if new_feature_request or bug_fix or missing_test_coverage:
    route_to("DeveloperAgent")

if existing_code_without_tests or new_component_implementation:
    route_to("DeveloperAgent")
```

#### Reviewer Agent 활성화:
```
if developer_agent_completed:
    route_to("ReviewerAgent")

if pull_request_created or code_quality_check_needed:
    route_to("ReviewerAgent")

if test_coverage_below_threshold or critical_logic_changed:
    route_to("ReviewerAgent")
```

#### Refactory Agent 활성화:
```
if reviewer_agent_approved and optimization_needed:
    route_to("RefactoryAgent")

if performance_issues_detected or technical_debt_accumulated:
    route_to("RefactoryAgent")

if code_quality_metrics_below_target:
    route_to("RefactoryAgent")
```

### 우선순위 기반 라우팅 (Priority-Based Routing)

#### 높음 (High Priority):
1. **보안 관련 변경**: 보안 취약점 수정, API 키 처리
2. **거래 로직 변경**: 수익/손실 로직, 포지션 관리
3. **데이터 무결성**: 데이터베이스 스키마 변경, 데이터 검증
4. **금융 계산**: 이익 계산, 수수료 처리

#### 중간 (Medium Priority):
1. **UI/UX 개선**: 사용자 인터페이스 변경, 사용자 경험
2. **API 연동**: 새로운 거래소 추가, API 변경
3. **성능 최적화**: 응답 속도 개선, 메모리 사용량
4. **테스트 인프라**: 테스트 프레임워크 개선

#### 낮음 (Low Priority):
1. **문서화**: 주석 추가, README 업데이트
2. **코드 스타일**: 포맷팅, 명명 규칙
3. **리팩토링**: 코드 구조 개선, 변수명 변경

## 프로토콜 (Protocols)

### 1. 에이전트 간 통신 (Inter-Agent Communication)

```python
class AgentMessage:
    def __init__(self, sender: str, recipient: str, message_type: str, data: dict):
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.data = data
        self.timestamp = datetime.now()
        self.priority = self._determine_priority()

    def _determine_priority(self) -> int:
        """메시지 우선순위 결정"""
        priority_map = {
            "SECURITY_ALERT": 1,
            "TRADING_CRITICAL": 1,
            "PERFORMANCE_CRITICAL": 2,
            "CODE_REVIEW": 3,
            "REFACTORING": 4,
            "GENERAL_INFO": 5
        }
        return priority_map.get(self.message_type, 5)
```

### 2. 상태 관리 (State Management)

```python
class TDDWorkflowState:
    def __init__(self):
        self.current_phase = "IDLE"
        self.active_agent = None
        self.task_stack = []
        self.results = {}
        self.errors = []
        self.progress = 0.0

    def transition_to_phase(self, phase: str, agent: str, task_data: dict):
        """TDD 워크플로우 상태 전환"""
        valid_transitions = {
            "IDLE": ["RED", "REVIEW"],
            "RED": ["GREEN", "ERROR"],
            "GREEN": ["REVIEW"],
            "REVIEW": ["REFACTOR", "ERROR"],
            "REFACTOR": ["COMPLETE", "ERROR"],
            "ERROR": ["RED", "COMPLETE"]
        }

        if phase in valid_transitions.get(self.current_phase, []):
            self.current_phase = phase
            self.active_agent = agent
            self.task_stack.append((phase, agent, task_data))
            return True
        return False
```

### 3. 에러 처리 및 복구 (Error Handling & Recovery)

```python
class ErrorHandler:
    def __init__(self):
        self.retry_strategies = {
            "API_FAILURE": self._retry_with_backoff,
            "DATABASE_ERROR": self._database_recovery,
            "TEST_FAILURE": self._test_recovery,
            "NETWORK_ERROR": self._network_recovery
        }

    def handle_error(self, error: Exception, agent: str, context: dict) -> dict:
        """에러 처리 및 복구 전략"""
        error_type = self._classify_error(error)

        recovery_strategy = self.retry_strategies.get(error_type)
        if recovery_strategy:
            return recovery_strategy(error, agent, context)

        return self._default_error_recovery(error, agent, context)
```

## 워크플로우 제어 (Workflow Control)

### TDD 사이클 관리 (TDD Cycle Management)

```python
class TDDCycleManager:
    def __init__(self):
        self.developer = DeveloperAgent()
        self.reviewer = ReviewerAgent()
        self.refactory = RefactoryAgent()
        self.current_task = None

    def execute_tdd_cycle(self, feature_spec: dict) -> dict:
        """완전한 TDD 사이클 실행"""
        results = {
            "feature_spec": feature_spec,
            "development": {},
            "review": {},
            "refactoring": {},
            "final_result": None
        }

        # 1. 개발 단계 (Red-Green)
        results["development"] = self.developer.implement_feature(feature_spec)

        if not results["development"]["success"]:
            return {"status": "FAILED", "results": results}

        # 2. 리뷰 단계
        results["review"] = self.reviewer.review_code(
            results["development"]["code"],
            results["development"]["tests"]
        )

        if results["review"]["approval_required"]:
            return {"status": "PENDING_REVIEW", "results": results}

        # 3. 리팩토리 단계
        results["refactoring"] = self.refactory.optimize_code(
            results["development"]["code"],
            results["review"]["suggestions"]
        )

        results["final_result"] = "SUCCESS"
        return {"status": "COMPLETED", "results": results}
```

## 명령어 인터페이스 (Command Interface)

### 슬래시 명령어 (Slash Commands)

#### `/tdd-start <feature>`
```bash
# 새로운 기능에 대한 TDD 사이클 시작
/tdd-start add-binance-futures-support

# 자동 에이전트 라우팅 시작
# 1. Developer Agent: 테스트 작성 및 구현
# 2. Reviewer Agent: 코드 리뷰
# 3. Refactory Agent: 최적화
```

#### `/tdd-review <file_path>`
```bash
# 특정 파일에 대한 코드 리뷰 요청
/tdd-review ui/trading_bot.py

# 현재 브랜치의 모든 변경사항 리뷰
/tdd-review
```

#### `/tdd-refactor <scope>`
```bash
# 전체 코드베이스 리팩토링
/tdd-refactor all

# 특정 모듈 리팩토링
/tdd-refactor api/

# 성능 최적화 리팩토링
/tdd-refactor performance
```

#### `/tdd-status`
```bash
# 현재 TDD 워크플로우 상태 확인
/tdd-status

# 특정 에이전트 상태 확인
/tdd-status developer
```

#### `/tdd-coverage`
```bash
# 테스트 커버리지 보고 생성
/tdd-coverage

# 특정 모듈 커버리지 확인
/tdd-coverage trading-bot
```

## 모니터링 및 로깅 (Monitoring & Logging)

### TDD 진행 상태 모니터링

```python
class TDDMonitor:
    def __init__(self):
        self.metrics = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "average_cycle_time": 0.0,
            "test_coverage": 0.0,
            "agent_performance": {}
        }

    def log_cycle_start(self, feature: str, agent: str):
        """TDD 사이클 시작 로깅"""
        logger.info("TDD_MONITOR",
                   f"Starting TDD cycle for '{feature}' with {agent}")

    def log_cycle_completion(self, results: dict):
        """TDD 사이클 완료 로깅"""
        status = results.get("status", "UNKNOWN")
        duration = results.get("duration", 0)

        logger.info("TDD_MONITOR",
                   f"TDD cycle completed: {status} in {duration:.2f}s")

        self.metrics["total_cycles"] += 1
        if status == "COMPLETED":
            self.metrics["successful_cycles"] += 1
        else:
            self.metrics["failed_cycles"] += 1
```

이 라우팅 규칙과 프로토콜을 통해 Gr8 DIY 프로젝트에서 일관된 TDD 방법론을 구현하고, 고품질 암호화폐 거래 시스템의 안정성과 유지보수성을 보장할 수 있습니다.