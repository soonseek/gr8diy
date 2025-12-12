"""
설정 페이지 - 거래소 연동 + GPT
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
    """설정 페이지"""
    
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
        
        self.pivot.addItem("exchange", "거래소 연동", lambda: self.stack_widget.setCurrentIndex(0), icon=FluentIcon.CONNECT)
        self.pivot.addItem("gpt", "GPT", lambda: self.stack_widget.setCurrentIndex(1), icon=FluentIcon.ROBOT)
        
        self.stack_widget.addWidget(exchange_widget)
        self.stack_widget.addWidget(gpt_widget)
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack_widget)
        
        self.pivot.setCurrentItem("exchange")
    
    def _create_exchange_widget(self) -> QWidget:
        """거래소 연동"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 거래소 선택
        layout.addWidget(SubtitleLabel("거래소 선택"))
        
        info = BodyLabel(f"{len(ALL_EXCHANGE_IDS)}개 거래소 지원")
        info.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(info)
        
        self.exchange_combo = ComboBox()
        self.exchange_combo.setFixedHeight(32)
        for ex_id in self.exchange_ids:
            ex_info = SUPPORTED_EXCHANGES.get(ex_id, {})
            self.exchange_combo.addItem(f"{ex_info.get('name', ex_id)} (#{ex_info.get('rank', 999)})")
        try:
            self.exchange_combo.setCurrentIndex(self.exchange_ids.index(DEFAULT_EXCHANGE_ID))
        except:
            self.exchange_combo.setCurrentIndex(0)
        layout.addWidget(self.exchange_combo)
        
        # 테스트넷
        testnet_row = QHBoxLayout()
        testnet_row.setSpacing(5)
        testnet_row.addWidget(BodyLabel("테스트넷:"))
        self.testnet_switch = SwitchButton()
        testnet_row.addWidget(self.testnet_switch)
        self.testnet_label = BodyLabel("메인넷")
        self.testnet_label.setStyleSheet("color: #27ae60; font-size: 10px;")
        testnet_row.addWidget(self.testnet_label)
        testnet_row.addStretch()
        layout.addLayout(testnet_row)
        
        self._add_line(layout)
        
        # API 입력
        self.api_title = SubtitleLabel("API 연동")
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
        
        # 버튼
        btn_row = QHBoxLayout()
        btn_row.setSpacing(5)
        
        save_btn = PushButton("저장")
        save_btn.setFixedHeight(28)
        save_btn.clicked.connect(self._save_credentials)
        btn_row.addWidget(save_btn)
        
        test_btn = PushButton("테스트")
        test_btn.setFixedHeight(28)
        test_btn.clicked.connect(self._test_connection)
        btn_row.addWidget(test_btn)
        
        del_btn = PushButton("삭제")
        del_btn.setFixedHeight(28)
        del_btn.clicked.connect(self._delete_credentials)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        self._add_line(layout)
        
        # 계정 설정 확인
        layout.addWidget(SubtitleLabel("계정 설정 확인"))
        
        info2 = BodyLabel("Hedge Mode 권장")
        info2.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(info2)
        
        acct_ex_row = QHBoxLayout()
        acct_ex_row.setSpacing(5)
        acct_ex_row.addWidget(BodyLabel("거래소:"))
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
        
        check_btn = PushButton("확인")
        check_btn.setFixedHeight(28)
        check_btn.clicked.connect(self._check_config)
        acct_btn_row.addWidget(check_btn)
        
        self.fix_btn = PushButton("자동 수정")
        self.fix_btn.setFixedHeight(28)
        self.fix_btn.setEnabled(False)
        self.fix_btn.clicked.connect(self._fix_config)
        acct_btn_row.addWidget(self.fix_btn)
        acct_btn_row.addStretch()
        
        layout.addLayout(acct_btn_row)
        
        self._add_line(layout)
        
        # 연동 상태
        layout.addWidget(SubtitleLabel("연동 상태"))
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
        
        layout.addWidget(SubtitleLabel("GPT API 연동"))
        
        info = BodyLabel("선택 사항 - AI 분석 기능")
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
        
        save_btn = PushButton("저장")
        save_btn.setFixedHeight(28)
        save_btn.clicked.connect(self._save_gpt)
        btn_row.addWidget(save_btn)
        
        test_btn = PushButton("테스트")
        test_btn.setFixedHeight(28)
        test_btn.clicked.connect(self._test_gpt)
        btn_row.addWidget(test_btn)
        btn_row.addStretch()
        
        layout.addLayout(btn_row)
        layout.addStretch()
        
        return widget
    
    def _add_line(self, layout):
        """구분선"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: #4a5080;")
        line.setFixedHeight(1)
        layout.addWidget(line)
    
    def _on_exchange_changed(self, index: int):
        """거래소 변경"""
        if index < 0 or index >= len(self.exchange_ids):
            return
        
        self.current_exchange_id = self.exchange_ids[index]
        self._update_ui()
        self._load_credentials()
    
    def _on_testnet_changed(self, checked: bool):
        """테스트넷 변경"""
        ex = SUPPORTED_EXCHANGES.get(self.current_exchange_id, {})
        
        if checked and not ex.get('has_testnet'):
            self.testnet_switch.setChecked(False)
            InfoBar.warning("미지원", f"{ex.get('name')} 테스트넷 미지원", parent=self)
            return
        
        self.is_testnet = checked
        self._update_ui()
        
        separate = ex.get('testnet_separate_api', False)
        if not separate and checked:
            InfoBar.info("메인넷 키 사용", f"{ex.get('name')}은 메인넷 키 공유", parent=self)
        elif separate or not checked:
            self._load_credentials()
    
    def _update_ui(self):
        """UI 업데이트"""
        ex = SUPPORTED_EXCHANGES.get(self.current_exchange_id, {})
        name = ex.get('name', self.current_exchange_id)
        
        mode = " (테스트넷)" if self.is_testnet else ""
        self.api_title.setText(f"{name} API{mode}")
        
        needs_pass = ex.get('requires_passphrase', False)
        self.passphrase_edit.setVisible(needs_pass)
        self.passphrase_label.setVisible(needs_pass)
        
        if self.is_testnet:
            url = ex.get('testnet_url', '')
            self.testnet_label.setText(f"테스트넷 - {url}")
            self.testnet_label.setStyleSheet("color: #f39c12; font-size: 10px;")
        else:
            self.testnet_label.setText("메인넷")
            self.testnet_label.setStyleSheet("color: #27ae60; font-size: 10px;")
    
    def _load_credentials(self):
        """자격증명 로드"""
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
        """저장"""
        api_key = self.api_key_edit.text().strip()
        secret = self.secret_edit.text().strip()
        passphrase = self.passphrase_edit.text().strip()
        
        if not api_key or not secret:
            InfoBar.warning("입력 필요", "API Key/Secret 필수", parent=self)
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
            
            mode = "테스트넷" if (self.is_testnet and separate) else "메인넷"
            InfoBar.success("저장 완료", f"{ex.get('name')} ({mode})", parent=self)
            
        except Exception as e:
            InfoBar.error("저장 실패", str(e), duration=-1, parent=self)
    
    def _test_connection(self):
        """연결 테스트"""
        api_key = self.api_key_edit.text().strip()
        secret = self.secret_edit.text().strip()
        passphrase = self.passphrase_edit.text().strip()
        
        if not api_key or not secret:
            InfoBar.warning("입력 필요", "API Key/Secret 입력", parent=self)
            return
        
        try:
            from api.ccxt_client import CCXTClient
            
            client = CCXTClient(
                self.current_exchange_id, api_key, secret, passphrase, self.is_testnet
            )
            
            success, msg = client.test_connection()
            
            if success:
                InfoBar.success("연동 성공", msg, parent=self)
            else:
                InfoBar.error("연동 실패", msg, duration=-1, parent=self)
                
        except Exception as e:
            InfoBar.error("오류", str(e), duration=-1, parent=self)
    
    def _delete_credentials(self):
        """삭제"""
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
            
            InfoBar.success("삭제 완료", f"{ex.get('name')}", parent=self)
            
        except Exception as e:
            InfoBar.error("삭제 실패", str(e), duration=-1, parent=self)
    
    def _update_status_grid(self):
        """상태 그리드"""
        while self.status_grid.count():
            item = self.status_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        h_ex = BodyLabel("거래소")
        h_ex.setStyleSheet("font-size: 10px; font-weight: bold;")
        h_main = BodyLabel("메인")
        h_main.setStyleSheet("font-size: 10px; font-weight: bold;")
        h_test = BodyLabel("테스트")
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
        """GPT 저장"""
        api_key = self.gpt_api_key_edit.text().strip()
        if not api_key:
            InfoBar.warning("입력 필요", "API Key 필요", parent=self)
            return
        
        try:
            self.credential_manager.save_gpt_credentials(api_key)
            InfoBar.success("저장 완료", "GPT API 저장됨", parent=self)
        except Exception as e:
            InfoBar.error("저장 실패", str(e), duration=-1, parent=self)
    
    def _test_gpt(self):
        """GPT 테스트"""
        api_key = self.gpt_api_key_edit.text().strip()
        if not api_key:
            InfoBar.warning("입력 필요", "API Key 필요", parent=self)
            return
        
        try:
            self.gpt_client.api_key = api_key
            success, msg = self.gpt_client.test_connection()
            
            if success:
                InfoBar.success("연동 성공", msg, parent=self)
            else:
                InfoBar.error("연동 실패", msg, duration=-1, parent=self)
        except Exception as e:
            InfoBar.error("오류", str(e), duration=-1, parent=self)
    
    def _check_config(self):
        """설정 확인"""
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
