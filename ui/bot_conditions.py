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

from PySide6.QtCore import QThread
from database.repository import BotConfigsRepository, ActiveSymbolsRepository
from config.settings import BOT_INTERVALS, MAX_LEVERAGE, MAX_MARTINGALE_STEPS, CREDENTIALS_PATH
from utils.logger import logger
from utils.crypto import CredentialManager
from api.okx_client import OKXClient
from workers.trading_bot import TradingBotWorker


class BotConditionsWidget(QWidget):
    """봇 조건설정 위젯"""
    
    def __init__(self):
        super().__init__()
        self.bot_configs_repo = BotConfigsRepository()
        self.symbols_repo = ActiveSymbolsRepository()
        self.credential_manager = CredentialManager(CREDENTIALS_PATH)
        
        # 가용 증거금 계산
        self.available_margin = self._get_available_margin()
        
        # 봇 워커 관리
        self.bot_threads = {}
        self.bot_workers = {}
        
        self._init_ui()
        
        # 프로그램 시작 시 기존 봇 자동 복원
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self._auto_restore_bots)  # 2초 후 자동 복원
    
    def _init_ui(self):
        """UI 초기화"""
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
        
        # 종목 설정 카드
        symbol_card = CardWidget()
        symbol_layout = QVBoxLayout(symbol_card)
        
        symbol_title = SubtitleLabel("종목 설정")
        symbol_layout.addWidget(symbol_title)
        
        # 가용 증거금 표시
        balance_layout = QHBoxLayout()
        
        if self.available_margin > 0:
            self.balance_info = BodyLabel(
                f"💰 계정 가용 증거금: {self.available_margin:.2f} USDT\n"
                f"📊 심볼당 권장 증거금: {self.available_margin / 5:.2f} USDT (5개 균등 분배)"
            )
            self.balance_info.setWordWrap(True)
            self.balance_info.setStyleSheet("color: #2ecc71; font-weight: bold;")
            balance_layout.addWidget(self.balance_info)
        else:
            self.balance_info = BodyLabel("⚠ 가용 증거금을 조회할 수 없습니다")
            self.balance_info.setWordWrap(True)
            self.balance_info.setStyleSheet("color: #e74c3c;")
            balance_layout.addWidget(self.balance_info)
        
        # 새로고침 버튼
        refresh_balance_btn = PushButton("잔고 새로고침")
        refresh_balance_btn.clicked.connect(self._refresh_balance)
        balance_layout.addWidget(refresh_balance_btn)
        balance_layout.addStretch()
        
        symbol_layout.addLayout(balance_layout)
        
        symbol_desc = BodyLabel(
            "활성 심볼에 대해 방향, 증거금, 레버리지를 설정하세요."
        )
        symbol_layout.addWidget(symbol_desc)
        
        # 헤더 행
        header_layout = QHBoxLayout()
        header_layout.addWidget(BodyLabel(""))  # 체크박스 공간
        
        header_symbol = BodyLabel("심볼")
        header_symbol.setFixedWidth(150)
        header_layout.addWidget(header_symbol)
        
        header_direction = BodyLabel("방향")
        header_direction.setFixedWidth(100)
        header_layout.addWidget(header_direction)
        
        header_margin = BodyLabel("증거금")
        header_margin.setMinimumWidth(180)
        header_layout.addWidget(header_margin)
        
        header_leverage = BodyLabel("레버리지")
        header_leverage.setMinimumWidth(120)
        header_layout.addWidget(header_leverage)
        
        header_layout.addStretch()
        symbol_layout.addLayout(header_layout)
        
        # 활성 심볼 목록
        active_symbols = self.symbols_repo.get_active_symbols()
        self.symbol_configs = {}
        
        for symbol in active_symbols:
            symbol_row_layout = QHBoxLayout()
            
            # 체크박스
            checkbox = CheckBox()
            if symbol == "BTC-USDT-SWAP":
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(
                lambda state, s=symbol: self._on_symbol_checkbox_changed(s, state)
            )
            symbol_row_layout.addWidget(checkbox)
            
            # 심볼명
            symbol_label = BodyLabel(symbol)
            symbol_label.setFixedWidth(150)
            symbol_row_layout.addWidget(symbol_label)
            
            # 방향
            direction_combo = ComboBox()
            direction_combo.addItems(["LONG", "SHORT"])
            direction_combo.setFixedWidth(100)
            symbol_row_layout.addWidget(direction_combo)
            
            # 증거금
            margin_spin = DoubleSpinBox()
            margin_spin.setRange(1, 100000)
            margin_spin.setSuffix(" USDT")
            margin_spin.setMinimumWidth(180)
            margin_spin.setDecimals(2)
            symbol_row_layout.addWidget(margin_spin)
            
            # 레버리지 (심볼별)
            leverage_spin = SpinBox()
            leverage_spin.setRange(1, MAX_LEVERAGE)
            # 심볼별 기본 레버리지
            if "BTC" in symbol or "ETH" in symbol:
                leverage_spin.setValue(10)  # BTC, ETH: 10배
            else:
                leverage_spin.setValue(5)   # 나머지: 5배
            leverage_spin.setSuffix("x")
            leverage_spin.setMinimumWidth(120)
            symbol_row_layout.addWidget(leverage_spin)
            
            # 기본적으로 비활성화 (체크된 것만 활성화)
            if symbol != "BTC-USDT-SWAP":
                direction_combo.setEnabled(False)
                margin_spin.setEnabled(False)
                leverage_spin.setEnabled(False)
            
            symbol_row_layout.addStretch()
            symbol_layout.addLayout(symbol_row_layout)
            
            self.symbol_configs[symbol] = {
                "checkbox": checkbox,
                "direction": direction_combo,
                "margin": margin_spin,
                "leverage": leverage_spin
            }
        
        # 초기 증거금 분배
        self._redistribute_margin()
        
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
        self.margin_mode_combo.addItems(["cross (교차)", "isolated (격리)"])
        self.margin_mode_combo.setCurrentIndex(0)  # cross가 기본
        form_layout.addRow("증거금 모드:", self.margin_mode_combo)
        
        info_label = BodyLabel("※ 레버리지는 각 심볼별로 위에서 설정합니다.")
        info_label.setStyleSheet("color: #7f8c8d;")
        trade_layout.addWidget(info_label)
        
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
        self.martin_switch.setChecked(True)  # 기본 활성화
        self.martin_switch.checkedChanged.connect(self._toggle_martingale)
        switch_layout.addWidget(self.martin_switch)
        switch_layout.addStretch()
        martin_layout.addLayout(switch_layout)
        
        self.martin_form = QFormLayout()
        
        self.martin_steps_spin = SpinBox()
        self.martin_steps_spin.setRange(1, MAX_MARTINGALE_STEPS)
        self.martin_steps_spin.setValue(3)
        self.martin_steps_spin.setEnabled(True)  # 기본 활성화
        self.martin_form.addRow("최대 단계:", self.martin_steps_spin)
        
        self.martin_offset_spin = DoubleSpinBox()
        self.martin_offset_spin.setRange(0.1, 50.0)
        self.martin_offset_spin.setValue(5.0)
        self.martin_offset_spin.setSuffix(" %")
        self.martin_offset_spin.setEnabled(True)  # 기본 활성화
        self.martin_offset_spin.valueChanged.connect(self._on_martin_offset_changed)
        self.martin_form.addRow("오프셋:", self.martin_offset_spin)
        
        martin_layout.addLayout(self.martin_form)
        
        martin_info = BodyLabel(
            "※ 사이즈 비율은 1, 1, 2, 4, 8, 16, ... 패턴으로 자동 적용됩니다."
        )
        martin_info.setStyleSheet("color: #7f8c8d;")
        martin_layout.addWidget(martin_info)
        
        # 익절/레버리지 관계 설명
        leverage_info = BodyLabel(
            "💡 익절 계산 공식: 실제 익절 PnL(%) = 오프셋(%) × 레버리지\n"
            "   예) 오프셋 1% + 레버리지 10배 = PnL 약 10% 부근에서 익절\n"
            "   예) 오프셋 2% + 레버리지 5배 = PnL 약 10% 부근에서 익절"
        )
        leverage_info.setStyleSheet("color: #00d4ff; font-size: 12px;")
        martin_layout.addWidget(leverage_info)
        
        layout.addWidget(martin_card)
        
        # 익절/손절 설정 카드
        tp_sl_card = CardWidget()
        tp_sl_layout = QVBoxLayout(tp_sl_card)
        
        tp_sl_title = SubtitleLabel("익절 / 손절")
        tp_sl_layout.addWidget(tp_sl_title)
        
        tp_sl_form = QFormLayout()
        
        self.tp_offset_spin = DoubleSpinBox()
        self.tp_offset_spin.setRange(0.1, 100.0)
        self.tp_offset_spin.setValue(1.0)  # 기본값 1%
        self.tp_offset_spin.setSuffix(" %")
        tp_sl_form.addRow("익절 오프셋 (필수):", self.tp_offset_spin)
        
        sl_layout = QHBoxLayout()
        self.sl_enabled_check = CheckBox()
        self.sl_enabled_check.stateChanged.connect(self._toggle_sl)
        sl_layout.addWidget(self.sl_enabled_check)
        
        self.sl_offset_spin = DoubleSpinBox()
        self.sl_offset_spin.setRange(0.1, 100.0)
        self.sl_offset_spin.setValue(6.0)  # 기본값: 마틴 5% + 1%
        self.sl_offset_spin.setSuffix(" %")
        self.sl_offset_spin.setEnabled(False)
        sl_layout.addWidget(self.sl_offset_spin)
        sl_layout.addStretch()
        
        tp_sl_form.addRow("손절 오프셋 (선택):", sl_layout)
        
        tp_sl_layout.addLayout(tp_sl_form)
        
        sl_warning = BodyLabel(
            "⚠ 손절을 설정하지 않으면 큰 손실 위험이 있습니다.\n"
            "💡 추가매수 활성화 시: 손절은 추가매수 오프셋 + 1% 이상이어야 합니다."
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
        
        # 초기화 시 손절 최소값 업데이트 (마틴게일 기본 활성화)
        self._update_sl_minimum()
    
    def _toggle_martingale(self, checked: bool):
        """마틴게일 토글"""
        self.martin_steps_spin.setEnabled(checked)
        self.martin_offset_spin.setEnabled(checked)
        
        # 마틴게일 활성화 시 손절 최소값 업데이트
        if checked:
            self._update_sl_minimum()
    
    def _on_martin_offset_changed(self, value: float):
        """마틴게일 오프셋 변경 시"""
        if self.martin_switch.isChecked():
            self._update_sl_minimum()
    
    def _update_sl_minimum(self):
        """손절 최소값 업데이트"""
        if not self.martin_switch.isChecked():
            # 마틴게일 비활성화 시 원래대로
            self.sl_offset_spin.setMinimum(0.1)
            return
        
        martin_offset = self.martin_offset_spin.value()
        min_sl_offset = martin_offset + 1.0  # 최소 1% 차이
        
        # 손절 최소값 설정
        self.sl_offset_spin.setMinimum(min_sl_offset)
        
        # 현재 손절 값이 최소값보다 작으면 자동 조정
        if self.sl_offset_spin.value() < min_sl_offset:
            self.sl_offset_spin.setValue(min_sl_offset)
        
        logger.debug("Bot", f"손절 최소값 업데이트: {min_sl_offset}% (마틴 {martin_offset}% + 1%)")
    
    def _toggle_sl(self, state: int):
        """손절 토글"""
        checked = (state == Qt.Checked)
        self.sl_offset_spin.setEnabled(checked)
        
        # 체크되지 않았을 때 경고 표시만 (입력란은 비활성화)
        # 빨간색 보더는 제거 (혼란 방지)
        self.sl_offset_spin.setStyleSheet("")
    
    def _on_symbol_checkbox_changed(self, symbol: str, state: int):
        """심볼 체크박스 변경"""
        checked = (state == Qt.Checked)
        
        # 위젯 활성화/비활성화
        widgets = self.symbol_configs[symbol]
        widgets['direction'].setEnabled(checked)
        widgets['margin'].setEnabled(checked)
        widgets['leverage'].setEnabled(checked)
        
        # 증거금 재분배
        self._redistribute_margin()
        
        logger.info("Bot", f"{symbol} {'활성화' if checked else '비활성화'}")
    
    def _redistribute_margin(self):
        """활성화된 심볼에 증거금 균등 분배"""
        # 활성화된 심볼 수 카운트
        active_count = sum(
            1 for widgets in self.symbol_configs.values() 
            if widgets['checkbox'].isChecked()
        )
        
        if active_count == 0:
            return
        
        # 균등 분배 계산
        margin_per_symbol = (self.available_margin / active_count) if self.available_margin > 0 else 100
        margin_per_symbol = round(margin_per_symbol, 2)
        
        # 활성화된 심볼에만 적용
        for widgets in self.symbol_configs.values():
            if widgets['checkbox'].isChecked():
                widgets['margin'].setValue(margin_per_symbol)
        
        logger.info("Bot", f"증거금 재분배: {active_count}개 심볼 × {margin_per_symbol} USDT")
    
    def _save_config(self):
        """설정 저장"""
        try:
            logger.info("Bot", "봇 설정 저장 시작")
            
            # 각 심볼별 설정 저장
            for symbol, widgets in self.symbol_configs.items():
                # 체크되지 않은 심볼은 건너뛰기
                if not widgets['checkbox'].isChecked():
                    continue
                
                direction = widgets['direction'].currentText()
                
                margin = widgets['margin'].value()
                leverage = widgets['leverage'].value()
                
                # 마진모드 처리
                margin_mode_text = self.margin_mode_combo.currentText()
                margin_mode = "isolated" if "isolated" in margin_mode_text else "cross"
                
                # 손절 오프셋 처리
                sl_offset = self.sl_offset_spin.value() if self.sl_enabled_check.isChecked() else None
                
                config = {
                    'symbol': symbol,
                    'direction': direction,
                    'interval': self.interval_combo.currentText(),
                    'max_margin': margin,
                    'margin_mode': margin_mode,
                    'leverage': leverage,
                    'martingale_enabled': 1 if self.martin_switch.isChecked() else 0,
                    'martingale_steps': self.martin_steps_spin.value(),
                    'martingale_offset_pct': self.martin_offset_spin.value(),
                    'tp_offset_pct': self.tp_offset_spin.value(),
                    'sl_offset_pct': sl_offset,
                    'is_active': 0
                }
                
                self.bot_configs_repo.upsert_config(config)
                logger.info("Bot", f"{symbol} 설정 저장 완료")
            
            InfoBar.success(
                title="저장 완료",
                content="봇 설정이 저장되었습니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            
        except Exception as e:
            import traceback
            error_msg = f"설정 저장 실패: {str(e)}"
            logger.error("Bot", error_msg, traceback.format_exc())
            InfoBar.error(
                title="저장 실패",
                content=error_msg,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def _run_bot(self):
        """봇 실행"""
        try:
            logger.info("Bot", "봇 실행 시작")
            
            # 설정 검증
            if not self._validate_settings():
                self._reset_run_button()  # 검증 실패 시 버튼 복원
                return
            
            # OKX 클라이언트 생성
            creds = self.credential_manager.get_okx_credentials()
            if not all(creds.values()):
                InfoBar.warning(
                    title="OKX 미연동",
                    content="먼저 설정에서 OKX API 자격증명을 저장해주세요.",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                self._reset_run_button()  # 연동 실패 시 버튼 복원
                return
            
            okx_client = OKXClient(
                creds['api_key'],
                creds['secret'],
                creds['passphrase']
            )
            
            # 먼저 설정 저장
            self._save_config()
            
            # 각 심볼별 봇 시작
            started_count = 0
            for symbol, widgets in self.symbol_configs.items():
                # 체크되지 않은 심볼은 건너뛰기
                if not widgets['checkbox'].isChecked():
                    continue
                
                direction = widgets['direction'].currentText()
                
                # 설정 가져오기
                config = self.bot_configs_repo.get_config(symbol)
                if not config:
                    logger.warning("Bot", f"{symbol} 설정을 찾을 수 없습니다")
                    continue
                
                # 봇 워커 생성
                bot_thread = QThread()
                bot_worker = TradingBotWorker(okx_client, config)
                bot_worker.moveToThread(bot_thread)
                
                # 시그널 연결
                bot_worker.position_opened.connect(self._on_position_opened)
                bot_worker.order_placed.connect(self._on_order_placed)
                bot_worker.error_occurred.connect(self._on_bot_error)
                bot_worker.bot_stopped.connect(self._on_bot_stopped)
                bot_worker.existing_position_found.connect(self._on_existing_position)
                bot_worker.position_closed.connect(self._on_position_closed)
                
                # 스레드 시작 시 봇 실행
                bot_thread.started.connect(bot_worker.start_trading)
                
                # 저장
                self.bot_threads[symbol] = bot_thread
                self.bot_workers[symbol] = bot_worker
                
                # 스레드 시작
                bot_thread.start()
                
                # DB에 활성화 상태 저장
                self.bot_configs_repo.set_active(symbol, True)
                
                logger.info("Bot", f"{symbol} 봇 시작됨")
                started_count += 1
            
            if started_count > 0:
                InfoBar.success(
                    title="봇 실행",
                    content=f"{started_count}개 심볼에 대한 자동매매가 시작되었습니다.",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                self.run_btn.setEnabled(False)
                self.run_btn.setText("실행 중...")
            else:
                InfoBar.warning(
                    title="실행 불가",
                    content="실행할 봇이 없습니다. 체크박스로 심볼을 선택해주세요.",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                self._reset_run_button()  # 실행할 봇 없으면 버튼 복원
                
        except Exception as e:
            import traceback
            error_msg = f"봇 실행 실패: {str(e)}"
            logger.error("Bot", error_msg, traceback.format_exc())
            InfoBar.error(
                title="실행 실패",
                content=error_msg,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            self._reset_run_button()  # 예외 발생 시 버튼 복원
    
    def _on_position_opened(self, symbol: str, side: str, size: float):
        """포지션 진입 완료"""
        logger.info("Bot", f"{symbol} 포지션 진입: {side} {size}")
        InfoBar.success(
            title="포지션 진입",
            content=f"{symbol} {side} {size} 진입 완료",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _on_order_placed(self, symbol: str, order_type: str, side: str, price: float):
        """주문 체결"""
        logger.info("Bot", f"{symbol} {order_type} 주문: {side} @ {price}")
    
    def _on_bot_error(self, symbol: str, error_msg: str):
        """봇 에러"""
        logger.error("Bot", f"{symbol} 에러: {error_msg}")
        
        InfoBar.error(
            title=f"{symbol} 오류",
            content=error_msg,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
        
        # 해당 봇 스레드 정리
        if symbol in self.bot_threads:
            self.bot_threads[symbol].quit()
            self.bot_threads[symbol].wait()
            del self.bot_threads[symbol]
            del self.bot_workers[symbol]
        
        # 모든 봇이 종료되면 버튼 활성화
        if len(self.bot_threads) == 0:
            self._reset_run_button()
    
    def _validate_settings(self) -> bool:
        """설정 검증"""
        # 1. 마틴게일 활성화 시 손절 오프셋 검증
        if self.martin_switch.isChecked() and self.sl_enabled_check.isChecked():
            martin_offset = self.martin_offset_spin.value()
            sl_offset = self.sl_offset_spin.value()
            min_sl_offset = martin_offset + 1.0
            
            if sl_offset < min_sl_offset:
                InfoBar.error(
                    title="설정 오류",
                    content=f"손절 오프셋은 추가매수 오프셋보다 최소 1% 이상 커야 합니다.\n"
                            f"현재: 손절 {sl_offset}%, 추가매수 {martin_offset}%\n"
                            f"최소 필요: {min_sl_offset}%",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=10000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return False
        
        # 2. 증거금 합계 검증
        total_margin = 0
        active_symbols = []
        for symbol, widgets in self.symbol_configs.items():
            if widgets['checkbox'].isChecked():
                margin = widgets['margin'].value()
                total_margin += margin
                active_symbols.append(symbol)
        
        if total_margin > self.available_margin and self.available_margin > 0:
            InfoBar.error(
                title="증거금 부족",
                content=f"할당된 증거금 합계({total_margin:.2f} USDT)가 "
                        f"가용 잔고({self.available_margin:.2f} USDT)를 초과합니다.\n\n"
                        f"활성 심볼 수를 줄이거나 증거금을 조정해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                duration=15000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return False
        
        # 3. 활성 심볼 확인
        if len(active_symbols) == 0:
            InfoBar.warning(
                title="실행 불가",
                content="체크박스로 최소 1개 이상의 심볼을 선택해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return False
        
        logger.info("Bot", f"설정 검증 완료: {len(active_symbols)}개 심볼, "
                           f"증거금 합계 {total_margin:.2f} USDT")
        
        return True
    
    def _on_existing_position(self, symbol: str, message: str):
        """기존 포지션 발견"""
        logger.warning("Bot", f"{symbol} {message}")
        InfoBar.warning(
            title=f"{symbol} 기존 포지션 정리",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            duration=10000,  # 10초간 표시
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _on_position_closed(self, symbol: str, pnl: float):
        """포지션 청산 (TP/SL 체결)"""
        pnl_str = f"+{pnl:.2f}" if pnl >= 0 else f"{pnl:.2f}"
        logger.info("Bot", f"{symbol} 포지션 청산: PNL {pnl_str} USDT")
        
        InfoBar.success(
            title=f"{symbol} 포지션 청산",
            content=f"익절/손절 체결 - PNL: {pnl_str} USDT\n자동 재실행 모드",
            orient=Qt.Horizontal,
            isClosable=True,
            duration=5000,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _on_bot_stopped(self, symbol: str):
        """봇 종료"""
        logger.info("Bot", f"{symbol} 봇 종료됨")
        
        # DB에 비활성화 상태 저장
        self.bot_configs_repo.set_active(symbol, False)
        
        # 스레드 정리
        if symbol in self.bot_threads:
            self.bot_threads[symbol].quit()
            self.bot_threads[symbol].wait()
            del self.bot_threads[symbol]
            del self.bot_workers[symbol]
        
        # 모든 봇이 종료되면 버튼 활성화
        if len(self.bot_threads) == 0:
            self._reset_run_button()
    
    def _reset_run_button(self):
        """봇 실행 버튼 초기화"""
        self.run_btn.setEnabled(True)
        self.run_btn.setText("봇 실행")
    
    def _auto_restore_bots(self):
        """기존 봇 자동 복원"""
        try:
            logger.info("Bot", "기존 봇 자동 복원 시작...")
            
            # OKX 클라이언트 생성
            creds = self.credential_manager.get_okx_credentials()
            if not all(creds.values()):
                logger.warning("Bot", "OKX 미연동 - 자동 복원 건너뜀")
                return
            
            okx_client = OKXClient(
                creds['api_key'],
                creds['secret'],
                creds['passphrase']
            )
            
            # 활성화된 봇 설정 조회
            active_configs = self.bot_configs_repo.get_active_configs()
            
            if not active_configs:
                logger.info("Bot", "활성화된 봇 설정 없음")
                return
            
            # 각 설정별로 포지션 확인 및 복원
            restored_count = 0
            for config in active_configs:
                symbol = config['symbol']
                
                # OKX에서 실제 포지션 확인
                positions = okx_client.get_positions(symbol)
                has_position = False
                
                if positions:
                    for pos in positions:
                        if abs(float(pos.get('pos', 0))) > 0:
                            has_position = True
                            break
                
                if not has_position:
                    logger.info("Bot", f"{symbol} 포지션 없음 - 봇 설정만 유지")
                    # 포지션 없으면 봇 비활성화
                    self.bot_configs_repo.set_active(symbol, False)
                    continue
                
                # 포지션이 있으면 봇 복원
                logger.info("Bot", f"{symbol} 포지션 발견 - 봇 복원 중")
                
                # 봇 워커 생성 (모니터링 모드)
                bot_thread = QThread()
                bot_worker = TradingBotWorker(okx_client, config)
                bot_worker.moveToThread(bot_thread)
                
                # 복원 모드 설정
                bot_worker.auto_restart = True
                bot_worker.is_running = True
                
                # 시그널 연결
                bot_worker.position_opened.connect(self._on_position_opened)
                bot_worker.order_placed.connect(self._on_order_placed)
                bot_worker.error_occurred.connect(self._on_bot_error)
                bot_worker.bot_stopped.connect(self._on_bot_stopped)
                bot_worker.existing_position_found.connect(self._on_existing_position)
                bot_worker.position_closed.connect(self._on_position_closed)
                
                # 모니터링만 시작 (새로 진입하지 않음)
                bot_thread.started.connect(bot_worker._monitoring_loop)
                
                # 저장
                self.bot_threads[symbol] = bot_thread
                self.bot_workers[symbol] = bot_worker
                
                # 스레드 시작
                bot_thread.start()
                
                logger.info("Bot", f"{symbol} 봇 복원 완료 (모니터링 모드)")
                restored_count += 1
            
            if restored_count > 0:
                InfoBar.success(
                    title="봇 자동 복원",
                    content=f"{restored_count}개 봇이 자동으로 복원되었습니다.\n"
                            f"기존 포지션 모니터링을 계속합니다.",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=10000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                self.run_btn.setEnabled(False)
                self.run_btn.setText("실행 중...")
                
                logger.info("Bot", f"총 {restored_count}개 봇 복원 완료")
            
        except Exception as e:
            import traceback
            logger.error("Bot", f"봇 자동 복원 실패: {str(e)}", traceback.format_exc())
    
    def _refresh_balance(self):
        """잔고 새로고침"""
        logger.info("Bot", "잔고 새로고침 중...")
        
        self.available_margin = self._get_available_margin()
        
        if self.available_margin > 0:
            self.balance_info.setText(
                f"💰 계정 가용 증거금: {self.available_margin:.2f} USDT\n"
                f"📊 심볼당 권장 증거금: {self.available_margin / 5:.2f} USDT (5개 균등 분배)"
            )
            self.balance_info.setStyleSheet("color: #2ecc71; font-weight: bold;")
            
            InfoBar.success(
                title="잔고 조회 완료",
                content=f"가용 증거금: {self.available_margin:.2f} USDT",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            
            # 증거금 재분배
            self._redistribute_margin()
        else:
            self.balance_info.setText("⚠ 가용 증거금을 조회할 수 없습니다")
            self.balance_info.setStyleSheet("color: #e74c3c;")
            
            InfoBar.error(
                title="잔고 조회 실패",
                content="OKX API 연동을 확인해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def _get_available_margin(self) -> float:
        """OKX 계정 가용 증거금 조회"""
        try:
            creds = self.credential_manager.get_okx_credentials()
            if not all(creds.values()):
                logger.warning("Bot", "OKX 자격증명이 없어 가용 증거금을 조회할 수 없습니다")
                return 0.0
            
            okx_client = OKXClient(
                creds['api_key'],
                creds['secret'],
                creds['passphrase']
            )
            
            # 계정 잔고 조회
            balance = okx_client.get_balance()
            if not balance:
                logger.warning("Bot", "계정 잔고 조회 실패")
                return 0.0
            
            # USDT 가용 잔고 찾기
            for asset in balance:
                if asset.get('ccy') == 'USDT':
                    available = float(asset.get('availBal', 0))
                    logger.info("Bot", f"USDT 가용 잔고: {available:.2f}")
                    return available
            
            logger.warning("Bot", "USDT 잔고를 찾을 수 없습니다")
            return 0.0
            
        except Exception as e:
            import traceback
            logger.error("Bot", f"가용 증거금 조회 실패: {str(e)}", traceback.format_exc())
            return 0.0


