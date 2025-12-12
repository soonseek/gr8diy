"""
홈페이지 - 탭별 콘텐츠 분리
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QStackedWidget
from PySide6.QtCore import Qt
from qfluentwidgets import Pivot, FluentIcon
from pathlib import Path
import markdown


class HomePage(QWidget):
    """홈페이지"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Pivot 탭
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        layout.addLayout(pivot_layout)
        
        # 스택 위젯
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # 탭 콘텐츠
        self.intro_browser = self._create_browser()
        self.features_browser = self._create_browser()
        self.setup_browser = self._create_browser()
        self.guide_browser = self._create_browser()
        self.community_browser = self._create_browser()
        self.updates_browser = self._create_browser()
        
        self.stack.addWidget(self.intro_browser)
        self.stack.addWidget(self.features_browser)
        self.stack.addWidget(self.setup_browser)
        self.stack.addWidget(self.guide_browser)
        self.stack.addWidget(self.community_browser)
        self.stack.addWidget(self.updates_browser)
        
        self.pivot.addItem("intro", "프로젝트 소개", lambda: self.stack.setCurrentIndex(0), icon=FluentIcon.INFO)
        self.pivot.addItem("features", "주요 기능", lambda: self.stack.setCurrentIndex(1), icon=FluentIcon.ALBUM)
        self.pivot.addItem("setup", "설치 및 실행", lambda: self.stack.setCurrentIndex(2), icon=FluentIcon.DEVELOPER_TOOLS)
        self.pivot.addItem("guide", "개발 가이드", lambda: self.stack.setCurrentIndex(3), icon=FluentIcon.DOCUMENT)
        self.pivot.addItem("community", "커뮤니티", lambda: self.stack.setCurrentIndex(4), icon=FluentIcon.PEOPLE)
        self.pivot.addItem("updates", "업데이트 기록", lambda: self.stack.setCurrentIndex(5), icon=FluentIcon.UPDATE)
        
        self.pivot.setCurrentItem("intro")
        
        self._load_content()
    
    def _create_browser(self) -> QTextBrowser:
        """텍스트 브라우저 생성"""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                border: none;
                padding: 10px;
                font-size: 13px;
            }
        """)
        return browser
    
    def _load_content(self):
        """콘텐츠 로드"""
        # 프로젝트 소개
        self.intro_browser.setHtml(self._style_html("""
# Gr8 DIY

**PySide6 + QFluentWidgets 기반의 멀티 거래소 암호화폐 자동매매 데스크탑 애플리케이션**

## 주요 특징

### 🌐 멀티 거래소 지원
- CCXT 라이브러리 기반 - CoinGecko Top 100 거래소
- Binance, Bybit, OKX, Bitget, Gate.io, KuCoin, HTX, Kraken 등
- 거래소별 독립적인 API 키 관리

### 📊 데이터 수집
- 과거 데이터 백필 (최대 200일)
- 실시간 데이터 최신화 (10초 폴링)
- 6개 타임프레임 (1m, 5m, 15m, 1h, 4h, 1d)

### 🤖 자동매매 봇
- 마틴게일 DCA 전략
- 레버리지 조절 (1~100배)
- 익절/손절 자동화
- 실시간 모니터링

### 기술 스택
- UI: PySide6, QFluentWidgets
- 거래소: CCXT
- DB: SQLite
- AI: OpenAI GPT
        """))
        
        # 주요 기능
        self.features_browser.setHtml(self._style_html("""
# 주요 기능

## ⚙️ 설정
### 거래소 연동
- 38개+ 거래소 API 키 관리
- 메인넷/테스트넷 모드
- 연동 테스트 및 상태 확인
- Hedge Mode 자동 설정

### GPT 연동
- OpenAI API 키 관리
- AI 분석 기능 (선택 사항)

## 📊 데이터
### 수집
- 거래소별 데이터 수집
- 과거 데이터 백필
- 실시간 최신화 (10초 폴링)
- 활성 심볼 관리

### 조회
- 거래소별 데이터 조회
- 심볼/타임프레임별 데이터 확인
- 수집 상태 모니터링

## 🤖 봇
### 봇 생성
- 거래소 선택 (연동된 거래소만)
- 심볼별 방향 설정 (LONG/SHORT)
- 증거금 및 레버리지 설정
- 마틴게일 단계/오프셋 설정
- 익절/손절 설정

### 모니터링
- 실시간 포지션 현황
- 손익(PnL) 추적
- 개별/전체 청산

### 내역
- 거래 통계 (승률, 순익 등)
- 거래 내역 조회

## 📈 백테스트 (개발 중)
- 과거 데이터 기반 시뮬레이션
- 성과 지표 분석
- 결과 내보내기
        """))
        
        # 설치 및 실행
        self.setup_browser.setHtml(self._style_html("""
# 설치 및 실행

## 시스템 요구사항
- Windows 10/11
- Python 3.10 이상
- 8GB RAM 이상 권장

## 설치 방법

### 1. Python 설치
- [python.org](https://www.python.org/downloads/) 에서 다운로드
- 설치 시 "Add to PATH" 체크

### 2. 가상환경 생성
```bash
python -m venv env
```

### 3. 의존성 설치
```bash
.\\env\\Scripts\\pip.exe install -r requirements.txt
```

### 4. 실행
```bash
.\\env\\Scripts\\python.exe .\\app\\main.py
```

## 초기 설정

### 1. 거래소 API 연동
1. 설정 → 거래소 연동
2. 거래소 선택
3. API Key, Secret (일부는 Passphrase) 입력
4. 테스트 버튼으로 연동 확인
5. 저장

### 2. 데이터 수집
1. 데이터 → 수집
2. 거래소 선택
3. 수집 기간 설정
4. 활성 심볼 선택
5. 수집 시작

### 3. 봇 실행
1. 봇 → 봇 생성
2. 거래소 선택 (연동된 거래소만)
3. 심볼 체크박스 선택
4. 방향/증거금/레버리지 설정
5. 마틴게일 설정
6. 익절/손절 설정
7. 🚀 봇 실행
        """))
        
        # 개발 가이드
        self.guide_browser.setHtml(self._style_html("""
# 개발 가이드

## 프로젝트 구조
```
free-trader/
├── app/           # 메인 진입점
├── ui/            # UI 컴포넌트
├── api/           # 거래소 API
├── workers/       # 백그라운드 작업
├── database/      # DB 스키마 및 레포지토리
├── config/        # 설정
├── backtest/      # 백테스트 엔진
└── utils/         # 유틸리티
```

## 주요 클래스

### API
- `CCXTClient`: CCXT 통합 클라이언트
- `ExchangeFactory`: 거래소 클라이언트 팩토리

### Workers
- `DataCollectorWorker`: 데이터 수집
- `TradingBotWorker`: 봇 실행
- `BacktestWorker`: 백테스트 실행

### UI
- `MainWindow`: 메인 윈도우
- `SettingsPage`: 설정
- `DataPage`: 데이터
- `BotPage`: 봇
- `BacktestPage`: 백테스트

## 새 거래소 추가
1. `config/exchanges.py`에 메타데이터 추가
2. CCXT가 지원하면 자동 작동

## 테마 커스터마이징
`ui/theme.py`의 `Gr8Theme` 클래스 수정:
```python
NEON_GREEN = "#00ff9f"  # 원하는 색상
NEON_BLUE = "#00d4ff"
```
        """))
        
        # 커뮤니티
        self.community_browser.setHtml(self._style_html("""
# 커뮤니티

## 📺 YouTube
**채널: 소피아빠**
- 자동매매 봇 개발 강좌
- DIY 프로젝트 진행 과정
- 실시간 코딩 세션

## 💬 Discord
**[Gr8 DIY Discord 참여하기](https://discord.gg/KBvavs9F47)**
- 실시간 소통
- Q&A
- 버그 리포트
- 기능 제안

## 🐙 GitHub
**[Gr8 DIY GitHub 레포지토리](https://github.com/soonseek/gr8diy)**
- 소스 코드
- 이슈 트래킹
- Pull Request

## 기여 방법
- 🐛 버그 발견: Discord 또는 GitHub Issue
- 💡 기능 제안: Discord에서 논의
- 🔧 코드 기여: Pull Request 환영
- 📖 문서 개선: README 수정 제안

---

**Made with ❤️ by 유튜브 <소피아빠>와 구독자님들**
        """))
        
        # 업데이트 기록
        updates_path = Path(__file__).parent.parent / "UPDATES.md"
        if updates_path.exists():
            try:
                with open(updates_path, 'r', encoding='utf-8') as f:
                    updates_content = f.read()
                self.updates_browser.setHtml(self._style_html(updates_content))
            except:
                self.updates_browser.setHtml(self._style_html("# 업데이트 기록\n\n로드 실패"))
        else:
            self.updates_browser.setHtml(self._style_html("# 업데이트 기록\n\nUPDATES.md 파일을 찾을 수 없습니다."))
    
    def _style_html(self, content: str) -> str:
        """마크다운을 스타일된 HTML로 변환"""
        try:
            html = markdown.markdown(
                content, 
                extensions=['fenced_code', 'tables', 'toc']
            )
        except:
            html = f"<pre>{content}</pre>"
        
        return f"""
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                color: #e0e0e0; 
                line-height: 1.6;
            }}
            h1 {{ color: #00ff9f; font-size: 24px; margin: 20px 0 12px 0; border-bottom: 2px solid #00ff9f; padding-bottom: 8px; }}
            h2 {{ color: #00d4aa; font-size: 18px; margin: 16px 0 10px 0; }}
            h3 {{ color: #00d4aa; font-size: 15px; margin: 12px 0 8px 0; }}
            p {{ margin: 8px 0; }}
            ul, ol {{ margin: 10px 0; padding-left: 30px; }}
            li {{ margin: 5px 0; line-height: 1.5; }}
            code {{ 
                background: #1a1a2e; 
                padding: 3px 6px; 
                border-radius: 3px; 
                font-size: 12px; 
                color: #00ff9f;
                font-family: 'Consolas', 'Monaco', monospace;
            }}
            pre {{ 
                background: #1a1a2e; 
                padding: 15px; 
                border-radius: 6px; 
                overflow-x: auto; 
                border: 1px solid #4a5080;
                margin: 12px 0;
            }}
            pre code {{
                background: transparent;
                padding: 0;
                color: #e0e0e0;
            }}
            a {{ color: #00d4ff; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            table {{ border-collapse: collapse; margin: 12px 0; width: 100%; }}
            th, td {{ border: 1px solid #4a5080; padding: 8px 12px; text-align: left; }}
            th {{ background: #1a1a2e; color: #00ff9f; font-weight: bold; }}
            blockquote {{
                border-left: 4px solid #00ff9f;
                margin: 12px 0;
                padding: 8px 15px;
                background: rgba(0, 255, 159, 0.05);
            }}
            hr {{ border: none; border-top: 1px solid #4a5080; margin: 20px 0; }}
        </style>
        {html}
        """
