"""
Data Page
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QScrollArea,
    QDateEdit, QFrame, QDialog, QPushButton, QTextEdit, QLabel
)
from PySide6.QtCore import Qt, QDate, QThread, QTimer
from qfluentwidgets import (
    SubtitleLabel, BodyLabel,
    PushButton, SwitchButton, CheckBox, ProgressBar,
    InfoBar, Pivot, ComboBox, FluentIcon
)
from datetime import datetime

from database.repository import CandlesRepository, ActiveSymbolsRepository, BaseRepository, IndicatorsRepository
from config.settings import TIMEFRAMES, DATA_RETENTION_DAYS
from config.exchanges import (
    SUPPORTED_EXCHANGES, ALL_EXCHANGE_IDS, DEFAULT_EXCHANGE_ID,
    DEFAULT_SYMBOLS as CCXT_DEFAULT_SYMBOLS
)
from utils.time_helper import time_helper
from utils.logger import logger
from api.exchange_factory import get_public_client
from workers.data_collector import DataCollectorWorker
# from ui.chart_widget import CandlestickChartWidget  # Temporarily disabled due to PyQtGraph segfault


class DataPage(QWidget):
    """Data Page"""
    
    def __init__(self):
        super().__init__()
        self.candles_repo = CandlesRepository()
        self.symbols_repo = ActiveSymbolsRepository()
        self.indicators_repo = IndicatorsRepository()
        
        self.exchange_ids = ALL_EXCHANGE_IDS.copy()
        self.exchange_id = DEFAULT_EXCHANGE_ID
        self.view_exchange_id = DEFAULT_EXCHANGE_ID
        
        self.symbols_repo.init_default_symbols(self.exchange_id, CCXT_DEFAULT_SYMBOLS)
        
        self.collector_thread = None
        self.collector_worker = None

        # Timer for UI update throttling
        self.progress_update_timer = QTimer()
        self.progress_update_timer.setSingleShot(True)
        self.progress_update_timer.timeout.connect(self._delayed_progress_update)
        self.pending_progress = None
        self.last_progress_log_time = 0

        self._init_ui()

    def _init_ui(self):
        """Initialize UI"""
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
        
        self.pivot.addItem("settings", "Collection", lambda: self.stack.setCurrentIndex(0), icon=FluentIcon.DOWNLOAD)
        self.pivot.addItem("view", "View", lambda: self.stack.setCurrentIndex(1), icon=FluentIcon.SEARCH)
        
        self.stack.addWidget(settings_w)
        self.stack.addWidget(view_w)
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack)
        
        self.pivot.setCurrentItem("settings")
    
    def _create_settings(self) -> QWidget:
        """Collection Settings"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Exchange
        layout.addWidget(SubtitleLabel("Exchange"))

        info = BodyLabel(f"{len(ALL_EXCHANGE_IDS)} exchanges | Public API")
        info.setStyleSheet("color: #27ae60; font-size: 10px;")
        layout.addWidget(info)
        
        self.ex_combo = ComboBox()
        self.ex_combo.setFixedHeight(32)
        self.ex_combo.setMinimumWidth(300)
        self.ex_combo.setMaximumWidth(400)

        # 드롭다운 스타일 적용
        from ui.theme import get_custom_stylesheet
        self.ex_combo.setStyleSheet(get_custom_stylesheet())

        # 너비 제한을 위한 추가 스타일
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
        current_style = self.ex_combo.styleSheet()
        self.ex_combo.setStyleSheet(current_style + width_style)

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
        self.start_date.setDate(QDate.currentDate().addDays(-365))  # 1년으로 변경
        self.start_date.setFixedSize(130, 28)
        date_row.addWidget(self.start_date)
        date_row.addStretch()
        layout.addLayout(date_row)
        
        info2 = BodyLabel(f"전체 기간 수집 가능 | TF: 1m/5m/15m/1h/4h/1d")
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
        self.view_ex_combo.setMinimumWidth(300)
        self.view_ex_combo.setMaximumWidth(400)

        # 드롭다운 스타일 적용
        from ui.theme import get_custom_stylesheet
        self.view_ex_combo.setStyleSheet(get_custom_stylesheet())

        # 너비 제한을 위한 추가 스타일
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
        current_style = self.view_ex_combo.styleSheet()
        self.view_ex_combo.setStyleSheet(current_style + width_style)

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

        # 타임프레임 필터
        tf_layout = QHBoxLayout()
        tf_layout.addWidget(BodyLabel("타임프레임 필터:"))

        self.tf_filters = {}
        for tf in TIMEFRAMES:
            cb = CheckBox(tf)
            if tf == "1m":  # 1분봉 기본 선택
                cb.setChecked(True)
            else:
                cb.setChecked(False)
            cb.stateChanged.connect(lambda state, t=tf: self._on_timeframe_filter_changed(t, state == Qt.Checked))
            self.tf_filters[tf] = cb
            tf_layout.addWidget(cb)

        # 전체 선택/해제 버튼
        select_all_btn = PushButton("전체 선택")
        select_all_btn.setFixedHeight(28)
        select_all_btn.clicked.connect(self._select_all_timeframes)
        tf_layout.addWidget(select_all_btn)

        clear_all_btn = PushButton("전체 해제")
        clear_all_btn.setFixedHeight(28)
        clear_all_btn.clicked.connect(self._clear_all_timeframes)
        tf_layout.addWidget(clear_all_btn)

        tf_layout.addStretch()
        layout.addLayout(tf_layout)

        # 차트
        # self.main_chart_widget = CandlestickChartWidget()  # Temporarily disabled due to PyQtGraph segfault
        from PySide6.QtWidgets import QLabel
        self.main_chart_widget = QLabel("차트 기능이 일시적으로 비활성화되었습니다.\n\nPyQtGraph 충돌 문제를 해결 중입니다.")
        self.main_chart_widget.setAlignment(Qt.AlignCenter)
        self.main_chart_widget.setStyleSheet("color: #e0e0e0; padding: 20px;")
        self.main_chart_widget.setMinimumHeight(300)
        self.main_chart_widget.setMaximumHeight(400)

        # 동적 데이터 로딩 콜백 설정 - 일시적으로 비활성화
        # self.main_chart_widget.set_data_loader_callback(self._load_additional_chart_data)
        print("[DEBUG] Chart data loader callback temporarily disabled")

        layout.addWidget(self.main_chart_widget)

    def _select_all_timeframes(self):
        """모든 타임프레임 선택"""
        for cb in self.tf_filters.values():
            cb.setChecked(True)
        self._refresh_table()

    def _clear_all_timeframes(self):
        """모든 타임프레임 해제"""
        for cb in self.tf_filters.values():
            cb.setChecked(False)
        self._refresh_table()

        # 테이블
        self.data_table = QTableWidget(0, 4)
        self.data_table.setHorizontalHeaderLabels(["심볼", "TF", "최신 시간", "개수"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setMinimumHeight(500)
        self.data_table.setStyleSheet("""
            font-size: 12px;
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #4a5080;
            }
            QTableWidget::item:hover {
                background: rgba(0, 255, 159, 0.1);
            }
            QTableWidget::item:selected {
                background: rgba(0, 255, 159, 0.2);
                border: 1px solid #00ff9f;
            }
        """)
        # 테이블 항목 클릭 시 상세 데이터 보기
        self.data_table.itemDoubleClicked.connect(self._show_detailed_data)
        self.data_table.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.data_table)
        
        btn_layout = QHBoxLayout()

        refresh_btn = PushButton("새로고침")
        refresh_btn.setFixedHeight(28)
        refresh_btn.clicked.connect(self._refresh_table)
        btn_layout.addWidget(refresh_btn)

        # 상세 데이터 보기 안내
        info_label = QLabel("※ 더블클릭하여 실제 데이터 확인")
        info_label.setStyleSheet("color: #00d4ff; font-size: 11px; margin-left: 10px;")
        btn_layout.addWidget(info_label)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        layout.addStretch()

        # 초기 1분봉만 보이도록 필터 설정
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
            print("="*60)
            print("[DEBUG] 데이터 수집 버튼 클릭!")
            print(f"[DEBUG] 버튼 상태: enabled={self.collect_btn.isEnabled()}")
            print(f"[DEBUG] 버튼 텍스트: '{self.collect_btn.text()}'")
            print("="*60)

            start = self.start_date.date()
            py_date = datetime(start.year(), start.month(), start.day())
            py_date = time_helper.kst.localize(py_date)

            print(f"[DEBUG] 선택된 시작 날짜: {py_date}")
            print(f"[DEBUG] 현재 거래소 ID: {self.exchange_id}")

            # 날짜 제한 없음 - 가장 과거 데이터부터 수집 가능

            active_symbols = self.symbols_repo.get_active_symbols(self.exchange_id)
            print(f"[DEBUG] 활성화된 심볼 수: {len(active_symbols)}")
            print(f"[DEBUG] 활성화된 심볼: {active_symbols}")

            if not active_symbols:
                print("[DEBUG] 활성화된 심볼이 없어 수집을 중단합니다")
                InfoBar.warning("심볼 없음", "최소 1개 활성화", parent=self)
                return

            # 기존 데이터 확인
            total_existing = 0
            for symbol in active_symbols[:3]:  # 처음 3개 심볼만 확인 (속도)
                for tf in TIMEFRAMES[:2]:  # 2개 타임프레임만 확인
                    count = len(self.candles_repo.get_candles(self.exchange_id, symbol, tf, limit=1))
                    total_existing += count
                    if count > 0:
                        latest = self.candles_repo.get_latest_timestamp(self.exchange_id, symbol, tf)
                        logger.info("Data", f"기존 데이터: {symbol} {tf} {count}개 (최신: {latest})")
                        print(f"[DEBUG] 기존 데이터 확인: {symbol} {tf} {count}개 (최신: {latest})")

            print(f"[DEBUG] 기존 데이터 총 개수: {total_existing}")

            if total_existing > 0:
                InfoBar.warning(
                    "기존 데이터 발견",
                    f"총 {total_existing}개 데이터가 있습니다. 최신 데이터부터 수집합니다.",
                    parent=self, duration=3000
                )

            print(f"[DEBUG] 거래소 클라이언트 생성 시도: {self.exchange_id}")
            client = get_public_client(self.exchange_id)
            if not client:
                print(f"[DEBUG] 클라이언트 생성 실패: {self.exchange_id}")
                InfoBar.warning("연결 실패", f"{self.exchange_id} 연결 불가", parent=self)
                return

            print(f"[DEBUG] 클라이언트 생성 성공: {type(client)}")

            ex = SUPPORTED_EXCHANGES.get(self.exchange_id, {})
            logger.info("Data", f"수집 시작: {ex.get('name')}")
            print(f"[DEBUG] 수집 시작: {ex.get('name')} ({self.exchange_id})")

            # 워커 스레드 설정
            print("[DEBUG] 워커 스레드 설정 시작...")
            self.collector_thread = QThread()
            self.collector_worker = DataCollectorWorker(self.exchange_id, client)
            self.collector_worker.moveToThread(self.collector_thread)

            # 시그널 연결
            print("[DEBUG] 시그널 연결...")
            self.collector_worker.progress_updated.connect(self._on_progress)
            self.collector_worker.collection_completed.connect(self._on_completed)
            self.collector_worker.error_occurred.connect(self._on_error)

            # 스레드 시작 시 워커 실행
            print("[DEBUG] 스레드 시작 연결 설정...")
            self.collector_thread.started.connect(
                lambda: self._start_worker_backfill(active_symbols, py_date, self.exchange_id)
            )

            # UI 상태 변경
            print("[DEBUG] UI 상태 변경...")
            self.collect_btn.setEnabled(False)
            self.collect_btn.setText("수집 중...")
            self.status_label.setVisible(True)
            self.status_label.setText(f"📊 준비 중...")
            self.progress.setVisible(True)
            self.progress.setValue(0)

            print("[DEBUG] 스레드 시작...")
            self.collector_thread.start()

            InfoBar.info("수집 시작", ex.get('name'), parent=self)
            print("[DEBUG] 데이터 수집 시작 완료")

        except Exception as e:
            import traceback
            error_msg = f"수집 실패: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] 상세 에러: {traceback.format_exc()}")
            logger.error("Data", error_msg)
            InfoBar.error("오류", str(e), duration=-1, parent=self)

    def _start_worker_backfill(self, active_symbols, py_date, exchange_id):
        """워커 백필 시작 (별도 메서드로 분리하여 디버깅)"""
        try:
            print(f"[DEBUG] 워커 백필 시작: {exchange_id}, {len(active_symbols)}개 심볼")
            self.collector_worker.backfill_data(active_symbols, py_date, exchange_id)
        except Exception as e:
            import traceback
            error_msg = f"워커 백필 실패: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] 상세 에러: {traceback.format_exc()}")
            self.error_occurred.emit(error_msg)
    
    def _on_progress(self, msg: str, cur: int, total: int):
        """진행률 (쓰로틀링 적용)"""
        print(f"[DEBUG] 진행률 업데이트: {msg} ({cur}/{total})")

        # UI 업데이트를 타이머로 지연시켜 과도한 업데이트 방지
        self.pending_progress = (msg, cur, total)

        # 100ms 이내의 업데이트는 지연
        if not self.progress_update_timer.isActive():
            self.progress_update_timer.start(100)

        # 로그는 1초에 한번만 출력
        import time
        current_time = time.time()
        if current_time - self.last_progress_log_time > 1.0:
            from utils.logger import logger
            logger.info("DataCollection", f"{msg} ({cur}/{total})")
            print(f"[DEBUG] 1초 주기 로그: {msg} ({cur}/{total})")
            self.last_progress_log_time = current_time

    def _delayed_progress_update(self):
        """지연된 진행률 업데이트"""
        if self.pending_progress:
            msg, cur, total = self.pending_progress
            prog = int((cur / total) * 100) if total > 0 else 0
            self.progress.setValue(prog)
            self.status_label.setText(f"📊 {msg} ({cur}/{total})")
            self.pending_progress = None
    
    def _on_completed(self):
        """완료"""
        print("="*60)
        print("[DEBUG] 데이터 수집 완료!")
        print("="*60)

        self.collect_btn.setEnabled(True)
        self.collect_btn.setText("수집 시작")
        self.status_label.setVisible(False)
        self.progress.setVisible(False)

        if self.collector_thread:
            print("[DEBUG] 워커 스레드 정리...")
            self.collector_thread.quit()
            self.collector_thread.wait()
            print("[DEBUG] 워커 스레드 정리 완료")

        InfoBar.success("수집 완료", "", parent=self)
        print("[DEBUG] 테이블 새로고침...")
        self._refresh_table()
        print("[DEBUG] 수집 완료 처리 끝")

    def _on_error(self, error_msg: str):
        """오류"""
        print("="*60)
        print(f"[ERROR] 데이터 수집 오류: {error_msg}")
        print("="*60)

        self.collect_btn.setEnabled(True)
        self.collect_btn.setText("수집 시작")
        self.status_label.setText(f"❌ {error_msg}")
        self.status_label.setVisible(True)
        InfoBar.error("수집 오류", error_msg, duration=-1, parent=self)
    
    def _toggle_realtime(self, checked: bool):
        """실시간"""
        if self.collector_worker:
            self.collector_worker.set_realtime_enabled(checked)
        
        InfoBar.success("설정 변경", "실시간 " + ("활성" if checked else "비활성"), parent=self)
    
    def _toggle_symbol(self, symbol: str, active: bool):
        """심볼 토글"""
        self.symbols_repo.set_symbol_active(self.exchange_id, symbol, active)
    
    def _get_active_timeframes(self):
        """활성화된 타임프레임 목록 반환"""
        return [tf for tf, cb in self.tf_filters.items() if cb.isChecked()]

    def _on_timeframe_filter_changed(self, timeframe: str, checked: bool):
        """타임프레임 필터 변경 시 테이블 새로고침"""
        self._refresh_table()

    def _refresh_table(self):
        """테이블 새로고침"""
        self.data_table.setRowCount(0)

        symbols = self.symbols_repo.get_active_symbols(self.view_exchange_id)
        active_timeframes = self._get_active_timeframes()

        row = 0
        from config.settings import TIMEFRAMES
        for sym in symbols:
            for tf in active_timeframes:  # 필터링된 타임프레임만 표시
                latest = self.candles_repo.get_latest_timestamp(self.view_exchange_id, sym, tf)

                # 실제 개수를 먼저 조회 (쿼리 개수 제한 없음)
                base_repo = BaseRepository()
                sql = """
                SELECT COUNT(*) as count FROM candles
                WHERE exchange_id = ? AND symbol = ? AND timeframe = ?
                """
                result = base_repo.fetch_one(sql, (self.view_exchange_id, sym, tf))
                actual_count = result['count'] if result else 0

                # 데이터 조회 (최대 999999개)
                candles = self.candles_repo.get_candles(self.view_exchange_id, sym, tf, limit=999999)

                self.data_table.insertRow(row)
                self.data_table.setItem(row, 0, QTableWidgetItem(sym))
                self.data_table.setItem(row, 1, QTableWidgetItem(tf))
                self.data_table.setItem(row, 2, QTableWidgetItem(latest or "-"))
                self.data_table.setItem(row, 3, QTableWidgetItem(str(actual_count)))
                row += 1

    def _show_detailed_data(self, item):
        """테이블 항목 더블클릭 시 상세 데이터 보기"""
        row = item.row()
        symbol = self.data_table.item(row, 0).text()
        timeframe = self.data_table.item(row, 1).text()

        dialog = DataDetailDialog(self.view_exchange_id, symbol, timeframe, self)
        dialog.exec()

    def _on_table_selection_changed(self):
        """테이블 선택 변경 시 메인 차트 업데이트"""
        current_row = self.data_table.currentRow()
        if current_row >= 0:
            symbol = self.data_table.item(current_row, 0).text()
            timeframe = self.data_table.item(current_row, 1).text()

            # 최근 데이터를 차트에 로드 (최대 500개)
            self._load_chart_data(self.view_exchange_id, symbol, timeframe)

    def _load_chart_data(self, exchange_id: str, symbol: str, timeframe: str):
        """차트 데이터 로드"""
        try:
            # 최근 500개 캔들 데이터 가져오기
            candles = self.candles_repo.get_candles(
                exchange_id, symbol, timeframe, limit=500
            )

            if not candles:
                self.main_chart_widget.clear_chart()
                return

            # 해당 기간의 보조지표 가져오기
            if candles:
                # 첫 캔들과 마지막 캔들의 타임스탬프로 범위 계산
                start_ts = candles[-1]['timestamp']  # 가장 오래된
                end_ts = candles[0]['timestamp']    # 가장 최신

                all_indicators = self.indicators_repo.get_indicators_by_timestamp_range(
                    exchange_id, symbol, timeframe, start_ts, end_ts
                )

                # 보조지표를 타임스탬프로 인덱싱
                indicators_dict = {}
                for ind in all_indicators:
                    indicators_dict[ind['timestamp']] = ind
            else:
                indicators_dict = {}

            # 차트 제목 설정 - 일시적으로 비활성화
            # self.main_chart_widget.set_title(f"{exchange_id.upper()} {symbol} ({timeframe})")

            # 차트에 캔들 데이터 로드 (거래소, 심볼 정보 포함) - 일시적으로 비활성화
            # self.main_chart_widget.load_data(candles, indicators_dict, timeframe, exchange_id, symbol)
            print(f"[DEBUG] Chart loading temporarily disabled: {len(candles) if candles else 0} candles for {exchange_id} {symbol}")

        except Exception as e:
            print(f"차트 데이터 로드 실패: {str(e)}")
            self.main_chart_widget.clear_chart()

    def _load_additional_chart_data(self, exchange_id: str, symbol: str, timeframe: str,
                                   start_time: float, end_time: float):
        """동적 차트 데이터 로딩 (과거 데이터)"""
        try:
            # 시간을 문자열로 변환
            start_str = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            end_str = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

            print(f"동적 데이터 로드: {exchange_id} {symbol} {timeframe} {start_str} ~ {end_str}")

            # 추가 데이터 조회 (최대 1000개)
            additional_candles = self.candles_repo.get_candles(
                exchange_id, symbol, timeframe,
                limit=1000, start_time=start_str, end_time=end_str
            )

            if additional_candles:
                # 해당 기간의 보조지표 조회
                additional_indicators = self.indicators_repo.get_indicators_by_timestamp_range(
                    exchange_id, symbol, timeframe, start_str, end_str
                )

                # 보조지표를 딕셔너리로 변환
                indicators_dict = {}
                for ind in additional_indicators:
                    indicators_dict[ind['timestamp']] = ind

                # 차트 위젯에 데이터 추가
                self.main_chart_widget.add_additional_data(additional_candles, indicators_dict)

        except Exception as e:
            print(f"동적 차트 데이터 로딩 실패: {str(e)}")


class DataDetailDialog(QDialog):
    """데이터 상세 보기 다이얼로그"""

    def __init__(self, exchange_id: str, symbol: str, timeframe: str, parent=None):
        super().__init__(parent)
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.timeframe = timeframe

        from database.repository import CandlesRepository, IndicatorsRepository
        self.candles_repo = CandlesRepository()
        self.indicators_repo = IndicatorsRepository()

        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(f"데이터 상세 보기 - {self.symbol} ({self.timeframe})")
        self.setMinimumSize(900, 700)

        layout = QVBoxLayout(self)

        # 제목
        from qfluentwidgets import SubtitleLabel
        title = SubtitleLabel(f"{self.symbol} - {self.timeframe} 데이터")
        layout.addWidget(title)

        # 날짜 범위 선택
        date_layout = QHBoxLayout()

        # 시작 날짜
        date_layout.addWidget(QLabel("시작:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate().addDays(-7))  # 기본 7일
        self.start_date.setFixedWidth(130)
        self.start_date.dateChanged.connect(self._load_data)
        date_layout.addWidget(self.start_date)

        # 종료 날짜
        date_layout.addWidget(QLabel("종료:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFixedWidth(130)
        self.end_date.dateChanged.connect(self._load_data)
        date_layout.addWidget(self.end_date)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # 데이터 개수 표시
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #00ff9f; font-size: 12px; margin: 5px 0;")
        layout.addWidget(self.count_label)

        # 차트 위젯
        # self.chart_widget = CandlestickChartWidget()  # Temporarily disabled due to PyQtGraph segfault
        from PySide6.QtWidgets import QLabel
        self.chart_widget = QLabel("차트 기능이 일시적으로 비활성화되었습니다.\n\nPyQtGraph 충돌 문제를 해결 중입니다.")
        self.chart_widget.setAlignment(Qt.AlignCenter)
        self.chart_widget.setStyleSheet("color: #e0e0e0; padding: 20px;")
        self.chart_widget.setMinimumHeight(400)
        self.chart_widget.setMaximumHeight(600)
        layout.addWidget(self.chart_widget)

        # 데이터 테이블 (OHLCV + 지표)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(10)
        self.data_table.setHorizontalHeaderLabels([
            "시간", "시가", "고가", "저가", "종가", "거래량", "데이터 유형",
            "MA20", "RSI", "MACD"
        ])

        # 열 너비 설정
        self.data_table.setColumnWidth(0, 150)  # 시간
        self.data_table.setColumnWidth(1, 80)   # 시가
        self.data_table.setColumnWidth(2, 80)   # 고가
        self.data_table.setColumnWidth(3, 80)   # 저가
        self.data_table.setColumnWidth(4, 80)   # 종가
        self.data_table.setColumnWidth(5, 100)  # 거래량
        self.data_table.setColumnWidth(6, 80)   # 데이터 유형 (아이콘 포함)
        self.data_table.setColumnWidth(7, 80)   # MA20
        self.data_table.setColumnWidth(8, 60)   # RSI
        self.data_table.setColumnWidth(9, 100)  # MACD

        # 데이터 유형 컬럼에 배경색 적용
        from PySide6.QtWidgets import QStyledItemDelegate
        from PySide6.QtGui import QColor, QBrush

        class TypeItemDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                # 기본 페인팅
                super().paint(painter, option, index)

                # 텍스트에 따른 배경색 처리
                text = index.data()
                if text and "보간" in str(text):
                    # 오렌지 색상으로 강조
                    painter.fillRect(option.rect, QBrush(QColor(255, 170, 0, 30)))
                elif text and "실제" in str(text):
                    # 녹색으로 강조
                    painter.fillRect(option.rect, QBrush(QColor(0, 255, 159, 30)))

        self.data_table.setItemDelegateForColumn(6, TypeItemDelegate())

        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
            QTableWidget {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background: #1a1a2e;
                gridline-color: #4a5080;
                color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #4a5080;
            }
            QTableWidget::item:selected {
                background: rgba(0, 255, 159, 0.2);
                border: 1px solid #00ff9f;
            }
            QTableWidget::alternate-item {
                background: #1e2338;
            }
            QHeaderView::section {
                background: #252b4a;
                color: #00ff9f;
                padding: 8px;
                border: 1px solid #4a5080;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.data_table)

        # 닫기 버튼
        from qfluentwidgets import PushButton
        close_btn = PushButton("닫기")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_data(self):
        """데이터 로드"""
        # 날짜를 시간 형식으로 변환 (DB에는 'YYYY-MM-DD HH:mm:ss' 형식으로 저장)
        start_date = self.start_date.date().toString("yyyy-MM-dd") + " 00:00:00"
        end_date = self.end_date.date().addDays(1).toString("yyyy-MM-dd") + " 00:00:00"  # 종료일 포함

        # 날짜 범위의 데이터 가져오기 (최대 5000개)
        candles = self.candles_repo.get_candles(
            self.exchange_id, self.symbol, self.timeframe,
            limit=5000, start_time=start_date, end_time=end_date
        )

        # 해당 기간의 모든 보조지표 가져오기
        all_indicators = self.indicators_repo.get_indicators_by_timestamp_range(
            self.exchange_id, self.symbol, self.timeframe,
            start_date, end_date
        )

        # 보조지표를 타임스탬프로 인덱싱 (빠른 조회 방지)
        indicators_dict = {}
        for ind in all_indicators:
            indicators_dict[ind['timestamp']] = ind

        # 데이터 개수 표시
        self.count_label.setText(f"총 {len(candles)}개 데이터, {len(all_indicators)}개 지표")

        # 차트에 데이터 로드 - 일시적으로 비활성화
        if candles:
            # 차트 제목 설정
            # self.chart_widget.set_title(f"{self.exchange_id.upper()} {self.symbol} ({self.timeframe})")

            # 차트에 캔들 데이터 로드 (거래소, 심볼 정보 포함) - 일시적으로 비활성화
            # self.chart_widget.load_data(candles, indicators_dict, self.timeframe, self.exchange_id, self.symbol)
            print(f"[DEBUG] Detail chart loading temporarily disabled: {len(candles)} candles for {self.exchange_id} {self.symbol}")
        else:
            # self.chart_widget.clear_chart()
            print("[DEBUG] Chart clear temporarily disabled")

        # 테이블에 데이터 채우기
        self.data_table.setRowCount(len(candles))

        for i, candle in enumerate(candles):
            # 시간 (최신순으로 표시)
            time_item = QTableWidgetItem(candle['timestamp'])
            self.data_table.setItem(i, 0, time_item)

            # OHLCV
            item1 = QTableWidgetItem(f"{candle['open']:.4f}")
            item2 = QTableWidgetItem(f"{candle['high']:.4f}")
            item3 = QTableWidgetItem(f"{candle['low']:.4f}")
            item4 = QTableWidgetItem(f"{candle['close']:.4f}")
            item5 = QTableWidgetItem(f"{candle['volume']:.2f}")

            # 정렬을 위해 숫자 데이터 텍스트로 설정하지만 정렬은 유지
            item1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item2.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item3.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item4.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item5.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.data_table.setItem(i, 1, item1)
            self.data_table.setItem(i, 2, item2)
            self.data_table.setItem(i, 3, item3)
            self.data_table.setItem(i, 4, item4)
            self.data_table.setItem(i, 5, item5)

            # 데이터 유형 (is_interpolated 필드가 있으면 표시)
            if 'is_interpolated' in candle:
                data_type = "보간" if candle['is_interpolated'] else "실제"
            else:
                data_type = "실제"

            type_item = QTableWidgetItem(data_type)
            type_item.setTextAlignment(Qt.AlignCenter)

            # QTableWidgetItem은 setStyleSheet를 지원하지 않음
            # 대신 테이블 위젯의 스타일시트에서 아이템별 스타일을 처리
            # 간단하게 텍스트로 구분
            if data_type == "보간":
                type_item.setText("⚠️ 보간")
            else:
                type_item.setText("✓ 실제")

            self.data_table.setItem(i, 6, type_item)

            # 보조지표 조회 (이미 딕셔너리에 있음)
            indicator = indicators_dict.get(candle['timestamp'], {})

            # MA20
            ma20_item = QTableWidgetItem("")
            ma20_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            ma20 = indicator.get('ma_20')
            if ma20 is not None:
                try:
                    ma20_float = float(ma20)
                    ma20_item.setText(f"{ma20_float:.2f}")
                except (ValueError, TypeError):
                    ma20_item.setText("N/A")
            self.data_table.setItem(i, 7, ma20_item)

            # RSI
            rsi_item = QTableWidgetItem("")
            rsi_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            rsi = indicator.get('rsi')
            if rsi is not None:
                try:
                    rsi_float = float(rsi)
                    rsi_item.setText(f"{rsi_float:.2f}")
                except (ValueError, TypeError):
                    rsi_item.setText("N/A")
            self.data_table.setItem(i, 8, rsi_item)

            # MACD
            macd_item = QTableWidgetItem("")
            macd_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            macd = indicator.get('macd')
            if macd is not None:
                try:
                    macd_float = float(macd)
                    macd_item.setText(f"{macd_float:.4f}")
                except (ValueError, TypeError):
                    macd_item.setText("N/A")
            self.data_table.setItem(i, 9, macd_item)
