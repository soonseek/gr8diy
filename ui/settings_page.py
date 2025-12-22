"""
Settings Page - Exchange Integration + GPT
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QStackedWidget,
    QScrollArea, QGridLayout, QFrame
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    Pivot, LineEdit, PasswordLineEdit, 
    PushButton, InfoBar,
    SubtitleLabel, BodyLabel, SwitchButton, ComboBox, FluentIcon
)

from api.exchange_factory import get_exchange_factory
from api.gpt_client import GPTClient
from utils.crypto import CredentialManager
from config.settings import CREDENTIALS_PATH
from config.exchanges import (
    SUPPORTED_EXCHANGES, ALL_EXCHANGE_IDS, DEFAULT_EXCHANGE_ID
)
from utils.logger import logger


class SettingsPage(QWidget):
    """Settings Page"""
    
    def __init__(self):
        super().__init__()
        self.credential_manager = CredentialManager(CREDENTIALS_PATH)
        self.gpt_client = GPTClient()
        
        self.exchange_ids = ALL_EXCHANGE_IDS.copy()
        self.current_exchange_id = DEFAULT_EXCHANGE_ID
        self.is_testnet = False
        
        self._init_ui()
        
        self.current_exchange_id = self.exchange_ids[self.exchange_combo.currentIndex()]
        self.exchange_combo.currentIndexChanged.connect(self._on_exchange_changed)
        self.testnet_switch.checkedChanged.connect(self._on_testnet_changed)
        
        self._update_ui()
        self._load_credentials()
    
    def _init_ui(self):
        """UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        
        self.stack_widget = QStackedWidget(self)
        
        exchange_widget = self._create_exchange_widget()
        gpt_widget = self._create_gpt_widget()
        
        self.pivot.addItem("exchange", "Exchange Integration", lambda: self.stack_widget.setCurrentIndex(0), icon=FluentIcon.CONNECT)
        self.pivot.addItem("gpt", "GPT", lambda: self.stack_widget.setCurrentIndex(1), icon=FluentIcon.ROBOT)
        self.pivot.addItem("ui", "UI Settings", lambda: self.stack_widget.setCurrentIndex(2), icon=FluentIcon.SETTING)
        
        self.stack_widget.addWidget(exchange_widget)
        self.stack_widget.addWidget(gpt_widget)
        ui_widget = self._create_ui_widget()
        self.stack_widget.addWidget(ui_widget)
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack_widget)
        
        self.pivot.setCurrentItem("exchange")
    
    def _create_exchange_widget(self) -> QWidget:
        """Exchange Integration"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Exchange selection
        layout.addWidget(SubtitleLabel("Exchange Selection"))

        info = BodyLabel(f"Supports {len(ALL_EXCHANGE_IDS)} exchanges")
        info.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(info)

        self.exchange_combo = ComboBox()
        self.exchange_combo.setFixedHeight(32)
        self.exchange_combo.setMinimumWidth(300)
        self.exchange_combo.setMaximumWidth(400)

        # Apply dropdown style
        from ui.theme import get_custom_stylesheet
        self.exchange_combo.setStyleSheet(get_custom_stylesheet())

        # Additional style for width limit
        width_style = """
            QComboBox {
                max-width: 380px;
                min-width: 280px;
            }
            QComboBox QAbstractItemView {
                max-width: 380px !important;
                min-width: 280px !important;
            }
        """
        current_style = self.exchange_combo.styleSheet()
        self.exchange_combo.setStyleSheet(current_style + width_style)

        for ex_id in self.exchange_ids:
            ex_info = SUPPORTED_EXCHANGES.get(ex_id, {})
            self.exchange_combo.addItem(f"{ex_info.get('name', ex_id)} (#{ex_info.get('rank', 999)})")
        try:
            self.exchange_combo.setCurrentIndex(self.exchange_ids.index(DEFAULT_EXCHANGE_ID))
        except:
            self.exchange_combo.setCurrentIndex(0)
        layout.addWidget(self.exchange_combo)
        
        # Testnet
        testnet_row = QHBoxLayout()
        testnet_row.setSpacing(5)
        testnet_row.addWidget(BodyLabel("Testnet:"))
        self.testnet_switch = SwitchButton()
        testnet_row.addWidget(self.testnet_switch)
        self.testnet_label = BodyLabel("Mainnet")
        self.testnet_label.setStyleSheet("color: #27ae60; font-size: 10px;")
        testnet_row.addWidget(self.testnet_label)
        testnet_row.addStretch()
        layout.addLayout(testnet_row)
        
        self._add_line(layout)
        
        # API Input
        self.api_title = SubtitleLabel("API Integration")
        layout.addWidget(self.api_title)
        
        form = QFormLayout()
        form.setSpacing(3)
        form.setContentsMargins(0, 0, 0, 0)
        
        self.api_key_edit = LineEdit()
        self.api_key_edit.setPlaceholderText("API Key")
        self.api_key_edit.setFixedHeight(28)
        form.addRow("API Key:", self.api_key_edit)
        
        self.secret_edit = PasswordLineEdit()
        self.secret_edit.setPlaceholderText("Secret")
        self.secret_edit.setFixedHeight(28)
        form.addRow("Secret:", self.secret_edit)
        
        self.passphrase_edit = PasswordLineEdit()
        self.passphrase_edit.setPlaceholderText("Passphrase")
        self.passphrase_edit.setFixedHeight(28)
        self.passphrase_label = QLabel("Passphrase:")
        form.addRow(self.passphrase_label, self.passphrase_edit)
        
        layout.addLayout(form)
        
        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(5)

        save_btn = PushButton("Save")
        save_btn.setFixedHeight(28)
        save_btn.clicked.connect(self._save_credentials)
        btn_row.addWidget(save_btn)

        test_btn = PushButton("Test")
        test_btn.setFixedHeight(28)
        test_btn.clicked.connect(self._test_connection)
        btn_row.addWidget(test_btn)

        del_btn = PushButton("Delete")
        del_btn.setFixedHeight(28)
        del_btn.clicked.connect(self._delete_credentials)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        self._add_line(layout)
        
        # Account Settings Verification
        layout.addWidget(SubtitleLabel("Account Settings Verification"))

        info2 = BodyLabel("Hedge Mode Recommended")
        info2.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(info2)

        acct_ex_row = QHBoxLayout()
        acct_ex_row.setSpacing(5)
        acct_ex_row.addWidget(BodyLabel("Exchange:"))
        self.settings_ex_combo = ComboBox()
        self.settings_ex_combo.setFixedHeight(28)
        for ex_id in self.exchange_ids:
            ex_info = SUPPORTED_EXCHANGES.get(ex_id, {})
            self.settings_ex_combo.addItem(f"{ex_info.get('name', ex_id)}")
        acct_ex_row.addWidget(self.settings_ex_combo)
        acct_ex_row.addStretch()
        layout.addLayout(acct_ex_row)
        
        self.acct_label = BodyLabel("Account: -")
        self.acct_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.acct_label)
        
        self.pos_label = BodyLabel("Position: -")
        self.pos_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.pos_label)
        
        acct_btn_row = QHBoxLayout()
        acct_btn_row.setSpacing(5)
        
        check_btn = PushButton("Check")
        check_btn.setFixedHeight(28)
        check_btn.clicked.connect(self._check_config)
        acct_btn_row.addWidget(check_btn)

        self.fix_btn = PushButton("Auto Fix")
        self.fix_btn.setFixedHeight(28)
        self.fix_btn.setEnabled(False)
        self.fix_btn.clicked.connect(self._fix_config)
        acct_btn_row.addWidget(self.fix_btn)
        acct_btn_row.addStretch()

        layout.addLayout(acct_btn_row)

        self._add_line(layout)

        # Integration Status
        layout.addWidget(SubtitleLabel("Integration Status"))
        self.status_grid = QGridLayout()
        self.status_grid.setSpacing(3)
        self._update_status_grid()
        layout.addLayout(self.status_grid)
        
        layout.addStretch()
        scroll.setWidget(widget)
        return scroll
    
    def _create_gpt_widget(self) -> QWidget:
        """GPT"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        layout.addWidget(SubtitleLabel("GPT API Integration"))

        info = BodyLabel("Optional - AI Analysis Features")
        info.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(info)
        
        form = QFormLayout()
        form.setSpacing(3)
        
        self.gpt_api_key_edit = PasswordLineEdit()
        self.gpt_api_key_edit.setPlaceholderText("OpenAI API Key")
        self.gpt_api_key_edit.setFixedHeight(28)
        form.addRow("API Key:", self.gpt_api_key_edit)
        
        layout.addLayout(form)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(5)
        
        save_btn = PushButton("Save")
        save_btn.setFixedHeight(28)
        save_btn.clicked.connect(self._save_gpt)
        btn_row.addWidget(save_btn)

        test_btn = PushButton("Test")
        test_btn.setFixedHeight(28)
        test_btn.clicked.connect(self._test_gpt)
        btn_row.addWidget(test_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)
        layout.addStretch()

        return widget

    def _add_line(self, layout):
        """Separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: #4a5080;")
        line.setFixedHeight(1)
        layout.addWidget(line)
    
    def _on_exchange_changed(self, index: int):
        """Exchange change"""
        if index < 0 or index >= len(self.exchange_ids):
            return
        
        self.current_exchange_id = self.exchange_ids[index]
        self._update_ui()
        self._load_credentials()
    
    def _on_testnet_changed(self, checked: bool):
        """Testnet change"""
        ex = SUPPORTED_EXCHANGES.get(self.current_exchange_id, {})

        if checked and not ex.get('has_testnet'):
            self.testnet_switch.setChecked(False)
            InfoBar.warning("Not Supported", f"{ex.get('name')} testnet not supported", parent=self)
            return
        
        self.is_testnet = checked
        self._update_ui()
        
        separate = ex.get('testnet_separate_api', False)
        if not separate and checked:
            InfoBar.info("Using Mainnet Keys", f"{ex.get('name')} shares mainnet keys", parent=self)
        elif separate or not checked:
            self._load_credentials()

    def _update_ui(self):
        """UI update"""
        ex = SUPPORTED_EXCHANGES.get(self.current_exchange_id, {})
        name = ex.get('name', self.current_exchange_id)

        mode = " (Testnet)" if self.is_testnet else ""
        self.api_title.setText(f"{name} API{mode}")

        needs_pass = ex.get('requires_passphrase', False)
        self.passphrase_edit.setVisible(needs_pass)
        self.passphrase_label.setVisible(needs_pass)

        if self.is_testnet:
            url = ex.get('testnet_url', '')
            self.testnet_label.setText(f"Testnet - {url}")
            self.testnet_label.setStyleSheet("color: #f39c12; font-size: 10px;")
        else:
            self.testnet_label.setText("Mainnet")
            self.testnet_label.setStyleSheet("color: #27ae60; font-size: 10px;")

    def _load_credentials(self):
        """Load credentials"""
        ex = SUPPORTED_EXCHANGES.get(self.current_exchange_id, {})
        separate = ex.get('testnet_separate_api', False)
        
        use_testnet = self.is_testnet and separate
        
        creds = self.credential_manager.get_exchange_credentials(
            self.current_exchange_id, 
            is_testnet=use_testnet
        )
        
        self.api_key_edit.setText(creds.get('api_key', ''))
        self.secret_edit.setText(creds.get('secret', ''))
        self.passphrase_edit.setText(creds.get('passphrase', ''))
        
        gpt = self.credential_manager.get_gpt_credentials()
        self.gpt_api_key_edit.setText(gpt.get('api_key', ''))
    
    def _save_credentials(self):
        """Save"""
        api_key = self.api_key_edit.text().strip()
        secret = self.secret_edit.text().strip()
        passphrase = self.passphrase_edit.text().strip()

        if not api_key or not secret:
            InfoBar.warning("Input Required", "API Key/Secret required", parent=self)
            return
        
        try:
            ex = SUPPORTED_EXCHANGES.get(self.current_exchange_id, {})
            separate = ex.get('testnet_separate_api', False)
            
            self.credential_manager.save_exchange_credentials(
                self.current_exchange_id, api_key, secret, passphrase, False
            )
            
            if self.is_testnet and separate:
                self.credential_manager.save_exchange_credentials(
                    self.current_exchange_id, api_key, secret, passphrase, True
                )
            
            self._update_status_grid()
            
            mode = "Testnet" if (self.is_testnet and separate) else "Mainnet"
            InfoBar.success("Save Complete", f"{ex.get('name')} ({mode})", parent=self)

        except Exception as e:
            InfoBar.error("Save Failed", str(e), duration=-1, parent=self)

    def _test_connection(self):
        """Connection test"""
        api_key = self.api_key_edit.text().strip()
        secret = self.secret_edit.text().strip()
        passphrase = self.passphrase_edit.text().strip()

        if not api_key or not secret:
            InfoBar.warning("Input Required", "Enter API Key/Secret", parent=self)
            return
        
        try:
            from api.ccxt_client import CCXTClient
            
            client = CCXTClient(
                self.current_exchange_id, api_key, secret, passphrase, self.is_testnet
            )
            
            success, msg = client.test_connection()
            
            if success:
                InfoBar.success("Integration Success", msg, parent=self)
            else:
                InfoBar.error("Integration Failed", msg, duration=-1, parent=self)

        except Exception as e:
            InfoBar.error("Error", str(e), duration=-1, parent=self)

    def _delete_credentials(self):
        """Delete"""
        try:
            ex = SUPPORTED_EXCHANGES.get(self.current_exchange_id, {})
            separate = ex.get('testnet_separate_api', False)
            
            use_testnet = self.is_testnet and separate
            
            self.credential_manager.delete_exchange_credentials(
                self.current_exchange_id, use_testnet
            )
            
            self.api_key_edit.clear()
            self.secret_edit.clear()
            self.passphrase_edit.clear()
            
            self._update_status_grid()
            
            InfoBar.success("Delete Complete", f"{ex.get('name')}", parent=self)

        except Exception as e:
            InfoBar.error("Delete Failed", str(e), duration=-1, parent=self)

    def _update_status_grid(self):
        """Status grid"""
        while self.status_grid.count():
            item = self.status_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        h_ex = BodyLabel("Exchange")
        h_ex.setStyleSheet("font-size: 10px; font-weight: bold;")
        h_main = BodyLabel("Main")
        h_main.setStyleSheet("font-size: 10px; font-weight: bold;")
        h_test = BodyLabel("Test")
        h_test.setStyleSheet("font-size: 10px; font-weight: bold;")
        
        self.status_grid.addWidget(h_ex, 0, 0)
        self.status_grid.addWidget(h_main, 0, 1)
        self.status_grid.addWidget(h_test, 0, 2)
        
        top = ["binance", "bybit", "okx", "bitget", "gate", "kucoin", "htx", "kraken"]
        
        row = 1
        for ex_id in top:
            if ex_id not in SUPPORTED_EXCHANGES:
                continue
            
            ex = SUPPORTED_EXCHANGES[ex_id]
            
            name_lbl = BodyLabel(ex['name'])
            name_lbl.setStyleSheet("font-size: 10px;")
            self.status_grid.addWidget(name_lbl, row, 0)
            
            m_creds = self.credential_manager.get_exchange_credentials(ex_id, False)
            m_lbl = BodyLabel("✅" if m_creds.get('api_key') else "❌")
            m_lbl.setStyleSheet("font-size: 10px;")
            self.status_grid.addWidget(m_lbl, row, 1)
            
            if ex.get('has_testnet'):
                t_creds = self.credential_manager.get_exchange_credentials(ex_id, True)
                t_lbl = BodyLabel("✅" if t_creds.get('api_key') else "❌")
            else:
                t_lbl = BodyLabel("-")
            t_lbl.setStyleSheet("font-size: 10px;")
            self.status_grid.addWidget(t_lbl, row, 2)
            
            row += 1
    
    def _save_gpt(self):
        """GPT Save"""
        api_key = self.gpt_api_key_edit.text().strip()
        if not api_key:
            InfoBar.warning("Input Required", "API Key required", parent=self)
            return

        try:
            self.credential_manager.save_gpt_credentials(api_key)
            InfoBar.success("Save Complete", "GPT API saved", parent=self)
        except Exception as e:
            InfoBar.error("Save Failed", str(e), duration=-1, parent=self)

    def _test_gpt(self):
        """GPT Test"""
        api_key = self.gpt_api_key_edit.text().strip()
        if not api_key:
            InfoBar.warning("Input Required", "API Key required", parent=self)
            return
        
        try:
            self.gpt_client.api_key = api_key
            success, msg = self.gpt_client.test_connection()
            
            if success:
                InfoBar.success("Integration Success", msg, parent=self)
            else:
                InfoBar.error("Integration Failed", msg, duration=-1, parent=self)
        except Exception as e:
            InfoBar.error("Error", str(e), duration=-1, parent=self)

    def _check_config(self):
        """Check configuration"""
        index = self.settings_ex_combo.currentIndex()
        if index < 0:
            return
        
        ex_id = self.exchange_ids[index]
        
        try:
            factory = get_exchange_factory()
            client = factory.get_client(ex_id)
            
            if not client:
                InfoBar.warning("연동 필요", f"{ex_id} API 먼저 연동", parent=self)
                return
            
            config = client.get_account_config()
            
            if config:
                self.acct_label.setText(f"Account: {config.get('acct_lv', 'N/A')}")
                self.pos_label.setText(f"Position: {config.get('pos_mode', 'N/A')}")
                
                needs_fix = config.get('pos_mode') != 'long_short_mode'
                self.fix_btn.setEnabled(needs_fix)
                
                if not needs_fix:
                    InfoBar.success("설정 확인", "올바른 설정", parent=self)
            else:
                self.acct_label.setText("Account: 조회 실패")
                self.pos_label.setText("Position: 조회 실패")
                
        except Exception as e:
            InfoBar.error("확인 실패", str(e), duration=-1, parent=self)
    
    def _fix_config(self):
        """설정 수정"""
        index = self.settings_ex_combo.currentIndex()
        if index < 0:
            return
        
        ex_id = self.exchange_ids[index]
        
        try:
            factory = get_exchange_factory()
            client = factory.get_client(ex_id)
            
            if client and client.set_hedge_mode():
                InfoBar.success("설정 변경", "Hedge Mode 설정됨", parent=self)
                self._check_config()
            else:
                InfoBar.warning("변경 실패", "거래소에서 직접 변경 필요", parent=self)
        except Exception as e:
            InfoBar.error("오류", str(e), duration=-1, parent=self)

    def _create_ui_widget(self) -> QWidget:
        """UI 설정 위젯"""
        from qfluentwidgets import CardWidget
        from PySide6.QtWidgets import QSpinBox, QButtonGroup, QRadioButton, QVBoxLayout, QGroupBox

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # 창 설정 카드
        window_card = CardWidget()
        window_layout = QVBoxLayout(window_card)
        window_layout.addWidget(SubtitleLabel("창 설정"))

        # 시작 위치 설정
        position_layout = QVBoxLayout()
        position_layout.addWidget(BodyLabel("창 시작 위치:"))

        self.position_group = QButtonGroup()
        self.position_buttons = {}

        positions = [
            ("center", "화면 중앙"),
            ("top_left", "왼쪽 상단"),
            ("top_right", "오른쪽 상단"),
            ("bottom_left", "왼쪽 하단"),
            ("bottom_right", "오른쪽 하단"),
            ("remember", "마지막 위치 기억")
        ]

        for value, text in positions:
            radio = QRadioButton(text)
            self.position_buttons[value] = radio
            self.position_group.addButton(radio)
            position_layout.addWidget(radio)

        window_layout.addLayout(position_layout)

        # 시작 모드 설정
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(BodyLabel("시작 모드:"))

        self.mode_group = QButtonGroup()
        self.mode_buttons = {}

        modes = [
            ("maximized", "전체 화면 (권장)"),
            ("fullscreen", "진정한 전체 화면"),
            ("normal", "일반 크기"),
            ("remember", "마지막 크기 기억")
        ]

        for value, text in modes:
            radio = QRadioButton(text)
            self.mode_buttons[value] = radio
            self.mode_group.addButton(radio)
            mode_layout.addWidget(radio)

        window_layout.addLayout(mode_layout)

        # 디스플레이 선택
        display_layout = QHBoxLayout()
        display_layout.addWidget(BodyLabel("기본 디스플레이:"))
        self.display_combo = ComboBox()
        self.display_combo.addItems(["기본 디스플레이", "보조 디스플레이 1", "보조 디스플레이 2"])
        display_layout.addWidget(self.display_combo)
        display_layout.addStretch()

        window_layout.addLayout(display_layout)

        layout.addWidget(window_card)

        # 적용 버튼
        apply_btn = PushButton("설정 저장")
        apply_btn.clicked.connect(self._save_ui_settings)
        layout.addWidget(apply_btn)

        layout.addStretch()

        # 기본값 설정
        self._load_ui_settings()

        scroll.setWidget(widget)
        return scroll

    def _load_ui_settings(self):
        """UI 설정 로드"""
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

            # 위치 설정
            position = settings.get("position", "center")
            if position in self.position_buttons:
                self.position_buttons[position].setChecked(True)

            # 모드 설정
            mode = settings.get("mode", "maximized")
            if mode in self.mode_buttons:
                self.mode_buttons[mode].setChecked(True)

            # 디스플레이 설정
            display_index = settings.get("display", 0)
            if 0 <= display_index < self.display_combo.count():
                self.display_combo.setCurrentIndex(display_index)

        except Exception as e:
            logger.error("SettingsPage", f"UI 설정 로드 실패: {str(e)}")

    def _save_ui_settings(self):
        """UI 설정 저장"""
        try:
            import json
            import os

            # 선택된 값 가져오기
            position = None
            for value, button in self.position_buttons.items():
                if button.isChecked():
                    position = value
                    break

            mode = None
            for value, button in self.mode_buttons.items():
                if button.isChecked():
                    mode = value
                    break

            display = self.display_combo.currentIndex()

            settings = {
                "position": position or "center",
                "mode": mode or "maximized",
                "display": display
            }

            # 폴더 생성
            os.makedirs("config", exist_ok=True)

            # 설정 저장
            with open("config/ui_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

            InfoBar.success(
                title="설정 저장",
                content="UI 설정이 저장되었습니다. 애플리케이션을 재시작하면 적용됩니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                duration=3000,
                parent=self
            )

            logger.info("SettingsPage", f"UI 설정 저장: {settings}")

        except Exception as e:
            InfoBar.error(
                title="저장 실패",
                content=f"UI 설정 저장 실패: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                duration=-1,
                parent=self
            )
            logger.error("SettingsPage", f"UI 설정 저장 실패: {str(e)}")
