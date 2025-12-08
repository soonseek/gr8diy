# 기여 가이드

이 프로젝트에 기여해주셔서 감사합니다! 🎉

## 개발 환경 설정

1. **저장소 클론**
   ```bash
   git clone https://github.com/your-username/free-trader.git
   cd free-trader
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   # source env/bin/activate  # Linux/Mac
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **데이터베이스 초기화**
   - 앱을 처음 실행하면 자동으로 DB가 생성됩니다

## 코드 스타일

- **Python**: PEP 8 준수
- **Docstring**: Google 스타일
- **Import 순서**: 
  1. 표준 라이브러리
  2. 서드파티 라이브러리
  3. 로컬 모듈

### 예시
```python
"""
모듈 설명
"""
import sys
from typing import List, Dict

from PySide6.QtWidgets import QWidget
from qfluentwidgets import PushButton

from config.settings import WINDOW_TITLE
from utils.logger import logger


class MyWidget(QWidget):
    """위젯 설명"""
    
    def __init__(self):
        super().__init__()
        logger.info("MyWidget", "초기화 완료")
```

## 커밋 메시지 규칙

### 포맷
```
<타입>: <제목>

<본문 (선택)>

<푸터 (선택)>
```

### 타입
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

### 예시
```
feat: OKX WebSocket 실시간 가격 구독 추가

- 가격 업데이트 Signal 구현
- 자동 재연결 로직 추가
- UI에 실시간 가격 표시

Closes #123
```

## Pull Request 프로세스

1. **브랜치 생성**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **변경 사항 커밋**
   ```bash
   git add .
   git commit -m "feat: 기능 설명"
   ```

3. **원격 저장소에 푸시**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **PR 생성**
   - GitHub에서 Pull Request 생성
   - 변경 사항 설명 작성
   - 관련 이슈 번호 참조

## 버그 리포트

버그를 발견하셨나요? 다음 정보를 포함해 이슈를 생성해주세요:

- **환경**: Windows 버전, Python 버전
- **재현 방법**: 단계별 설명
- **예상 동작**: 어떻게 동작해야 하는지
- **실제 동작**: 실제로 어떻게 동작하는지
- **스크린샷**: 가능하다면 첨부
- **로그**: 관련 에러 로그

## 기능 제안

새로운 기능을 제안하고 싶으신가요?

1. 기존 이슈에서 중복 확인
2. "Feature Request" 템플릿으로 이슈 생성
3. 다음 내용 포함:
   - **문제/니즈**: 왜 이 기능이 필요한가?
   - **제안 솔루션**: 어떻게 구현하면 좋을까?
   - **대안**: 다른 방법은?
   - **영향**: 어떤 사용자에게 도움이 될까?

## 코드 리뷰 기준

PR이 다음 기준을 만족하는지 확인해주세요:

- [ ] 코드가 PEP 8을 준수하는가?
- [ ] 새로운 기능에 주석/docstring이 있는가?
- [ ] 기존 기능이 깨지지 않는가?
- [ ] 로그 메시지가 적절히 추가되었는가?
- [ ] UI 변경 시 스크린샷을 첨부했는가?

## 테스트

### 수동 테스트
현재는 수동 테스트를 권장합니다:

1. 앱 실행: `python app/main.py`
2. 각 메뉴 동작 확인
3. 에러 발생 시 로그 확인

### 자동 테스트 (추후)
```bash
pytest tests/
```

## 질문이 있으신가요?

- **Issue 탭**에 질문을 올려주세요
- **Discussions** 섹션을 활용해주세요

## 행동 강령

- 서로 존중하고 배려합시다
- 건설적인 피드백을 주고받읍시다
- 다양성을 환영합니다

---

**다시 한번 기여해주셔서 감사합니다! 🙏**


