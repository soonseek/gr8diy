"""
메인 윈도우
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel, QSplitter, QApplication
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QScreen
from qfluentwidgets import (
    NavigationInterface, NavigationItemPosition, 
    FluentIcon, setTheme, Theme, isDarkTheme
)

from ui.home_page import HomePage
from ui.settings_page import SettingsPage
from ui.data_page import DataPage
from ui.bot_page import BotPage
from ui.log_widget import LogWidget
from ui.theme import apply_theme_to_widget, Gr8Theme
from config.settings import WINDOW_TITLE
from utils.logger import logger


class MainWindow(QMainWindow):
    """메인 윈도우"""
    
    def __init__(self):
        print("[DEBUG-MW] Step 1: MainWindow __init__ 시작")
        print("[DEBUG-MW] Step 2: super().__init__() 호출 전")
        super().__init__()
        print("[DEBUG-MW] Step 3: super().__init__() 완료")
        
        print("[DEBUG-MW] Step 4: setWindowTitle 호출")
        self.setWindowTitle(WINDOW_TITLE)
        
        # 커스텀 테마 적용
        print("[DEBUG-MW] Step 4.5: 커스텀 테마 적용")
        apply_theme_to_widget(self)
        
        # 화면 크기에 맞춤 (전체 화면 모드)
        print("[DEBUG-MW] Step 5: showMaximized 호출")
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen().availableGeometry()
            self.setGeometry(screen)
        self.showMaximized()
        
        # 중앙 위젯
        print("[DEBUG-MW] Step 6: QWidget() 생성 시작")
        central_widget = QWidget()
        print("[DEBUG-MW] Step 7: QWidget() 생성 완료")
        
        print("[DEBUG-MW] Step 8: setCentralWidget 호출")
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        print("[DEBUG-MW] Step 9: QHBoxLayout 생성")
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 콘텐츠 영역
        print("[DEBUG-MW] Step 12: QVBoxLayout 생성")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # 헤더 영역
        print("[DEBUG-MW] Step 13: _create_header 호출")
        header_widget = self._create_header()
        content_layout.addWidget(header_widget)
        
        # 스택 위젯 (페이지 전환용)
        print("[DEBUG-MW] Step 14: QStackedWidget 생성")
        self.stack_widget = QStackedWidget()
        content_layout.addWidget(self.stack_widget)
        
        # 콘텐츠 컨테이너
        print("[DEBUG-MW] Step 17: content_container QWidget 생성")
        content_container = QWidget()
        content_container.setLayout(content_layout)
        
        # 로그 위젯 (오른쪽 배치)
        print(f"[DEBUG-MW] Step 15: LogWidget 생성 시작 / QApplication.instance() = {QApplication.instance()}")
        try:
            self.log_widget = LogWidget()
            print("[DEBUG-MW] Step 16: LogWidget 생성 완료")
        except Exception as e:
            import traceback
            print("[DEBUG-MW-ERROR] LogWidget 생성 중 예외 발생:")
            traceback.print_exc()
            raise
        
        # 스플리터 생성 (콘텐츠 | 로그)
        print("[DEBUG-MW] Step 17.5: QSplitter 생성")
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(content_container)
        splitter.addWidget(self.log_widget)
        
        # 초기 비율: 콘텐츠 80%, 로그 20% (픽셀 단위로 명확히 설정)
        # 화면 너비를 1920으로 가정하면 1536:384
        splitter.setSizes([1536, 384])
        splitter.setStretchFactor(0, 8)
        splitter.setStretchFactor(1, 2)
        
        # 네비게이션 인터페이스
        print("[DEBUG-MW] Step 10: NavigationInterface 생성 시작")
        self.navigation = NavigationInterface(showReturnButton=False)
        print("[DEBUG-MW] Step 11: NavigationInterface 생성 완료")
        
        # 메인 레이아웃에 추가
        print("[DEBUG-MW] Step 18: 레이아웃에 위젯 추가")
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(splitter, stretch=1)
        
        # 페이지 초기화
        print("[DEBUG-MW] Step 19: _init_pages 호출")
        self._init_pages()
        
        # 네비게이션 아이템 추가
        print("[DEBUG-MW] Step 20: _init_navigation 호출")
        self._init_navigation()
        
        # 로그 시스템 연결
        print("[DEBUG-MW] Step 21: _connect_logger 호출")
        self._connect_logger()
        
        print("[DEBUG-MW] Step 22: MainWindow 초기화 완료")
        logger.info("UI", "메인 윈도우 초기화 완료")
    
    def _create_header(self):
        """헤더 위젯 생성"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # 브랜딩 로고 텍스트 (그라디언트 효과)
        logo_label = QLabel("Gr8 DIY")
        logo_font = QFont()
        logo_font.setPointSize(24)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        logo_label.setStyleSheet(f"""
            QLabel {{
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {Gr8Theme.NEON_GREEN}, 
                    stop:1 {Gr8Theme.NEON_BLUE});
                background: transparent;
                padding: 8px 16px;
                border-radius: 8px;
            }}
        """)
        
        # 서브타이틀
        subtitle_label = QLabel("유튜브 <소피아빠>와 구독자님들이 함께 만들어가는 자동매매봇 오픈소스 프로젝트")
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {Gr8Theme.TEXT_SECONDARY};
                font-size: 11px;
                font-style: italic;
                margin-left: 12px;
            }}
        """)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        
        # 헤더 스타일 (네온 언더라인)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {Gr8Theme.BG_SECONDARY};
                border-bottom: 2px solid transparent;
                border-image: linear-gradient(90deg, {Gr8Theme.NEON_GREEN} 0%, {Gr8Theme.NEON_BLUE} 100%);
            }}
        """)
        
        return header
    
    def _init_pages(self):
        """페이지 초기화"""
        # 홈 페이지
        print("[DEBUG-MW] Step 19-0: HomePage 생성 시작")
        self.home_page = HomePage()
        print("[DEBUG-MW] Step 19-0.5: HomePage 생성 완료")
        self.stack_widget.addWidget(self.home_page)
        
        # 설정 페이지
        print("[DEBUG-MW] Step 19-1: SettingsPage 생성 시작")
        self.settings_page = SettingsPage()
        print("[DEBUG-MW] Step 19-2: SettingsPage 생성 완료")
        self.stack_widget.addWidget(self.settings_page)
        
        # 데이터 페이지
        print("[DEBUG-MW] Step 19-3: DataPage 생성 시작")
        self.data_page = DataPage()
        print("[DEBUG-MW] Step 19-4: DataPage 생성 완료")
        self.stack_widget.addWidget(self.data_page)
        
        # 봇 페이지
        print("[DEBUG-MW] Step 19-5: BotPage 생성 시작")
        self.bot_page = BotPage()
        print("[DEBUG-MW] Step 19-6: BotPage 생성 완료")
        self.stack_widget.addWidget(self.bot_page)
    
    def _init_navigation(self):
        """네비게이션 아이템 추가"""
        # 홈 메뉴
        self.navigation.addItem(
            routeKey="home",
            icon=FluentIcon.HOME,
            text="홈",
            onClick=lambda: self.switch_page(0),
            position=NavigationItemPosition.TOP
        )
        
        # 설정 메뉴
        self.navigation.addItem(
            routeKey="settings",
            icon=FluentIcon.SETTING,
            text="설정",
            onClick=lambda: self.switch_page(1),
            position=NavigationItemPosition.TOP
        )
        
        # 데이터 메뉴
        self.navigation.addItem(
            routeKey="data",
            icon=FluentIcon.HISTORY,
            text="데이터",
            onClick=lambda: self.switch_page(2),
            position=NavigationItemPosition.TOP
        )
        
        # 봇 메뉴
        self.navigation.addItem(
            routeKey="bot",
            icon=FluentIcon.ROBOT,
            text="봇",
            onClick=lambda: self.switch_page(3),
            position=NavigationItemPosition.TOP
        )
        
        
        # 기본 선택 - 홈
        self.navigation.setCurrentItem("home")
    
    def switch_page(self, index: int):
        """페이지 전환"""
        self.stack_widget.setCurrentIndex(index)
    
    def toggle_theme(self):
        """테마 전환"""
        if isDarkTheme():
            setTheme(Theme.LIGHT)
            logger.info("UI", "라이트 테마로 전환")
        else:
            setTheme(Theme.DARK)
            logger.info("UI", "다크 테마로 전환")
    
    def _connect_logger(self):
        """로거와 UI 연결"""
        from utils.logger import logger
        logger.emitter.log_signal.connect(self.log_widget.add_log)
    
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        logger.info("UI", "애플리케이션 종료")
        event.accept()


