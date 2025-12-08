"""
봇 조건설정 위젯
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    CardWidget, SubtitleLabel, BodyLabel, ComboBox, SpinBox,
    DoubleSpinBox, SwitchButton, PushButton, CheckBox,
    InfoBar, InfoBarPosition
)

from database.repository import BotConfigsRepository, ActiveSymbolsRepository
from config.settings import BOT_INTERVALS, MAX_LEVERAGE, MAX_MARTINGALE_STEPS
from utils.logger import logger


class BotConditionsWidget(QWidget):
    """봇 조건설정 위젯"""
    
    def __init__(self):
        super().__init__()
        self.bot_configs_repo = BotConfigsRepository()
        self.symbols_repo = ActiveSymbolsRepository()
        
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # 종목 설정 카드
        symbol_card = CardWidget()
        symbol_layout = QVBoxLayout(symbol_card)
        
        symbol_title = SubtitleLabel("종목 설정")
        symbol_layout.addWidget(symbol_title)
        
        symbol_desc = BodyLabel(
            "활성 심볼에 대해 롱/숏/OFF를 선택하고 최대 증거금을 설정하세요."
        )
        symbol_layout.addWidget(symbol_desc)
        
        # 활성 심볼 목록
        active_symbols = self.symbols_repo.get_active_symbols()
        self.symbol_configs = {}
        
        for symbol in active_symbols:
            symbol_row_layout = QHBoxLayout()
            symbol_row_layout.addWidget(BodyLabel(symbol))
            
            direction_combo = ComboBox()
            direction_combo.addItems(["LONG", "SHORT", "OFF"])
            symbol_row_layout.addWidget(direction_combo)
            
            margin_spin = DoubleSpinBox()
            margin_spin.setRange(1, 100000)
            margin_spin.setValue(100)
            margin_spin.setSuffix(" USDT")
            symbol_row_layout.addWidget(margin_spin)
            
            symbol_row_layout.addStretch()
            symbol_layout.addLayout(symbol_row_layout)
            
            self.symbol_configs[symbol] = {
                "direction": direction_combo,
                "margin": margin_spin
            }
        
        layout.addWidget(symbol_card)
        
        # 매매 설정 카드
        trade_card = CardWidget()
        trade_layout = QVBoxLayout(trade_card)
        
        trade_title = SubtitleLabel("매매 설정")
        trade_layout.addWidget(trade_title)
        
        form_layout = QFormLayout()
        
        self.interval_combo = ComboBox()
        self.interval_combo.addItems(BOT_INTERVALS)
        form_layout.addRow("인터벌:", self.interval_combo)
        
        self.margin_mode_combo = ComboBox()
        self.margin_mode_combo.addItems(["isolated (격리)", "cross (교차)"])
        form_layout.addRow("증거금 모드:", self.margin_mode_combo)
        
        self.leverage_spin = SpinBox()
        self.leverage_spin.setRange(1, MAX_LEVERAGE)
        self.leverage_spin.setValue(1)
        form_layout.addRow("레버리지:", self.leverage_spin)
        
        trade_layout.addLayout(form_layout)
        layout.addWidget(trade_card)
        
        # 마틴게일 설정 카드
        martin_card = CardWidget()
        martin_layout = QVBoxLayout(martin_card)
        
        martin_title = SubtitleLabel("추가 매수 (마틴게일)")
        martin_layout.addWidget(martin_title)
        
        switch_layout = QHBoxLayout()
        switch_layout.addWidget(BodyLabel("추가 매수 활성화:"))
        self.martin_switch = SwitchButton()
        self.martin_switch.checkedChanged.connect(self._toggle_martingale)
        switch_layout.addWidget(self.martin_switch)
        switch_layout.addStretch()
        martin_layout.addLayout(switch_layout)
        
        self.martin_form = QFormLayout()
        
        self.martin_steps_spin = SpinBox()
        self.martin_steps_spin.setRange(1, MAX_MARTINGALE_STEPS)
        self.martin_steps_spin.setValue(3)
        self.martin_steps_spin.setEnabled(False)
        self.martin_form.addRow("최대 단계:", self.martin_steps_spin)
        
        self.martin_offset_spin = DoubleSpinBox()
        self.martin_offset_spin.setRange(0.1, 50.0)
        self.martin_offset_spin.setValue(5.0)
        self.martin_offset_spin.setSuffix(" %")
        self.martin_offset_spin.setEnabled(False)
        self.martin_form.addRow("오프셋:", self.martin_offset_spin)
        
        martin_layout.addLayout(self.martin_form)
        
        martin_info = BodyLabel(
            "※ 사이즈 비율은 1, 1, 2, 4, 8, 16, ... 패턴으로 자동 적용됩니다."
        )
        martin_info.setStyleSheet("color: #7f8c8d;")
        martin_layout.addWidget(martin_info)
        
        layout.addWidget(martin_card)
        
        # 익절/손절 설정 카드
        tp_sl_card = CardWidget()
        tp_sl_layout = QVBoxLayout(tp_sl_card)
        
        tp_sl_title = SubtitleLabel("익절 / 손절")
        tp_sl_layout.addWidget(tp_sl_title)
        
        tp_sl_form = QFormLayout()
        
        self.tp_offset_spin = DoubleSpinBox()
        self.tp_offset_spin.setRange(0.1, 100.0)
        self.tp_offset_spin.setValue(3.0)
        self.tp_offset_spin.setSuffix(" %")
        tp_sl_form.addRow("익절 오프셋 (필수):", self.tp_offset_spin)
        
        sl_layout = QHBoxLayout()
        self.sl_enabled_check = CheckBox()
        self.sl_enabled_check.stateChanged.connect(self._toggle_sl)
        sl_layout.addWidget(self.sl_enabled_check)
        
        self.sl_offset_spin = DoubleSpinBox()
        self.sl_offset_spin.setRange(0.1, 100.0)
        self.sl_offset_spin.setValue(5.0)
        self.sl_offset_spin.setSuffix(" %")
        self.sl_offset_spin.setEnabled(False)
        sl_layout.addWidget(self.sl_offset_spin)
        sl_layout.addStretch()
        
        tp_sl_form.addRow("손절 오프셋 (선택):", sl_layout)
        
        tp_sl_layout.addLayout(tp_sl_form)
        
        sl_warning = BodyLabel(
            "⚠ 손절을 설정하지 않으면 큰 손실 위험이 있습니다."
        )
        sl_warning.setStyleSheet("color: #e74c3c;")
        tp_sl_layout.addWidget(sl_warning)
        
        layout.addWidget(tp_sl_card)
        
        # 실행 버튼
        btn_layout = QHBoxLayout()
        
        save_btn = PushButton("설정 저장")
        save_btn.clicked.connect(self._save_config)
        btn_layout.addWidget(save_btn)
        
        self.run_btn = PushButton("봇 실행")
        self.run_btn.clicked.connect(self._run_bot)
        btn_layout.addWidget(self.run_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _toggle_martingale(self, checked: bool):
        """마틴게일 토글"""
        self.martin_steps_spin.setEnabled(checked)
        self.martin_offset_spin.setEnabled(checked)
    
    def _toggle_sl(self, state: int):
        """손절 토글"""
        checked = (state == Qt.Checked)
        self.sl_offset_spin.setEnabled(checked)
        
        if not checked:
            self.sl_offset_spin.setStyleSheet("border: 1px solid #e74c3c;")
        else:
            self.sl_offset_spin.setStyleSheet("")
    
    def _save_config(self):
        """설정 저장"""
        logger.info("Bot", "봇 설정 저장")
        
        # TODO: 실제 DB 저장
        
        InfoBar.success(
            title="저장 완료",
            content="봇 설정이 저장되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _run_bot(self):
        """봇 실행"""
        logger.info("Bot", "봇 실행 시작")
        
        # TODO: 실제 봇 워커 시작
        
        InfoBar.info(
            title="봇 실행",
            content="자동매매 봇이 시작되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
        
        self.run_btn.setEnabled(False)
        self.run_btn.setText("실행 중...")


