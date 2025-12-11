"""
홈 페이지 - README 및 가이드 표시
"""
import sys
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QStackedWidget
from PySide6.QtCore import Qt
from qfluentwidgets import Pivot
from pathlib import Path
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


def get_resource_path(filename):
    """PyInstaller 환경에서 리소스 파일 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        base_path = sys._MEIPASS
    else:
        # 개발 환경
        base_path = Path(__file__).parent.parent
    return Path(base_path) / filename


class HomePage(QWidget):
    """홈 페이지 - README 탭별 표시"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 10, 10)
        
        # Pivot (탭) - 좌측 정렬
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        
        self.stack_widget = QStackedWidget(self)
        
        # 탭별 뷰어 생성
        self.intro_browser = self._create_text_browser()
        self.features_browser = self._create_text_browser()
        self.setup_browser = self._create_text_browser()
        self.diy_browser = self._create_text_browser()
        self.community_browser = self._create_text_browser()
        
        # 스택에 추가 (순서 변경: 설치 가이드가 DIY 가이드 앞으로)
        self.stack_widget.addWidget(self.intro_browser)        # 0
        self.stack_widget.addWidget(self.features_browser)     # 1
        self.stack_widget.addWidget(self.setup_browser)        # 2 (변경)
        self.stack_widget.addWidget(self.diy_browser)          # 3 (변경)
        self.stack_widget.addWidget(self.community_browser)    # 4
        
        # Pivot 아이템 추가
        self.pivot.addItem(
            routeKey="intro",
            text="프로젝트 소개",
            onClick=lambda: self.stack_widget.setCurrentIndex(0)
        )
        self.pivot.addItem(
            routeKey="features",
            text="주요 기능",
            onClick=lambda: self.stack_widget.setCurrentIndex(1)
        )
        self.pivot.addItem(
            routeKey="setup",
            text="DIY 환경 만들기",
            onClick=lambda: self.stack_widget.setCurrentIndex(2)
        )
        self.pivot.addItem(
            routeKey="diy",
            text="DIY 개발 가이드",
            onClick=lambda: self.stack_widget.setCurrentIndex(3)
        )
        self.pivot.addItem(
            routeKey="community",
            text="커뮤니티",
            onClick=lambda: self.stack_widget.setCurrentIndex(4)
        )
        
        # 콘텐츠 로드
        self._load_contents()
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack_widget)
        
        # 기본 탭 선택
        self.pivot.setCurrentItem("intro")
    
    def _create_text_browser(self):
        """텍스트 브라우저 생성"""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        
        # 스타일 적용 (행간 축소)
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0a0e27;
                color: #e8e8e8;
                border: none;
                padding: 20px;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        
        return browser
    
    def _load_contents(self):
        """모든 콘텐츠 로드"""
        readme_path = get_resource_path("README.md")
        setup_path = get_resource_path("README_SETUP_ko.md")
        
        # README 전체 내용 읽기
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            # 섹션별로 분할
            self._load_intro_section(readme_content)
            self._load_features_section(readme_content)
            self._load_diy_section(readme_content)
            self._load_community_section(readme_content)
        
        # 설치 가이드 읽기
        if setup_path.exists():
            with open(setup_path, 'r', encoding='utf-8') as f:
                setup_content = f.read()
            self._display_markdown(self.setup_browser, setup_content)
    
    def _load_intro_section(self, content):
        """프로젝트 소개 섹션"""
        # README에서 프로젝트 구조, 기술 스택, 주요 설계 원칙까지
        sections = content.split('# 🛠️ DIY 개발 가이드')[0]
        self._display_markdown(self.intro_browser, sections)
    
    def _load_features_section(self, content):
        """주요 기능 섹션"""
        if '## 주요 기능' in content:
            start = content.find('## 주요 기능')
            end = content.find('## 기술 스택')
            if end == -1:
                end = content.find('## 설치 및 실행')
            features = content[start:end] if end != -1 else content[start:]
            self._display_markdown(self.features_browser, features)
    
    def _load_diy_section(self, content):
        """DIY 가이드 섹션"""
        if '# 🛠️ DIY 개발 가이드' in content:
            start = content.find('# 🛠️ DIY 개발 가이드')
            end = content.find('## 💬 커뮤니티 & 기여')
            if end == -1:
                end = content.find('## 기여')
            diy = content[start:end] if end != -1 else content[start:]
            self._display_markdown(self.diy_browser, diy)
    
    def _load_community_section(self, content):
        """커뮤니티 섹션"""
        if '## 💬 커뮤니티 & 기여' in content:
            start = content.find('## 💬 커뮤니티 & 기여')
            community = content[start:]
            self._display_markdown(self.community_browser, community)
    
    def _display_markdown(self, browser, md_content):
        """Markdown을 HTML로 변환하여 표시"""
        try:
            if MARKDOWN_AVAILABLE:
                html_content = markdown.markdown(
                    md_content,
                    extensions=['extra', 'codehilite', 'toc', 'fenced_code']
                )
            else:
                # markdown 모듈이 없으면 기본 텍스트로
                html_content = f"<pre>{md_content}</pre>"
            
            # CSS 스타일 추가 (행간 축소)
            styled_html = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
                        line-height: 1.5;
                        color: #e8e8e8;
                        margin: 0;
                        padding: 0;
                    }}
                    h1 {{
                        color: #00ff9f;
                        border-bottom: 2px solid #00ff9f;
                        padding-bottom: 8px;
                        margin-top: 15px;
                        margin-bottom: 12px;
                        font-size: 24px;
                    }}
                    h2 {{
                        color: #00d4ff;
                        margin-top: 20px;
                        margin-bottom: 10px;
                        font-size: 20px;
                    }}
                    h3 {{
                        color: #00ffb3;
                        margin-top: 15px;
                        margin-bottom: 8px;
                        font-size: 17px;
                    }}
                    h4 {{
                        color: #a0e0ff;
                        margin-top: 12px;
                        margin-bottom: 6px;
                        font-size: 15px;
                    }}
                    p {{
                        margin: 8px 0;
                        line-height: 1.5;
                    }}
                    code {{
                        background-color: #1a1f3a;
                        color: #00ff9f;
                        padding: 2px 5px;
                        border-radius: 3px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 12px;
                    }}
                    pre {{
                        background-color: #1a1f3a;
                        border-left: 3px solid #00ff9f;
                        padding: 12px;
                        border-radius: 6px;
                        overflow-x: auto;
                        margin: 10px 0;
                        line-height: 1.4;
                    }}
                    pre code {{
                        background-color: transparent;
                        padding: 0;
                    }}
                    a {{
                        color: #00d4ff;
                        text-decoration: none;
                    }}
                    a:hover {{
                        color: #00ffb3;
                        text-decoration: underline;
                    }}
                    ul, ol {{
                        margin: 8px 0;
                        padding-left: 25px;
                    }}
                    li {{
                        margin: 5px 0;
                        line-height: 1.4;
                    }}
                    blockquote {{
                        border-left: 4px solid #00d4ff;
                        padding-left: 12px;
                        margin: 10px 0;
                        color: #a0a0a0;
                        font-style: italic;
                    }}
                    hr {{
                        border: none;
                        border-top: 1px solid #2a3050;
                        margin: 15px 0;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            browser.setHtml(styled_html)
        
        except Exception as e:
            browser.setHtml(f"""
                <h1 style='color: #ff4444;'>콘텐츠 로드 오류</h1>
                <p>{str(e)}</p>
            """)

