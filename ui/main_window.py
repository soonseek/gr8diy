# -*- coding: utf-8 -*-
"""
Main Window
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel, QSplitter, QApplication, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QScreen
from datetime import datetime
from qfluentwidgets import (
    NavigationInterface, NavigationItemPosition,
    FluentIcon, setTheme, Theme, isDarkTheme
)

# Page imports - Only safe pages activated for now
from ui.home_page import HomePage
from ui.settings_page import SettingsPage
# Temporarily disable problematic pages
# from ui.data_page import DataPage
# from ui.bot_page import BotPage
# from ui.backtest_page import BacktestPage
from ui.log_widget import LogWidget
from ui.theme import apply_theme_to_widget, Gr8Theme
from config.settings import WINDOW_TITLE
from utils.logger import logger


class MainWindow(QMainWindow):
    """Main Window"""

    def __init__(self):
        print("[DEBUG-MW] Step 1: MainWindow __init__ 시작")
        print("[DEBUG-MW] Step 2: super().__init__() 호출 직전")
        super().__init__()
        print("[DEBUG-MW] Step 3: super().__init__() 완료")

        print("[DEBUG-MW] Step 4: setWindowTitle 호출")
        self.setWindowTitle(WINDOW_TITLE)

        # Apply custom theme
        print("[DEBUG-MW] Step 4.5: Applying custom theme")
        apply_theme_to_widget(self)

        # Set window position and size according to UI settings
        print("[DEBUG-MW] Step 5: Loading UI settings and configuring window")
        self._apply_ui_settings()

        # Central widget
        print("[DEBUG-MW] Step 6: Creating QWidget() started")
        central_widget = QWidget()
        print("[DEBUG-MW] Step 7: QWidget() creation completed")

        print("[DEBUG-MW] Step 8: setCentralWidget call")
        self.setCentralWidget(central_widget)

        # Main layout
        print("[DEBUG-MW] Step 9: Creating QHBoxLayout")
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Content area
        print("[DEBUG-MW] Step 12: Creating QVBoxLayout")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header area
        print("[DEBUG-MW] Step 13: _create_header call")
        header_widget = self._create_header()
        content_layout.addWidget(header_widget)

        # Stack widget (for page switching)
        print("[DEBUG-MW] Step 14: Creating QStackedWidget")
        self.stack_widget = QStackedWidget()

        # Configure stack_widget to expand
        from PySide6.QtWidgets import QSizePolicy
        self.stack_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout.addWidget(self.stack_widget)

        # Content container
        print("[DEBUG-MW] Step 17: Creating content_container QWidget")
        content_container = QWidget()
        content_container.setLayout(content_layout)

        # Configure content container to expand vertically
        content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Log widget (placed at bottom)
        print(f"[DEBUG-MW] Step 15: Creating LogWidget")
        try:
            self.log_widget = LogWidget()
            print("[DEBUG-MW] Step 16: LogWidget creation completed")
        except Exception as e:
            print(f"[DEBUG-MW-ERROR] LogWidget creation failed: {e}")
            # Replace with default widget on failure
            from PySide6.QtWidgets import QTextEdit
            self.log_widget = QTextEdit()
            self.log_widget.setReadOnly(True)
            self.log_widget.append("Log system has been loaded.")
            print("[DEBUG-MW] Step 16: Replaced with default log widget completed")

        # Create splitter (content on left, log on right)
        print("[DEBUG-MW] Step 17.5: Creating QSplitter")
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(content_container)
        splitter.addWidget(self.log_widget)

        # Set log widget width
        self.log_widget.setMaximumWidth(400)  # Maximum width 400px
        self.log_widget.setMinimumWidth(300)  # Minimum width 300px

        # Initial ratio: content 80%, log 20% (width ratio)
        splitter.setSizes([1200, 300])  # Based on 1500px total: 1200:300
        splitter.setStretchFactor(0, 80)  # Content occupies 80%
        splitter.setStretchFactor(1, 20)  # Log occupies 20%

        # Configure splitter to occupy entire space
        splitter.setChildrenCollapsible(False)

        # Create navigation interface (fixed on left, menu button hidden)
        print("[DEBUG-MW] Step 10: NavigationInterface creation started")
        self.navigation = NavigationInterface(showMenuButton=False, showReturnButton=False)

        # Navigation 200px fixed width (no collapse/expand)
        self.navigation.setExpandWidth(200)
        self.navigation.setFixedWidth(200)
        self.navigation.setCollapsible(False)  # Disable size adjustment

        print("[DEBUG-MW] Step 11: NavigationInterface creation completed")

        # Add widgets to main layout
        print("[DEBUG-MW] Step 18: Adding widgets to layout")
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(splitter, stretch=1)

        # Initialize pages
        print("[DEBUG-MW] Step 19: _init_pages call")
        self._init_pages()

        # Add navigation menu
        print("[DEBUG-MW] Step 20: _init_navigation call")
        self._init_navigation()

        # Connect logger signal
        print("[DEBUG-MW] Step 21: _connect_logger call")
        self._connect_logger()

        print("[DEBUG-MW] Step 22: MainWindow initialization completed")
        logger.info("UI", "Main window initialization completed")

    def _create_header(self):
        """Header - Simple guidance message"""
        header = QLabel()
        header.setText(f"<span style='color:#00d4aa;font-size:16px;font-weight:bold;'>Gr8 DIY</span>"
                       f"<span style='color:#7f8c8d;font-size:11px;margin-left:12px;'>"
                       f"  Open-source automated trading platform developed by YouTube &lt;Sofia Papa&gt; and subscribers</span>")
        header.setContentsMargins(12, 8, 0, 8)
        header.setStyleSheet("background:transparent; border:none;")
        return header

    def _init_pages(self):
        """Page initialization - Only HomePage actually used"""
        print("[DEBUG-MW] Step 19: Starting page creation")

        # Home page (actual page)
        print("[DEBUG-MW] Step 19-0: Starting HomePage creation")
        try:
            self.home_page = HomePage()
            print("[DEBUG-MW] Step 19-0.5: HomePage creation completed")
            self.stack_widget.addWidget(self.home_page)
        except Exception as e:
            import traceback
            print(f"[DEBUG-MW-ERROR] HomePage creation failed: {e}")
            traceback.print_exc()
            raise

        # Settings page (actual page)
        print("[DEBUG-MW] Step 19-1: Starting SettingsPage creation")
        try:
            self.settings_page = SettingsPage()
            print("[DEBUG-MW] Step 19-2: SettingsPage creation completed")
            self.stack_widget.addWidget(self.settings_page)
        except Exception as e:
            import traceback
            print(f"[DEBUG-MW-ERROR] SettingsPage creation failed: {e}")
            traceback.print_exc()
            raise

        # Create pages later for lazy loading - add empty placeholders first
        print("[DEBUG-MW] Step 19-3: Adding DataPage placeholder")
        self.data_page = None
        self.stack_widget.addWidget(QLabel("Loading data page..."))

        print("[DEBUG-MW] Step 19-5: Adding BotPage placeholder")
        self.bot_page = None
        self.stack_widget.addWidget(QLabel("Loading bot page..."))

        print("[DEBUG-MW] Step 19-7: Adding BacktestPage placeholder")
        self.backtest_page = None
        self.stack_widget.addWidget(QLabel("Loading backtest page..."))

        print("[DEBUG-MW] Step 19-9: Page placeholder creation completed")

    def _init_navigation(self):
        """Add navigation menu"""
        # Home menu
        self.navigation.addItem(
            routeKey="home",
            icon=FluentIcon.HOME,
            text="Home",
            onClick=lambda: self.switch_page(0),
            position=NavigationItemPosition.TOP
        )

        # Settings menu
        self.navigation.addItem(
            routeKey="settings",
            icon=FluentIcon.SETTING,
            text="Settings",
            onClick=lambda: self.switch_page(1),
            position=NavigationItemPosition.TOP
        )

        # Data menu
        self.navigation.addItem(
            routeKey="data",
            icon=FluentIcon.HISTORY,
            text="Data",
            onClick=lambda: self.switch_page(2),
            position=NavigationItemPosition.TOP
        )

        # Bot menu
        self.navigation.addItem(
            routeKey="bot",
            icon=FluentIcon.ROBOT,
            text="Bot",
            onClick=lambda: self.switch_page(3),
            position=NavigationItemPosition.TOP
        )

        # Backtest menu
        self.navigation.addItem(
            routeKey="backtest",
            icon=FluentIcon.DEVELOPER_TOOLS,
            text="Backtest",
            onClick=lambda: self.switch_page(4),
            position=NavigationItemPosition.TOP
        )

        # Default selection - Home
        self.navigation.setCurrentItem("home")

    def switch_page(self, index: int):
        """Page switching (including lazy loading)"""
        # Load required page if not yet loaded
        if index == 2 and self.data_page is None:  # Data page
            self._load_data_page()
        elif index == 3 and self.bot_page is None:  # Bot page
            self._load_bot_page()
        elif index == 4 and self.backtest_page is None:  # Backtest page
            self._load_backtest_page()

        self.stack_widget.setCurrentIndex(index)

    def _load_data_page(self):
        """Data page lazy loading - enhanced version"""
        print("[DEBUG-MW] Starting data page load (user clicked data menu)...")
        try:
            from ui.data_page_enhanced import DataPageEnhanced
            print("[DEBUG-MW] DataPageEnhanced import successful")

            # Remove placeholder and add actual page
            self.stack_widget.removeWidget(self.stack_widget.widget(2))
            self.data_page = DataPageEnhanced()
            print("[DEBUG-MW] DataPageEnhanced instance creation successful")
            self.stack_widget.insertWidget(2, self.data_page)
            print("[DEBUG-MW] DataPageEnhanced load completed - includes exchange selector UI")

        except Exception as e:
            print(f"[DEBUG-MW-ERROR] DataPage enhanced version load failed: {e}")
            import traceback
            print("[DEBUG-MW-ERROR] Full stack trace:")
            traceback.print_exc()
            # Replace with simple version on failure (no exchange selector UI)
            try:
                from ui.data_page_simple import DataPageSimple
                print("[DEBUG-MW] Replacing with DataPageSimple (no exchange selector UI)")
                self.stack_widget.removeWidget(self.stack_widget.widget(2))
                self.data_page = DataPageSimple()
                self.stack_widget.insertWidget(2, self.data_page)
                print("[DEBUG-MW] DataPageSimple load completed - no exchange selector UI")
            except Exception as e2:
                print(f"[DEBUG-MW-ERROR] DataPage simple version also failed: {e2}")
                self._load_safe_fallback_page(2, "Data Page", f"{str(e)} / {str(e2)}")

    def _load_bot_page(self):
        """Bot page lazy loading - feature recovery version"""
        print("[DEBUG-MW] Loading BotPage with feature recovery version...")
        try:
            from ui.bot_page_simple import BotPageSimple

            # Remove placeholder and add actual page
            self.stack_widget.removeWidget(self.stack_widget.widget(3))
            self.bot_page = BotPageSimple()
            self.stack_widget.insertWidget(3, self.bot_page)
            print("[DEBUG-MW] BotPage feature recovery version load completed")

        except Exception as e:
            print(f"[DEBUG-MW-ERROR] BotPage feature recovery failed: {e}")
            import traceback
            traceback.print_exc()
            # Replace with safe mode on failure
            self._load_safe_fallback_page(3, "Bot Page", str(e))

    def _load_backtest_page(self):
        """Backtest page lazy loading - feature recovery version"""
        print("[DEBUG-MW] Loading BacktestPage with feature recovery version...")
        try:
            from ui.backtest_page_simple import BacktestPageSimple

            # Remove placeholder and add actual page
            self.stack_widget.removeWidget(self.stack_widget.widget(4))
            self.backtest_page = BacktestPageSimple()
            self.stack_widget.insertWidget(4, self.backtest_page)
            print("[DEBUG-MW] BacktestPage feature recovery version load completed")

        except Exception as e:
            print(f"[DEBUG-MW-ERROR] BacktestPage feature recovery failed: {e}")
            import traceback
            traceback.print_exc()
            # Replace with safe mode on failure
            self._load_safe_fallback_page(4, "Backtest Page", str(e))

    def _load_safe_fallback_page(self, index: int, page_name: str, error_msg: str):
        """Load safe fallback page"""
        print(f"[DEBUG-MW] Loading safe fallback page for {page_name}...")
        try:
            from PySide6.QtWidgets import QVBoxLayout, QLabel
            from qfluentwidgets import TitleLabel, InfoBar, InfoBarPosition

            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)
            fallback_layout.setContentsMargins(20, 20, 20, 20)
            fallback_layout.setSpacing(10)

            # Title
            title = TitleLabel(page_name)
            title.setAlignment(Qt.AlignCenter)
            fallback_layout.addWidget(title)

            # Error message
            info = QLabel(f"An issue occurred while loading {page_name}.\n\nRunning in safe mode.\n\nError: {error_msg[:200]}...")
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet("font-size: 14px; color: #666; padding: 20px;")
            info.setWordWrap(True)
            fallback_layout.addWidget(info)

            # Show InfoBar
            info_bar = InfoBar.warning(
                title="Safe Mode",
                content=f"{page_name} has been loaded in safe mode. Some features may be limited.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=8000,
                parent=fallback_widget
            )
            fallback_layout.addWidget(info_bar)

            # Fill remaining space
            fallback_layout.addStretch()

            # Remove placeholder and add fallback page
            self.stack_widget.removeWidget(self.stack_widget.widget(index))
            self.stack_widget.insertWidget(index, fallback_widget)
            print(f"[DEBUG-MW] Safe fallback page for {page_name} load completed")

        except Exception as e:
            print(f"[DEBUG-MW-ERROR] {page_name} fallback page load failed: {e}")
            # Final minimal error page
            error_widget = QLabel(f"{page_name} load failed\n\n{str(e)[:200]}...")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("color: #ff6b6b; padding: 20px; font-size: 14px;")
            error_widget.setWordWrap(True)
            self.stack_widget.removeWidget(self.stack_widget.widget(index))
            self.stack_widget.insertWidget(index, error_widget)

    def toggle_theme(self):
        """Theme toggle"""
        if isDarkTheme():
            setTheme(Theme.LIGHT)
            logger.info("UI", "Switched to light theme")
        else:
            setTheme(Theme.DARK)
            logger.info("UI", "Switched to dark theme")

    def _connect_logger(self):
        """Connect logger to UI"""
        try:
            from utils.logger import logger
            if hasattr(self.log_widget, 'add_log'):
                logger.emitter.log_signal.connect(self.log_widget.add_log)
                print("[DEBUG-MW] Logger connection completed")
            else:
                print("[DEBUG-MW] Not LogWidget but default widget. Attempting alternate logger connection")
                # If default widget, directly connect log messages
                if hasattr(self, '_add_log_to_widget'):
                    logger.emitter.log_signal.connect(self._add_log_to_widget)
                    print("[DEBUG-MW] Alternate logger connection completed")
        except Exception as e:
            print(f"[DEBUG-MW-ERROR] Logger connection failed: {e}")

    def _add_log_to_widget(self, module: str, message: str):
        """Add log message to default widget"""
        if hasattr(self.log_widget, 'append'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_text = f"[{timestamp}] {module}: {message}"
            self.log_widget.append(log_text)
            # Scroll to bottom
            try:
                from PySide6.QtWidgets import QScrollBar
                self.log_widget.verticalScrollBar().setValue(self.log_widget.verticalScrollBar().maximum())
            except:
                pass

    def _apply_ui_settings(self):
        """Apply window position and size according to UI settings"""
        try:
            import json
            import os

            settings_file = "config/ui_settings.json"
            default_settings = {
                "position": "center",
                "mode": "maximized",
                "display": 0
            }

            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = default_settings

            app = QApplication.instance()
            if not app:
                # Apply default settings
                self.setWindowState(Qt.WindowMaximized)
                return

            # Select display
            displays = app.screens()
            display_index = min(settings.get("display", 0), len(displays) - 1)
            screen = displays[display_index].availableGeometry()

            # Set startup mode
            mode = settings.get("mode", "maximized")
            if mode == "fullscreen":
                self.showFullScreen()
            elif mode == "maximized":
                self.setWindowState(Qt.WindowMaximized)
            elif mode == "normal":
                self.setWindowState(Qt.WindowNoState)
                self.resize(1200, 800)
            else:  # remember
                self.setWindowState(Qt.WindowNoState)
                self.resize(1200, 800)

            # Set startup position
            position = settings.get("position", "center")
            if position == "center":
                x = screen.x() + (screen.width() - self.width()) // 2
                y = screen.y() + (screen.height() - self.height()) // 2
                self.move(x, y)
            elif position == "top_left":
                self.move(screen.x() + 50, screen.y() + 50)
            elif position == "top_right":
                x = screen.x() + screen.width() - self.width() - 50
                self.move(max(x, screen.x()), screen.y() + 50)
            elif position == "bottom_left":
                x = screen.x() + 50
                y = screen.y() + screen.height() - self.height() - 50
                self.move(x, max(y, screen.y()))
            elif position == "bottom_right":
                x = screen.x() + screen.width() - self.width() - 50
                y = screen.y() + screen.height() - self.height() - 50
                self.move(max(x, screen.x()), max(y, screen.y()))
            elif position == "remember":
                # Remember last position (future implementation)
                x = screen.x() + (screen.width() - self.width()) // 2
                y = screen.y() + (screen.height() - self.height()) // 2
                self.move(x, y)

            print(f"[DEBUG-MW] UI settings applied: position={position}, mode={mode}, display={display_index}")

        except Exception as e:
            print(f"[DEBUG-MW-ERROR] UI settings application failed: {e}")
            # Apply default settings on failure
            self.setWindowState(Qt.WindowMaximized)

    def closeEvent(self, event):
        """Close event"""
        # Save last window position and size (future implementation)
        logger.info("UI", "Application closed")
        event.accept()