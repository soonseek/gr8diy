"""
Bot Conditions Widget
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, ComboBox, SpinBox,
    DoubleSpinBox, SwitchButton, PushButton, CheckBox,
    InfoBar
)

from database.repository import BotConfigsRepository, ActiveSymbolsRepository
from config.settings import BOT_INTERVALS, MAX_LEVERAGE, MAX_MARTINGALE_STEPS, CREDENTIALS_PATH
from config.exchanges import SUPPORTED_EXCHANGES, ALL_EXCHANGE_IDS, DEFAULT_EXCHANGE_ID, DEFAULT_SYMBOLS
from utils.logger import logger
from utils.crypto import CredentialManager
from api.exchange_factory import get_exchange_factory
from workers.trading_bot import TradingBotWorker


class BotConditionsWidget(QWidget):
    """Bot Conditions Widget"""
    
    bot_started = Signal()
    
    def __init__(self):
        super().__init__()
        self.bot_configs_repo = BotConfigsRepository()
        self.symbols_repo = ActiveSymbolsRepository()
        self.credential_manager = CredentialManager(CREDENTIALS_PATH)
        self.exchange_id = DEFAULT_EXCHANGE_ID
        
        self.available_margin = self._get_available_margin()
        
        self.bot_threads = {}
        self.bot_workers = {}
        
        self._init_ui()
        
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._refresh_balance)
        QTimer.singleShot(2000, self._auto_restore_bots)
    
    def _init_ui(self):
        """Initialize UI"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Exchange selection
        layout.addWidget(SubtitleLabel("Exchange Selection"))

        ex_row = QHBoxLayout()
        ex_row.setSpacing(5)
        ex_row.addWidget(BodyLabel("Exchange:"))

        # Only configured exchanges
        self.configured_exchanges = []
        for ex_id in ALL_EXCHANGE_IDS:
            creds = self.credential_manager.get_exchange_credentials(ex_id, is_testnet=False)
            if creds.get('api_key'):
                self.configured_exchanges.append(ex_id)

        self.exchange_combo = ComboBox()
        self.exchange_combo.setFixedHeight(32)

        if not self.configured_exchanges:
            self.exchange_combo.addItem("⚠ No Configured Exchanges")
            self.exchange_combo.setEnabled(False)
        else:
            for ex_id in self.configured_exchanges:
                ex_info = SUPPORTED_EXCHANGES.get(ex_id, {})
                self.exchange_combo.addItem(f"{ex_info.get('name', ex_id)} (#{ex_info.get('rank', 999)})")
            
            last_exchange = self._load_last_exchange()
            if last_exchange and last_exchange in self.configured_exchanges:
                self.exchange_combo.setCurrentIndex(self.configured_exchanges.index(last_exchange))
            else:
                self.exchange_combo.setCurrentIndex(0)
            
            self.exchange_id = self.configured_exchanges[self.exchange_combo.currentIndex()]
        
        self.exchange_combo.currentIndexChanged.connect(self._on_exchange_changed)
        ex_row.addWidget(self.exchange_combo)
        ex_row.addStretch()
        layout.addLayout(ex_row)
        
        self._add_line(layout)

        # Symbol settings
        layout.addWidget(SubtitleLabel("Symbol Settings"))
        
        bal_row = QHBoxLayout()
        bal_row.setSpacing(5)
        
        if self.available_margin > 0:
            self.balance_info = BodyLabel(f"💰 가용: {self.available_margin:.2f} USDT")
            self.balance_info.setStyleSheet("color: #2ecc71; font-size: 11px;")
        else:
            self.balance_info = BodyLabel("⚠ 가용 증거금 조회 불가")
            self.balance_info.setStyleSheet("color: #e74c3c; font-size: 11px;")
        bal_row.addWidget(self.balance_info)
        
        refresh_btn = PushButton("잔고 새로고침")
        refresh_btn.setFixedHeight(28)
        refresh_btn.clicked.connect(self._refresh_balance)
        bal_row.addWidget(refresh_btn)
        bal_row.addStretch()
        layout.addLayout(bal_row)
        
        desc = BodyLabel("활성 심볼에 대해 방향, 증거금, 레버리지를 설정하세요.")
        desc.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(desc)
        
        # 헤더
        header = QHBoxLayout()
        header.setSpacing(5)
        
        h_cb = BodyLabel("")
        h_cb.setFixedWidth(30)
        header.addWidget(h_cb)
        
        h_sym = BodyLabel("심볼")
        h_sym.setFixedWidth(140)
        header.addWidget(h_sym)
        
        h_dir = BodyLabel("방향")
        h_dir.setFixedWidth(120)
        header.addWidget(h_dir)
        
        h_mar = BodyLabel("증거금")
        h_mar.setFixedWidth(160)
        header.addWidget(h_mar)
        
        h_lev = BodyLabel("레버리지")
        h_lev.setFixedWidth(120)
        header.addWidget(h_lev)
        
        header.addStretch()
        layout.addLayout(header)
        
        # 심볼 목록
        # 기본 심볼이 없으면 초기화
        self.symbols_repo.init_default_symbols(self.exchange_id, DEFAULT_SYMBOLS)
        active_symbols = self.symbols_repo.get_active_symbols(self.exchange_id)
        self.symbol_configs = {}
        
        for symbol in active_symbols:
            row = QHBoxLayout()
            row.setSpacing(5)
            
            cb = CheckBox()
            cb.setFixedWidth(30)
            cb.setChecked(symbol == "BTC/USDT:USDT")
            cb.stateChanged.connect(lambda s, sy=symbol: self._on_symbol_check(sy, s))
            row.addWidget(cb)
            
            lbl = BodyLabel(symbol)
            lbl.setFixedWidth(140)
            lbl.setStyleSheet("font-size: 12px;")
            row.addWidget(lbl)
            
            dir_combo = ComboBox()
            dir_combo.addItems(["📈 LONG", "📉 SHORT"])
            dir_combo.setCurrentIndex(0)
            dir_combo.setFixedWidth(120)
            dir_combo.setFixedHeight(28)
            row.addWidget(dir_combo)
            
            margin = DoubleSpinBox()
            margin.setRange(1, 100000)
            margin.setSuffix(" USDT")
            margin.setFixedWidth(160)
            margin.setFixedHeight(32)
            margin.setDecimals(2)
            row.addWidget(margin)
            
            lev = SpinBox()
            lev.setRange(1, MAX_LEVERAGE)
            lev.setValue(10 if "BTC" in symbol or "ETH" in symbol else 5)
            lev.setSuffix("x")
            lev.setFixedWidth(120)
            lev.setFixedHeight(32)
            row.addWidget(lev)
            
            if symbol != "BTC/USDT:USDT":
                dir_combo.setEnabled(False)
                margin.setEnabled(False)
                lev.setEnabled(False)
            
            row.addStretch()
            layout.addLayout(row)
            
            self.symbol_configs[symbol] = {
                "checkbox": cb,
                "direction": dir_combo,
                "margin": margin,
                "leverage": lev
            }
        
        self._redistribute_margin()
        
        self._add_line(layout)
        
        # 매매 설정
        layout.addWidget(SubtitleLabel("매매 설정"))
        
        form1 = QFormLayout()
        form1.setSpacing(3)
        form1.setContentsMargins(0, 0, 0, 0)
        
        self.interval_combo = ComboBox()
        self.interval_combo.addItems(BOT_INTERVALS)
        self.interval_combo.setFixedHeight(28)
        form1.addRow("인터벌:", self.interval_combo)
        
        self.margin_mode_combo = ComboBox()
        self.margin_mode_combo.addItems(["cross (교차)", "isolated (격리)"])
        self.margin_mode_combo.setFixedHeight(28)
        form1.addRow("증거금 모드:", self.margin_mode_combo)
        
        layout.addLayout(form1)
        
        self._add_line(layout)
        
        # 마틴게일
        martin_row = QHBoxLayout()
        martin_row.addWidget(SubtitleLabel("추가 매수 (마틴게일)"))
        self.martin_switch = SwitchButton()
        self.martin_switch.setChecked(True)
        self.martin_switch.checkedChanged.connect(self._toggle_martin)
        martin_row.addWidget(self.martin_switch)
        martin_row.addStretch()
        layout.addLayout(martin_row)
        
        form2 = QFormLayout()
        form2.setSpacing(3)
        form2.setContentsMargins(0, 0, 0, 0)
        
        self.martin_steps_spin = SpinBox()
        self.martin_steps_spin.setRange(1, MAX_MARTINGALE_STEPS)
        self.martin_steps_spin.setValue(3)
        self.martin_steps_spin.setFixedHeight(28)
        form2.addRow("최대 단계:", self.martin_steps_spin)
        
        self.martin_offset_spin = DoubleSpinBox()
        self.martin_offset_spin.setRange(0.1, 50.0)
        self.martin_offset_spin.setValue(5.0)
        self.martin_offset_spin.setSuffix(" %")
        self.martin_offset_spin.setFixedHeight(28)
        self.martin_offset_spin.valueChanged.connect(self._on_martin_offset_changed)
        form2.addRow("오프셋:", self.martin_offset_spin)
        
        layout.addLayout(form2)
        
        martin_info = BodyLabel("※ 사이즈: 1, 1, 2, 4, 8, 16... 자동 적용")
        martin_info.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(martin_info)
        
        self._add_line(layout)
        
        # 익절/손절
        layout.addWidget(SubtitleLabel("익절 / 손절"))
        
        form3 = QFormLayout()
        form3.setSpacing(3)
        form3.setContentsMargins(0, 0, 0, 0)
        
        self.tp_offset_spin = DoubleSpinBox()
        self.tp_offset_spin.setRange(0.1, 100.0)
        self.tp_offset_spin.setValue(1.0)
        self.tp_offset_spin.setSuffix(" %")
        self.tp_offset_spin.setFixedHeight(28)
        form3.addRow("익절:", self.tp_offset_spin)
        
        sl_row = QHBoxLayout()
        sl_row.setSpacing(3)
        self.sl_enabled_check = CheckBox()
        self.sl_enabled_check.stateChanged.connect(self._toggle_sl)
        sl_row.addWidget(self.sl_enabled_check)
        
        self.sl_offset_spin = DoubleSpinBox()
        self.sl_offset_spin.setRange(0.1, 100.0)
        self.sl_offset_spin.setValue(6.0)
        self.sl_offset_spin.setSuffix(" %")
        self.sl_offset_spin.setFixedHeight(28)
        self.sl_offset_spin.setEnabled(False)
        sl_row.addWidget(self.sl_offset_spin)
        sl_row.addStretch()
        
        form3.addRow("손절:", sl_row)
        layout.addLayout(form3)
        
        sl_warn = BodyLabel("⚠ 손절 미설정 시 큰 손실 위험")
        sl_warn.setStyleSheet("color: #e74c3c; font-size: 10px;")
        layout.addWidget(sl_warn)
        
        self._add_line(layout)
        
        # 버튼
        btn_row = QHBoxLayout()
        btn_row.setSpacing(5)
        
        save_btn = PushButton("설정 저장")
        save_btn.setFixedHeight(28)
        save_btn.clicked.connect(self._save_config)
        btn_row.addWidget(save_btn)
        
        self.run_btn = PushButton("🚀 봇 실행")
        self.run_btn.setFixedHeight(40)
        self.run_btn.setStyleSheet("""
            background-color: #00ff9f;
            color: #0a0e27;
            border: none;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
        """)
        self.run_btn.clicked.connect(self._run_bot)
        btn_row.addWidget(self.run_btn)
        btn_row.addStretch()
        
        layout.addLayout(btn_row)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        self._update_sl_minimum()
    
    def _add_line(self, layout):
        """구분선"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: #4a5080;")
        line.setFixedHeight(1)
        layout.addWidget(line)
    
    def _on_exchange_changed(self, index: int):
        """거래소 변경"""
        if not self.configured_exchanges or index < 0 or index >= len(self.configured_exchanges):
            return
        
        self.exchange_id = self.configured_exchanges[index]
        ex = SUPPORTED_EXCHANGES.get(self.exchange_id, {})
        logger.info("Bot", f"거래소 변경: {ex.get('name')} ({self.exchange_id})")
        
        self._save_last_exchange(self.exchange_id)
        self._refresh_balance()
    
    def _load_last_exchange(self) -> str:
        """마지막 선택 거래소"""
        try:
            from pathlib import Path
            from config.settings import DATA_DIR
            last_ex_file = DATA_DIR / "last_bot_exchange.txt"
            if last_ex_file.exists():
                return last_ex_file.read_text().strip()
        except:
            pass
        return ""
    
    def _save_last_exchange(self, exchange_id: str):
        """마지막 선택 저장"""
        try:
            from pathlib import Path
            from config.settings import DATA_DIR
            last_ex_file = DATA_DIR / "last_bot_exchange.txt"
            last_ex_file.write_text(exchange_id)
        except Exception as e:
            logger.warning("Bot", f"거래소 선택 저장 실패: {e}")
    
    def _toggle_martin(self, checked: bool):
        """마틴게일 토글"""
        self.martin_steps_spin.setEnabled(checked)
        self.martin_offset_spin.setEnabled(checked)
        if checked:
            self._update_sl_minimum()
    
    def _on_martin_offset_changed(self, value: float):
        """마틴게일 오프셋 변경"""
        if self.martin_switch.isChecked():
            self._update_sl_minimum()
    
    def _update_sl_minimum(self):
        """손절 최소값"""
        if not self.martin_switch.isChecked():
            self.sl_offset_spin.setMinimum(0.1)
            return
        
        martin_offset = self.martin_offset_spin.value()
        min_sl = martin_offset + 1.0
        self.sl_offset_spin.setMinimum(min_sl)
        if self.sl_offset_spin.value() < min_sl:
            self.sl_offset_spin.setValue(min_sl)
    
    def _toggle_sl(self, state: int):
        """손절 토글"""
        self.sl_offset_spin.setEnabled(state == Qt.Checked)
    
    def _on_symbol_check(self, symbol: str, state: int):
        """심볼 체크"""
        checked = (state == Qt.Checked)
        w = self.symbol_configs[symbol]
        w['direction'].setEnabled(checked)
        w['margin'].setEnabled(checked)
        w['leverage'].setEnabled(checked)
        self._redistribute_margin()
    
    def _redistribute_margin(self):
        """증거금 재분배"""
        active_count = sum(1 for w in self.symbol_configs.values() if w['checkbox'].isChecked())
        if active_count == 0:
            return
        
        margin_per = (self.available_margin / active_count) if self.available_margin > 0 else 100
        margin_per = round(margin_per, 2)
        
        for w in self.symbol_configs.values():
            if w['checkbox'].isChecked():
                w['margin'].setValue(margin_per)
    
    def _save_config(self):
        """저장"""
        try:
            for symbol, w in self.symbol_configs.items():
                if not w['checkbox'].isChecked():
                    continue
                
                direction_text = w['direction'].currentText()
                direction = "LONG" if "LONG" in direction_text else "SHORT"
                
                margin_mode_text = self.margin_mode_combo.currentText()
                margin_mode = "isolated" if "isolated" in margin_mode_text else "cross"
                sl_offset = self.sl_offset_spin.value() if self.sl_enabled_check.isChecked() else None
                
                config = {
                    'exchange_id': self.exchange_id,
                    'symbol': symbol,
                    'direction': direction,
                    'interval': self.interval_combo.currentText(),
                    'max_margin': w['margin'].value(),
                    'margin_mode': margin_mode,
                    'leverage': w['leverage'].value(),
                    'martingale_enabled': 1 if self.martin_switch.isChecked() else 0,
                    'martingale_steps': self.martin_steps_spin.value(),
                    'martingale_offset_pct': self.martin_offset_spin.value(),
                    'tp_offset_pct': self.tp_offset_spin.value(),
                    'sl_offset_pct': sl_offset,
                    'is_active': 0
                }
                
                self.bot_configs_repo.upsert_config(config)
            
            InfoBar.success("저장 완료", "봇 설정 저장됨", parent=self)
            
        except Exception as e:
            InfoBar.error("저장 실패", str(e), duration=-1, parent=self)
    
    def _run_bot(self):
        """봇 실행"""
        try:
            if not self._validate_settings():
                return
            
            factory = get_exchange_factory()
            ccxt_client = factory.get_client(self.exchange_id)
            if not ccxt_client:
                InfoBar.error("연결 실패", f"{self.exchange_id} 클라이언트 생성 실패", duration=-1, parent=self)
                return
            
            self._save_config()
            
            # 선택된 심볼들 확인
            selected_symbols = [sym for sym, w in self.symbol_configs.items() if w['checkbox'].isChecked()]
            
            if not selected_symbols:
                InfoBar.warning("심볼 선택 필요", "최소 1개 심볼 체크", parent=self)
                return
            
            # 기존 포지션 확인
            for symbol in selected_symbols:
                positions = ccxt_client.get_positions(symbol)
                if positions:
                    for pos in positions:
                        if pos.get('size', 0) > 0 and (pos.get('entry_price', 0) > 0 or pos.get('mark_price', 0) > 0):
                            InfoBar.error("포지션 존재", f"{symbol}에 이미 포지션이 있습니다", duration=-1, parent=self)
                            return
            
            started_count = 0
            for symbol in selected_symbols:
                config = self.bot_configs_repo.get_config(self.exchange_id, symbol)
                if not config:
                    logger.warning("Bot", f"{symbol} 설정 없음")
                    continue
                
                config['exchange_id'] = self.exchange_id
                
                bot_thread = QThread()
                bot_worker = TradingBotWorker(ccxt_client, config)
                bot_worker.moveToThread(bot_thread)
                
                bot_worker.position_opened.connect(self._on_position_opened)
                bot_worker.order_placed.connect(self._on_order_placed)
                bot_worker.error_occurred.connect(self._on_bot_error)
                bot_worker.bot_stopped.connect(self._on_bot_stopped)
                bot_worker.existing_position_found.connect(self._on_existing_position)
                bot_worker.position_closed.connect(self._on_position_closed)
                
                bot_thread.started.connect(bot_worker.start_trading)
                
                self.bot_threads[symbol] = bot_thread
                self.bot_workers[symbol] = bot_worker
                
                bot_thread.start()
                self.bot_configs_repo.set_active(self.exchange_id, symbol, True)
                started_count += 1
            
            if started_count > 0:
                InfoBar.success("봇 실행", f"{started_count}개 심볼 시작", parent=self)
                # 버튼은 활성화 상태 유지 (계속 생성 가능)
                self.bot_started.emit()  # 모니터링으로 전환
            else:
                InfoBar.warning("실행 불가", "설정을 확인해주세요", parent=self)
                
        except Exception as e:
            InfoBar.error("실행 실패", str(e), duration=-1, parent=self)
            self._reset_run_button()
    
    def _on_position_opened(self, symbol: str, side: str, size: float):
        """포지션 진입"""
        InfoBar.success("포지션 진입", f"{symbol} {side} {size}", parent=self)
    
    def _on_order_placed(self, symbol: str, order_type: str, side: str, price: float):
        """주문 체결"""
        logger.info("Bot", f"{symbol} {order_type}: {side} @ {price}")
    
    def _on_bot_error(self, symbol: str, error_msg: str):
        """봇 에러"""
        InfoBar.error(f"{symbol} 오류", error_msg, duration=-1, parent=self)
        
        if symbol in self.bot_threads:
            self.bot_threads[symbol].quit()
            self.bot_threads[symbol].wait()
            del self.bot_threads[symbol]
            del self.bot_workers[symbol]
        
        if len(self.bot_threads) == 0:
            self._reset_run_button()
    
    def _validate_settings(self) -> bool:
        """설정 검증"""
        if self.martin_switch.isChecked() and self.sl_enabled_check.isChecked():
            martin_offset = self.martin_offset_spin.value()
            sl_offset = self.sl_offset_spin.value()
            if sl_offset < martin_offset + 1.0:
                InfoBar.error("설정 오류", f"손절 >= 추가매수+1% 필요", duration=-1, parent=self)
                return False
        
        total_margin = 0
        active_symbols = []
        for symbol, w in self.symbol_configs.items():
            if w['checkbox'].isChecked():
                total_margin += w['margin'].value()
                active_symbols.append(symbol)
        
        if total_margin > self.available_margin and self.available_margin > 0:
            InfoBar.error("증거금 부족", f"할당({total_margin:.2f}) > 가용({self.available_margin:.2f})", duration=-1, parent=self)
            return False
        
        if len(active_symbols) == 0:
            InfoBar.warning("실행 불가", "심볼 선택 필요", parent=self)
            return False
        
        return True
    
    def _on_existing_position(self, symbol: str, message: str):
        """기존 포지션"""
        InfoBar.warning(f"{symbol}", message, parent=self)
    
    def _on_position_closed(self, symbol: str, pnl: float):
        """포지션 청산"""
        pnl_str = f"+{pnl:.2f}" if pnl >= 0 else f"{pnl:.2f}"
        InfoBar.success(f"{symbol} 청산", f"PNL: {pnl_str} USDT", parent=self)
    
    def _on_bot_stopped(self, symbol: str):
        """봇 종료"""
        self.bot_configs_repo.set_active(self.exchange_id, symbol, False)
        
        if symbol in self.bot_threads:
            self.bot_threads[symbol].quit()
            self.bot_threads[symbol].wait()
            del self.bot_threads[symbol]
            del self.bot_workers[symbol]
        
        if len(self.bot_threads) == 0:
            self._reset_run_button()
    
    def _reset_run_button(self):
        """버튼 리셋"""
        self.run_btn.setEnabled(True)
        self.run_btn.setText("🚀 봇 실행")
    
    def _auto_restore_bots(self):
        """봇 자동 복원"""
        try:
            logger.info("Bot", f"=== 기존 봇 자동 복원 시작 (거래소: {self.exchange_id}) ===")
            
            factory = get_exchange_factory()
            logger.info("Bot", f"ExchangeFactory 획득 완료")
            
            ccxt_client = factory.get_client(self.exchange_id)
            logger.info("Bot", f"CCXT 클라이언트: {ccxt_client is not None}")
            
            if not ccxt_client:
                logger.warning("Bot", f"{self.exchange_id} 미연동 - 자동 복원 건너뜀")
                return
            
            # 모든 봇 설정을 가져옴 (is_active와 관계없이)
            from database.repository import BaseRepository
            repo = BaseRepository()
            sql = "SELECT * FROM bot_configs WHERE exchange_id = ?"
            all_configs = repo.fetch_all(sql, (self.exchange_id,))
            logger.info("Bot", f"봇 설정 조회: {len(all_configs) if all_configs else 0}개")
            
            if not all_configs:
                logger.info("Bot", "봇 설정 없음 - 복원 종료")
                return
            
            # 먼저 모든 봇을 비활성화 (안전)
            logger.info("Bot", f"{len(all_configs)}개 봇 설정 발견 - 포지션 확인 중...")
            
            restored_count = 0
            for config in all_configs:
                symbol = config['symbol']
                
                # 일단 비활성화
                self.bot_configs_repo.set_active(self.exchange_id, symbol, False)
                
                # 포지션 확인
                positions = ccxt_client.get_positions(symbol)
                has_position = False
                actual_size = 0
                
                logger.info("Bot", f"{symbol} 포지션 조회 결과: {len(positions) if positions else 0}개")
                
                if positions:
                    for pos in positions:
                        size = pos.get('size', 0)
                        entry_price = pos.get('entry_price', 0)
                        mark_price = pos.get('mark_price', 0)
                        logger.info("Bot", f"{symbol} 포지션 - 크기: {size}, 진입가: {entry_price}, 현재가: {mark_price}")
                        # 크기 > 0이고 (진입가 또는 현재가)가 있으면 실제 포지션
                        if size > 0 and (entry_price > 0 or mark_price > 0):
                            has_position = True
                            actual_size = size
                            break
                
                if not has_position:
                    logger.info("Bot", f"{symbol} 포지션 없음 - 복원 건너뜀")
                    continue
                
                logger.info("Bot", f"{symbol} 포지션 {actual_size} 발견 - 봇 복원 시작")
                
                config['exchange_id'] = self.exchange_id
                
                bot_thread = QThread()
                bot_worker = TradingBotWorker(ccxt_client, config)
                bot_worker.moveToThread(bot_thread)
                
                bot_worker.auto_restart = True
                bot_worker.is_running = True
                
                bot_worker.position_opened.connect(self._on_position_opened)
                bot_worker.order_placed.connect(self._on_order_placed)
                bot_worker.error_occurred.connect(self._on_bot_error)
                bot_worker.bot_stopped.connect(self._on_bot_stopped)
                bot_worker.existing_position_found.connect(self._on_existing_position)
                bot_worker.position_closed.connect(self._on_position_closed)
                
                bot_thread.started.connect(bot_worker._monitoring_loop)
                
                self.bot_threads[symbol] = bot_thread
                self.bot_workers[symbol] = bot_worker
                
                bot_thread.start()
                restored_count += 1
            
            if restored_count > 0:
                InfoBar.success("봇 복원", f"{restored_count}개 봇 복원됨", parent=self)
                self.run_btn.setEnabled(False)
                self.run_btn.setText("실행 중...")
                
        except Exception as e:
            logger.error("Bot", f"봇 자동 복원 실패: {str(e)}")
    
    def _refresh_balance(self):
        """잔고 새로고침"""
        self.available_margin = self._get_available_margin()
        
        if self.available_margin > 0:
            self.balance_info.setText(f"💰 가용: {self.available_margin:.2f} USDT")
            self.balance_info.setStyleSheet("color: #2ecc71; font-size: 11px;")
            InfoBar.success("잔고 조회", f"{self.available_margin:.2f} USDT", parent=self)
            self._redistribute_margin()
        else:
            self.balance_info.setText("⚠ 가용 증거금 조회 불가")
            self.balance_info.setStyleSheet("color: #e74c3c; font-size: 11px;")
            InfoBar.error("잔고 조회 실패", "API 연동 확인", duration=-1, parent=self)
    
    def _get_available_margin(self) -> float:
        """가용 증거금 조회"""
        try:
            factory = get_exchange_factory()
            ccxt_client = factory.get_client(self.exchange_id)
            if not ccxt_client:
                return 0.0
            
            return ccxt_client.get_usdt_balance()
            
        except Exception:
            return 0.0
