"""
메인 윈도우
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from qfluentwidgets import (
    NavigationInterface, NavigationItemPosition, 
    FluentIcon, setTheme, Theme, isDarkTheme
)

from ui.settings_page import SettingsPage
from ui.data_page import DataPage
from ui.bot_page import BotPage
from ui.log_widget import LogWidget
from config.settings import WINDOW_TITLE
from utils.logger import logger


class MainWindow(QMainWindow):
    """메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        
        # 화면 크기에 맞춤 (최대화)
        self.showMaximized()
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 네비게이션 인터페이스 (parent를 명시적으로 설정하지 않음)
        self.navigation = NavigationInterface(parent=central_widget, showReturnButton=False)
        
        # 콘텐츠 영역
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # 헤더 영역
        header_widget = self._create_header()
        content_layout.addWidget(header_widget)
        
        # 스택 위젯 (페이지 전환용)
        self.stack_widget = QStackedWidget()
        content_layout.addWidget(self.stack_widget, stretch=3)
        
        # 하단 로그 위젯
        self.log_widget = LogWidget()
        content_layout.addWidget(self.log_widget, stretch=1)
        
        # 콘텐츠 컨테이너
        content_container = QWidget()
        content_container.setLayout(content_layout)
        
        # 메인 레이아웃에 추가
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(content_container, stretch=1)
        
        # 페이지 초기화
        self._init_pages()
        
        # 네비게이션 아이템 추가
        self._init_navigation()
        
        # 로그 시스템 연결
        self._connect_logger()
        
        logger.info("UI", "메인 윈도우 초기화 완료")
    
    def _create_header(self):
        """헤더 위젯 생성"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # 브랜딩 로고 텍스트
        logo_label = QLabel("프리트레이더 DIY 패키지")
        logo_font = QFont()
        logo_font.setPointSize(16)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        logo_label.setStyleSheet("color: #0078D4;")  # 브랜드 컬러
        
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        
        # 헤더에 구분선 스타일 추가
        header.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-bottom: 2px solid #E0E0E0;
            }
        """)
        
        return header
    
    def _init_pages(self):
        """페이지 초기화"""
        # 설정 페이지
        self.settings_page = SettingsPage()
        self.stack_widget.addWidget(self.settings_page)
        
        # 데이터 페이지
        self.data_page = DataPage()
        self.stack_widget.addWidget(self.data_page)
        
        # 봇 페이지
        self.bot_page = BotPage()
        self.stack_widget.addWidget(self.bot_page)
    
    def _init_navigation(self):
        """네비게이션 아이템 추가"""
        # 설정 메뉴
        self.navigation.addItem(
            routeKey="settings",
            icon=FluentIcon.SETTING,
            text="설정",
            onClick=lambda: self.switch_page(0),
            position=NavigationItemPosition.TOP
        )
        
        # 데이터 메뉴
        self.navigation.addItem(
            routeKey="data",
            icon=FluentIcon.HISTORY,
            text="데이터",
            onClick=lambda: self.switch_page(1),
            position=NavigationItemPosition.TOP
        )
        
        # 봇 메뉴
        self.navigation.addItem(
            routeKey="bot",
            icon=FluentIcon.ROBOT,
            text="봇",
            onClick=lambda: self.switch_page(2),
            position=NavigationItemPosition.TOP
        )
        
        # 하단 - 테마 전환
        self.navigation.addItem(
            routeKey="theme",
            icon=FluentIcon.CONSTRACT,
            text="테마 전환",
            onClick=self.toggle_theme,
            position=NavigationItemPosition.BOTTOM
        )
        
        # 기본 선택
        self.navigation.setCurrentItem("settings")
    
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


