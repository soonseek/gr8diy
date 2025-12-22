# -*- coding: utf-8 -*-
"""
최소한의 메인 윈도우 - 페이지 없음
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

# 페이지 imports 제거 - 문제 해결 후 추가
# from ui.home_page import HomePage
# from ui.settings_page import SettingsPage
# from ui.data_page import DataPage
# from ui.bot_page import BotPage
# from ui.backtest_page import BacktestPage
# from ui.log_widget import LogWidget

from ui.theme import apply_theme_to_widget, Gr8Theme
from config.settings import WINDOW_TITLE
from utils.logger import logger


class MinimalMainWindow(QMainWindow):
    """최소한의 메인 윈도우"""

    def __init__(self):
        print("[DEBUG-MW] Step 1: MinimalMainWindow __init__ 시작")
        super().__init__()
        print("[DEBUG-MW] Step 2: super().__init__() 완료")

        print("[DEBUG-MW] Step 3: setWindowTitle 호출")
        self.setWindowTitle(WINDOW_TITLE)

        # 커스텀 테마 적용
        print("[DEBUG-MW] Step 3.5: 커스텀 테마 적용")
        apply_theme_to_widget(self)

        # 화면 크기에 맞춤 (전체 화면 모드)
        print("[DEBUG-MW] Step 4: showMaximized 호출")
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen().availableGeometry()
            self.setGeometry(screen)
        self.showMaximized()

        # 중앙 위젯
        print("[DEBUG-MW] Step 5: QWidget() 생성")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        print("[DEBUG-MW] Step 6: QHBoxLayout 생성")
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 콘텐츠 영역
        print("[DEBUG-MW] Step 7: QVBoxLayout 생성")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 헤더 영역
        print("[DEBUG-MW] Step 8: 헤더 생성")
        header_widget = self._create_header()
        content_layout.addWidget(header_widget)

        # 스택 위젯 (페이지 전환용)
        print("[DEBUG-MW] Step 9: QStackedWidget 생성")
        self.stack_widget = QStackedWidget()
        content_layout.addWidget(self.stack_widget)

        # 간단한 위젯으로 대체
        print("[DEBUG-MW] Step 10: 기본 위젯 추가")
        default_widget = QLabel("애플리케이션이 로드되었습니다.\n\n메뉴에서 기능을 선택하세요.")
        default_widget.setAlignment(Qt.AlignCenter)
        default_widget.setStyleSheet("font-size: 16px; color: #e0e0e0; padding: 50px;")
        self.stack_widget.addWidget(default_widget)

        # 콘텐츠 컨테이너
        print("[DEBUG-MW] Step 11: content_container QWidget 생성")
        content_container = QWidget()
        content_container.setLayout(content_layout)

        # 기본 로그 위젯 (텍스트 편집기로 대체)
        print("[DEBUG-MW] Step 12: 기본 로그 위젯 생성")
        from PySide6.QtWidgets import QTextEdit
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setMaximumHeight(200)
        self.log_widget.append("로그 시스템이 초기화되었습니다.")

        # 스플리터 생성 (콘텐츠 | 로그)
        print("[DEBUG-MW] Step 13: QSplitter 생성")
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(content_container)
        splitter.addWidget(self.log_widget)
        splitter.setSizes([1536, 384])
        splitter.setStretchFactor(0, 8)
        splitter.setStretchFactor(1, 2)

        # 내비게이션 인터페이스 생성
        print("[DEBUG-MW] Step 14: NavigationInterface 생성")
        self.navigation = NavigationInterface(showMenuButton=False, showReturnButton=False)
        self.navigation.setExpandWidth(200)
        self.navigation.setFixedWidth(200)
        self.navigation.setCollapsible(False)

        # 메인 레이아웃에 위젯 추가
        print("[DEBUG-MW] Step 15: 레이아웃에 위젯 추가")
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(splitter, stretch=1)

        # 최소한의 내비게이션 메뉴
        print("[DEBUG-MW] Step 16: 최소한의 내비게이션 메뉴 추가")
        self._init_minimal_navigation()

        print("[DEBUG-MW] Step 17: MinimalMainWindow 초기화 완료")
        logger.info("UI", "최소한의 메인 윈도우 초기화 완료")

    def _create_header(self):
        """헤더 - 간단한 안내 메시지"""
        header = QLabel()
        header.setText(f"<span style='color:#00d4aa;font-size:16px;font-weight:bold;'>Gr8 DIY</span>"
                       f"<span style='color:#7f8c8d;font-size:11px;margin-left:12px;'>"
                       f"  최소한의 모드 - 안전한 로드</span>")
        header.setContentsMargins(12, 8, 0, 8)
        header.setStyleSheet("background:transparent; border:none;")
        return header

    def _init_minimal_navigation(self):
        """최소한의 내비게이션 메뉴"""
        # 홈 메뉴
        self.navigation.addItem(
            routeKey="home",
            icon=FluentIcon.HOME,
            text="홈",
            onClick=lambda: self.stack_widget.setCurrentIndex(0),
            position=NavigationItemPosition.TOP
        )

        # 기본 선택 - 홈
        self.navigation.setCurrentItem("home")

    def switch_page(self, index: int):
        """페이지 전환"""
        if hasattr(self, 'stack_widget'):
            self.stack_widget.setCurrentIndex(index)