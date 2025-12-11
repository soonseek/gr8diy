"""
설정 페이지
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    Pivot, LineEdit, PasswordLineEdit, 
    PushButton, InfoBar, InfoBarPosition, CardWidget,
    TitleLabel, SubtitleLabel, BodyLabel
)

from api.okx_client import OKXClient
from api.gpt_client import GPTClient
from utils.crypto import CredentialManager
from config.settings import CREDENTIALS_PATH
from utils.logger import logger


class SettingsPage(QWidget):
    """설정 페이지 (기본 연동 + 거래소 설정)"""
    
    def __init__(self):
        super().__init__()
        self.credential_manager = CredentialManager(CREDENTIALS_PATH)
        self.okx_client = None
        self.gpt_client = GPTClient()
        
        self._init_ui()
        self._load_credentials()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 10, 10)
        
        # 타이틀
        title = TitleLabel("설정")
        layout.addWidget(title)
        
        # Pivot (탭) - 좌측 정렬
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        
        self.stack_widget = QStackedWidget(self)
        
        # 기본 연동 탭
        self.credentials_widget = self._create_credentials_widget()
        
        # 거래소 설정 탭
        self.exchange_widget = self._create_exchange_widget()
        
        # Pivot 아이템 추가
        self.pivot.addItem(
            routeKey="credentials",
            text="기본 연동",
            onClick=lambda: self.stack_widget.setCurrentIndex(0)
        )
        self.pivot.addItem(
            routeKey="exchange",
            text="거래소 설정",
            onClick=lambda: self.stack_widget.setCurrentIndex(1)
        )
        
        # 스택 위젯에 추가
        self.stack_widget.addWidget(self.credentials_widget)
        self.stack_widget.addWidget(self.exchange_widget)
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack_widget)
        layout.addStretch()
        
        # 기본 탭 선택
        self.pivot.setCurrentItem("credentials")
    
    def _create_credentials_widget(self) -> QWidget:
        """기본 연동 위젯"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # OKX 카드
        okx_card = CardWidget()
        okx_layout = QVBoxLayout(okx_card)
        
        okx_title = SubtitleLabel("OKX API 연동")
        okx_layout.addWidget(okx_title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.okx_api_key_edit = LineEdit()
        self.okx_api_key_edit.setPlaceholderText("API Key")
        form_layout.addRow("API Key:", self.okx_api_key_edit)
        
        self.okx_secret_edit = PasswordLineEdit()
        self.okx_secret_edit.setPlaceholderText("Secret")
        form_layout.addRow("Secret:", self.okx_secret_edit)
        
        self.okx_passphrase_edit = PasswordLineEdit()
        self.okx_passphrase_edit.setPlaceholderText("Passphrase")
        form_layout.addRow("Passphrase:", self.okx_passphrase_edit)
        
        okx_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        save_okx_btn = PushButton("저장")
        save_okx_btn.clicked.connect(self._save_okx_credentials)
        btn_layout.addWidget(save_okx_btn)
        
        test_okx_btn = PushButton("연동 테스트")
        test_okx_btn.clicked.connect(self._test_okx_connection)
        btn_layout.addWidget(test_okx_btn)
        btn_layout.addStretch()
        
        okx_layout.addLayout(btn_layout)
        
        layout.addWidget(okx_card)
        
        # GPT 카드
        gpt_card = CardWidget()
        gpt_layout = QVBoxLayout(gpt_card)
        
        gpt_title = SubtitleLabel("GPT API 연동")
        gpt_layout.addWidget(gpt_title)
        
        gpt_form = QFormLayout()
        gpt_form.setSpacing(10)
        
        self.gpt_api_key_edit = PasswordLineEdit()
        self.gpt_api_key_edit.setPlaceholderText("API Key")
        gpt_form.addRow("API Key:", self.gpt_api_key_edit)
        
        gpt_layout.addLayout(gpt_form)
        
        gpt_btn_layout = QHBoxLayout()
        save_gpt_btn = PushButton("저장")
        save_gpt_btn.clicked.connect(self._save_gpt_credentials)
        gpt_btn_layout.addWidget(save_gpt_btn)
        
        test_gpt_btn = PushButton("연동 테스트")
        test_gpt_btn.clicked.connect(self._test_gpt_connection)
        gpt_btn_layout.addWidget(test_gpt_btn)
        gpt_btn_layout.addStretch()
        
        gpt_layout.addLayout(gpt_btn_layout)
        
        layout.addWidget(gpt_card)
        layout.addStretch()
        
        return widget
    
    def _create_exchange_widget(self) -> QWidget:
        """거래소 설정 위젯"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 안내 카드
        guide_card = CardWidget()
        guide_layout = QVBoxLayout(guide_card)
        
        guide_title = SubtitleLabel("OKX 계정 설정 가이드")
        guide_layout.addWidget(guide_title)
        
        guide_text = BodyLabel(
            "봇을 사용하기 위해서는 다음 설정이 필요합니다:\n\n"
            "• Account mode = 2, 3, 또는 4 (선물 거래 모드)\n"
            "  - 2: Single-currency margin\n"
            "  - 3: Multi-currency margin\n"
            "  - 4: Portfolio margin\n"
            "• Position mode = Hedge mode (long_short_mode)\n\n"
            "아래 버튼으로 현재 설정을 확인하고 필요 시 자동 변경할 수 있습니다."
        )
        guide_layout.addWidget(guide_text)
        
        layout.addWidget(guide_card)
        
        # 설정 확인 카드
        check_card = CardWidget()
        check_layout = QVBoxLayout(check_card)
        
        check_title = SubtitleLabel("설정 상태 확인")
        check_layout.addWidget(check_title)
        
        self.account_mode_label = BodyLabel("Account Mode: 확인 필요")
        check_layout.addWidget(self.account_mode_label)
        
        self.position_mode_label = BodyLabel("Position Mode: 확인 필요")
        check_layout.addWidget(self.position_mode_label)
        
        btn_layout = QHBoxLayout()
        
        check_btn = PushButton("설정 상태 확인")
        check_btn.clicked.connect(self._check_account_config)
        btn_layout.addWidget(check_btn)
        
        self.auto_fix_btn = PushButton("자동 변경 시도")
        self.auto_fix_btn.setEnabled(False)
        self.auto_fix_btn.clicked.connect(self._auto_fix_settings)
        btn_layout.addWidget(self.auto_fix_btn)
        
        btn_layout.addStretch()
        
        check_layout.addLayout(btn_layout)
        
        layout.addWidget(check_card)
        layout.addStretch()
        
        return widget
    
    def _load_credentials(self):
        """자격증명 로드"""
        okx_creds = self.credential_manager.get_okx_credentials()
        self.okx_api_key_edit.setText(okx_creds.get('api_key', ''))
        self.okx_secret_edit.setText(okx_creds.get('secret', ''))
        self.okx_passphrase_edit.setText(okx_creds.get('passphrase', ''))
        
        gpt_creds = self.credential_manager.get_gpt_credentials()
        self.gpt_api_key_edit.setText(gpt_creds.get('api_key', ''))
    
    def _save_okx_credentials(self):
        """OKX 자격증명 저장"""
        api_key = self.okx_api_key_edit.text().strip()
        secret = self.okx_secret_edit.text().strip()
        passphrase = self.okx_passphrase_edit.text().strip()
        
        if not all([api_key, secret, passphrase]):
            InfoBar.warning(
                title="입력 오류",
                content="모든 필드를 입력해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        self.credential_manager.update_okx_credentials(api_key, secret, passphrase)
        logger.info("Settings", "OKX 자격증명 저장 완료")
        
        InfoBar.success(
            title="저장 완료",
            content="OKX API 자격증명이 저장되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _save_gpt_credentials(self):
        """GPT 자격증명 저장"""
        api_key = self.gpt_api_key_edit.text().strip()
        
        if not api_key:
            InfoBar.warning(
                title="입력 오류",
                content="API Key를 입력해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        self.credential_manager.update_gpt_credentials(api_key)
        logger.info("Settings", "GPT 자격증명 저장 완료")
        
        InfoBar.success(
            title="저장 완료",
            content="GPT API 자격증명이 저장되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _test_okx_connection(self):
        """OKX 연결 테스트"""
        creds = self.credential_manager.get_okx_credentials()
        
        if not all(creds.values()):
            InfoBar.warning(
                title="자격증명 없음",
                content="먼저 OKX API 자격증명을 저장해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        client = OKXClient(
            creds['api_key'],
            creds['secret'],
            creds['passphrase']
        )
        
        success, message = client.test_connection()
        
        if success:
            InfoBar.success(
                title="연동 성공",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            self.okx_client = client
        else:
            InfoBar.error(
                title="연동 실패",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def _test_gpt_connection(self):
        """GPT 연결 테스트"""
        creds = self.credential_manager.get_gpt_credentials()
        
        if not creds.get('api_key'):
            InfoBar.warning(
                title="자격증명 없음",
                content="먼저 GPT API 자격증명을 저장해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        self.gpt_client.set_api_key(creds['api_key'])
        success, message = self.gpt_client.test_connection()
        
        if success:
            InfoBar.success(
                title="연동 성공",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
        else:
            InfoBar.error(
                title="연동 실패",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def _check_account_config(self):
        """계정 설정 확인"""
        if not self.okx_client:
            InfoBar.warning(
                title="OKX 미연동",
                content="먼저 OKX API 연동을 완료해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        config = self.okx_client.get_account_config()
        
        if not config:
            InfoBar.error(
                title="조회 실패",
                content="계정 설정 조회에 실패했습니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        acct_lv = config.get('acctLv')
        pos_mode = config.get('posMode')
        
        self.account_mode_label.setText(f"Account Mode: {acct_lv}")
        self.position_mode_label.setText(f"Position Mode: {pos_mode}")
        
        # 권장 설정과 비교
        need_fix = False
        if acct_lv not in ["2", "3", "4"]:  # 선물 거래 가능 모드
            self.account_mode_label.setStyleSheet("color: #e74c3c;")
            need_fix = True
        else:
            self.account_mode_label.setStyleSheet("color: #2ecc71;")
        
        if pos_mode != "long_short_mode":
            self.position_mode_label.setStyleSheet("color: #e74c3c;")
            need_fix = True
        else:
            self.position_mode_label.setStyleSheet("color: #2ecc71;")
        
        self.auto_fix_btn.setEnabled(need_fix)
        
        if not need_fix:
            InfoBar.success(
                title="설정 확인 완료",
                content="모든 설정이 권장 값으로 설정되어 있습니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def _auto_fix_settings(self):
        """설정 자동 변경"""
        if not self.okx_client:
            return
        
        # Account mode 변경 (Single-currency margin mode)
        success1 = self.okx_client.set_account_mode(acct_lv=2)
        
        # Position mode 변경 (hedge mode)
        success2 = self.okx_client.set_position_mode(pos_mode="long_short_mode")
        
        if success1 and success2:
            InfoBar.success(
                title="변경 완료",
                content="계정 설정이 권장 값으로 변경되었습니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            # 재확인
            self._check_account_config()
        else:
            InfoBar.error(
                title="변경 실패",
                content="설정 변경에 실패했습니다. 로그를 확인해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )


