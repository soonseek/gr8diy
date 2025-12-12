"""
데이터 페이지
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QScrollArea, 
    QDateEdit, QFrame
)
from PySide6.QtCore import Qt, QDate, QThread
from qfluentwidgets import (
    SubtitleLabel, BodyLabel,
    PushButton, SwitchButton, CheckBox, ProgressBar,
    InfoBar, Pivot, ComboBox, FluentIcon
)
from datetime import datetime

from database.repository import CandlesRepository, ActiveSymbolsRepository
from config.settings import TIMEFRAMES, DATA_RETENTION_DAYS
from config.exchanges import (
    SUPPORTED_EXCHANGES, ALL_EXCHANGE_IDS, DEFAULT_EXCHANGE_ID,
    DEFAULT_SYMBOLS as CCXT_DEFAULT_SYMBOLS
)
from utils.time_helper import time_helper
from utils.logger import logger
from api.exchange_factory import get_public_client
from workers.data_collector import DataCollectorWorker


class DataPage(QWidget):
    """데이터 페이지"""
    
    def __init__(self):
        super().__init__()
        self.candles_repo = CandlesRepository()
        self.symbols_repo = ActiveSymbolsRepository()
        
        self.exchange_ids = ALL_EXCHANGE_IDS.copy()
        self.exchange_id = DEFAULT_EXCHANGE_ID
        self.view_exchange_id = DEFAULT_EXCHANGE_ID
        
        self.symbols_repo.init_default_symbols(self.exchange_id, CCXT_DEFAULT_SYMBOLS)
        
        self.collector_thread = None
        self.collector_worker = None
        
        self._init_ui()
    
    def _init_ui(self):
        """UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        
        self.stack = QStackedWidget()
        
        settings_w = self._create_settings()
        view_w = self._create_view()
        
        self.pivot.addItem("settings", "수집", lambda: self.stack.setCurrentIndex(0), icon=FluentIcon.DOWNLOAD)
        self.pivot.addItem("view", "조회", lambda: self.stack.setCurrentIndex(1), icon=FluentIcon.SEARCH)
        
        self.stack.addWidget(settings_w)
        self.stack.addWidget(view_w)
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack)
        
        self.pivot.setCurrentItem("settings")
    
    def _create_settings(self) -> QWidget:
        """수집 설정"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 거래소
        layout.addWidget(SubtitleLabel("거래소"))
        
        info = BodyLabel(f"{len(ALL_EXCHANGE_IDS)}개 거래소 | 공개 API")
        info.setStyleSheet("color: #27ae60; font-size: 10px;")
        layout.addWidget(info)
        
        self.ex_combo = ComboBox()
        self.ex_combo.setFixedHeight(32)
        for ex_id in self.exchange_ids:
            ex = SUPPORTED_EXCHANGES.get(ex_id, {})
            self.ex_combo.addItem(f"{ex.get('name', ex_id)} (#{ex.get('rank', 999)})")
        try:
            self.ex_combo.setCurrentIndex(self.exchange_ids.index(DEFAULT_EXCHANGE_ID))
        except:
            self.ex_combo.setCurrentIndex(0)
        
        self.ex_combo.currentIndexChanged.connect(self._on_exchange_changed)
        layout.addWidget(self.ex_combo)
        
        self._add_line(layout)
        
        # 날짜
        layout.addWidget(SubtitleLabel("수집 기간"))
        
        date_row = QHBoxLayout()
        date_row.setSpacing(5)
        date_row.addWidget(BodyLabel("시작:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate().addDays(-10))
        self.start_date.setFixedSize(130, 28)
        date_row.addWidget(self.start_date)
        date_row.addStretch()
        layout.addLayout(date_row)
        
        info2 = BodyLabel(f"최대 {DATA_RETENTION_DAYS}일 | TF: 1m/5m/15m/1h/4h/1d")
        info2.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(info2)
        
        # 수집 버튼
        self.collect_btn = PushButton("수집 시작")
        self.collect_btn.setFixedHeight(32)
        self.collect_btn.clicked.connect(self._start_collection)
        layout.addWidget(self.collect_btn)
        
        self.status_label = BodyLabel("")
        self.status_label.setStyleSheet("font-size: 11px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        self.progress = ProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        self._add_line(layout)
        
        # 실시간
        rt_row = QHBoxLayout()
        rt_row.setSpacing(5)
        rt_row.addWidget(SubtitleLabel("실시간 최신화"))
        self.realtime_switch = SwitchButton()
        self.realtime_switch.checkedChanged.connect(self._toggle_realtime)
        rt_row.addWidget(self.realtime_switch)
        rt_row.addStretch()
        layout.addLayout(rt_row)
        
        self._add_line(layout)
        
        # 심볼
        layout.addWidget(SubtitleLabel("활성 심볼"))
        
        self.symbol_checks = {}
        for sym in CCXT_DEFAULT_SYMBOLS:
            cb = CheckBox(sym.split('/')[0])
            cb.setChecked(True)
            cb.stateChanged.connect(lambda s, sy=sym: self._toggle_symbol(sy, s == Qt.Checked))
            self.symbol_checks[sym] = cb
            layout.addWidget(cb)
        
        layout.addStretch()
        
        scroll.setWidget(w)
        return scroll
    
    def _create_view(self) -> QWidget:
        """데이터 조회"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        layout.addWidget(SubtitleLabel("거래소별 데이터"))
        
        self.view_ex_combo = ComboBox()
        self.view_ex_combo.setFixedHeight(32)
        for ex_id in self.exchange_ids:
            ex = SUPPORTED_EXCHANGES.get(ex_id, {})
            self.view_ex_combo.addItem(f"{ex.get('name', ex_id)}")
        try:
            self.view_ex_combo.setCurrentIndex(self.exchange_ids.index(DEFAULT_EXCHANGE_ID))
        except:
            self.view_ex_combo.setCurrentIndex(0)
        
        self.view_ex_combo.currentIndexChanged.connect(self._on_view_exchange_changed)
        layout.addWidget(self.view_ex_combo)
        
        self.current_ex_label = BodyLabel("")
        self.current_ex_label.setStyleSheet("color: #3498db; font-size: 10px;")
        layout.addWidget(self.current_ex_label)
        
        # 테이블
        self.data_table = QTableWidget(0, 4)
        self.data_table.setHorizontalHeaderLabels(["심볼", "TF", "최신 시간", "개수"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setMinimumHeight(500)
        self.data_table.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.data_table)
        
        refresh_btn = PushButton("새로고침")
        refresh_btn.setFixedHeight(28)
        refresh_btn.clicked.connect(self._refresh_table)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        self._refresh_table()
        
        scroll.setWidget(w)
        return scroll
    
    def _add_line(self, layout):
        """구분선"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: #4a5080;")
        line.setFixedHeight(1)
        layout.addWidget(line)
    
    def _on_exchange_changed(self, index: int):
        """수집 거래소 변경"""
        if index < 0 or index >= len(self.exchange_ids):
            return
        
        self.exchange_id = self.exchange_ids[index]
        self.symbols_repo.init_default_symbols(self.exchange_id, CCXT_DEFAULT_SYMBOLS)
    
    def _on_view_exchange_changed(self, index: int):
        """조회 거래소 변경"""
        if index < 0 or index >= len(self.exchange_ids):
            return
        
        self.view_exchange_id = self.exchange_ids[index]
        ex = SUPPORTED_EXCHANGES.get(self.view_exchange_id, {})
        self.current_ex_label.setText(f"현재: {ex.get('name')}")
        self._refresh_table()
    
    def _start_collection(self):
        """수집 시작"""
        try:
            start = self.start_date.date()
            py_date = datetime(start.year(), start.month(), start.day())
            py_date = time_helper.kst.localize(py_date)
            
            max_past = time_helper.days_ago_kst(DATA_RETENTION_DAYS)
            if py_date < max_past:
                InfoBar.warning("날짜 오류", f"최대 {DATA_RETENTION_DAYS}일", parent=self)
                return
            
            active_symbols = self.symbols_repo.get_active_symbols(self.exchange_id)
            if not active_symbols:
                InfoBar.warning("심볼 없음", "최소 1개 활성화", parent=self)
                return
            
            client = get_public_client(self.exchange_id)
            if not client:
                InfoBar.warning("연결 실패", f"{self.exchange_id} 연결 불가", parent=self)
                return
            
            ex = SUPPORTED_EXCHANGES.get(self.exchange_id, {})
            logger.info("Data", f"수집 시작: {ex.get('name')}")
            
            self.collector_thread = QThread()
            self.collector_worker = DataCollectorWorker(self.exchange_id, client)
            self.collector_worker.moveToThread(self.collector_thread)
            
            self.collector_worker.progress_updated.connect(self._on_progress)
            self.collector_worker.collection_completed.connect(self._on_completed)
            self.collector_worker.error_occurred.connect(self._on_error)
            
            self.collector_thread.started.connect(
                lambda: self.collector_worker.backfill_data(active_symbols, py_date, self.exchange_id)
            )
            
            self.collect_btn.setEnabled(False)
            self.collect_btn.setText("수집 중...")
            self.status_label.setVisible(True)
            self.status_label.setText(f"📊 준비 중...")
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            self.collector_thread.start()
            
            InfoBar.info("수집 시작", ex.get('name'), parent=self)
            
        except Exception as e:
            logger.error("Data", f"수집 실패: {e}")
            InfoBar.error("오류", str(e), duration=-1, parent=self)
    
    def _on_progress(self, msg: str, cur: int, total: int):
        """진행률"""
        prog = int((cur / total) * 100) if total > 0 else 0
        self.progress.setValue(prog)
        self.status_label.setText(f"📊 {msg} ({cur}/{total})")
    
    def _on_completed(self):
        """완료"""
        self.collect_btn.setEnabled(True)
        self.collect_btn.setText("수집 시작")
        self.status_label.setVisible(False)
        self.progress.setVisible(False)
        
        if self.collector_thread:
            self.collector_thread.quit()
            self.collector_thread.wait()
        
        InfoBar.success("수집 완료", "", parent=self)
        self._refresh_table()
    
    def _on_error(self, error_msg: str):
        """오류"""
        self.collect_btn.setEnabled(True)
        self.collect_btn.setText("수집 시작")
        self.status_label.setText(f"❌ {error_msg}")
        InfoBar.error("수집 오류", error_msg, duration=-1, parent=self)
    
    def _toggle_realtime(self, checked: bool):
        """실시간"""
        if self.collector_worker:
            self.collector_worker.set_realtime_enabled(checked)
        
        InfoBar.success("설정 변경", "실시간 " + ("활성" if checked else "비활성"), parent=self)
    
    def _toggle_symbol(self, symbol: str, active: bool):
        """심볼 토글"""
        self.symbols_repo.set_symbol_active(self.exchange_id, symbol, active)
    
    def _refresh_table(self):
        """테이블 새로고침"""
        self.data_table.setRowCount(0)
        
        symbols = self.symbols_repo.get_active_symbols(self.view_exchange_id)
        
        row = 0
        for sym in symbols:
            for tf in TIMEFRAMES:
                latest = self.candles_repo.get_latest_timestamp(self.view_exchange_id, sym, tf)
                candles = self.candles_repo.get_candles(self.view_exchange_id, sym, tf, limit=1000)
                
                self.data_table.insertRow(row)
                self.data_table.setItem(row, 0, QTableWidgetItem(sym))
                self.data_table.setItem(row, 1, QTableWidgetItem(tf))
                self.data_table.setItem(row, 2, QTableWidgetItem(latest or "-"))
                self.data_table.setItem(row, 3, QTableWidgetItem(str(len(candles))))
                row += 1
