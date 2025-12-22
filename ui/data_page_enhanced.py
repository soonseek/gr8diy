"""
데이터 페이지 - 개선된 버전 (실제 데이터 수집 기능)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QScrollArea, QDateEdit,
    QCheckBox, QSpinBox, QDoubleSpinBox, QLabel, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from qfluentwidgets import (
    CardWidget, TitleLabel, SubtitleLabel, BodyLabel,
    PushButton, SwitchButton, CheckBox, ProgressBar,
    InfoBar, InfoBarPosition, Pivot, FluentIcon, Slider
)
from datetime import datetime, timedelta
import threading
import pandas as pd

from workers.data_collector_worker import DataCollectorWorker
from database.repository import CandlesRepository, ActiveSymbolsRepository, IndicatorsRepository
from api.okx_client import OKXClient
from utils.logger import logger
from utils.time_helper import time_helper
from config.settings import TIMEFRAMES, DEFAULT_SYMBOLS, INDICATOR_PARAMS
from config.exchanges import SUPPORTED_EXCHANGES, ALL_EXCHANGE_IDS


class DataPageEnhanced(QWidget):
    """데이터 페이지 - 개선된 버전"""

    # Signal definition for DataCollectorWorker thread
    progress_updated = Signal(str, int, int)
    collection_completed = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()

        # 초기화
        self.symbols_repo = None
        self.candles_repo = None
        self.indicators_repo = None
        self.data_collector = None
        self.collection_thread = None

        # UI 상태
        self.is_collecting = False
        self.selected_symbols = []
        self.collection_start_date = None

        # UI 초기화
        self._init_ui()
        self._init_data()

        # 신호 연결
        self._connect_signals()

    def _init_data(self):
        """데이터베이스 및 초기 데이터 초기화"""
        try:
            self.symbols_repo = ActiveSymbolsRepository()
            self.candles_repo = CandlesRepository()
            self.indicators_repo = IndicatorsRepository()

            # 기본 심볼 설정
            self.symbols_repo.init_default_symbols("okx", DEFAULT_SYMBOLS)

            # 선택된 심볼 목록 (기본값으로 첫 3개)
            all_symbols = self.symbols_repo.get_all_symbols("okx")
            self.selected_symbols = [s['symbol'] for s in all_symbols[:3]]

            logger.info("DataPageEnhanced", "데이터베이스 초기화 완료")

        except Exception as e:
            logger.error("DataPageEnhanced", f"초기화 실패: {str(e)}")
            InfoBar.error(
                title="초기화 오류",
                content=f"데이터베이스 초기화에 실패했습니다: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def _init_ui(self):
        """UI 초기화"""
        print("[DEBUG-DataPageEnhanced] DataPageEnhanced UI 초기화 시작")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 10, 10)
        layout.setSpacing(15)

        # 타이틀
        title = TitleLabel("데이터 수집 및 관리")
        layout.addWidget(title)
        print("[DEBUG-DataPageEnhanced] 타이틀 추가 완료")

        # Pivot (탭)
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()

        self.stack_widget = QStackedWidget(self)

        # 설정 탭
        settings_widget = self._create_settings_widget()

        # 데이터 조회 탭
        data_view_widget = self._create_data_view_widget()

        # 수집 모니터 탭
        monitor_widget = self._create_monitor_widget()

        # Pivot 아이템 추가
        self.pivot.addItem(
            routeKey="settings",
            text="설정",
            onClick=lambda: self.stack_widget.setCurrentIndex(0)
        )
        self.pivot.addItem(
            routeKey="data_view",
            text="데이터 조회",
            onClick=lambda: self.stack_widget.setCurrentIndex(1)
        )
        self.pivot.addItem(
            routeKey="monitor",
            text="수집 모니터",
            onClick=lambda: self.stack_widget.setCurrentIndex(2)
        )

        # 스택 위젯에 추가
        self.stack_widget.addWidget(settings_widget)
        self.stack_widget.addWidget(data_view_widget)
        self.stack_widget.addWidget(monitor_widget)

        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack_widget)

        # 기본 탭 선택
        self.pivot.setCurrentItem("settings")

    def _create_settings_widget(self) -> QWidget:
        """설정 위젯 생성"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 수집 설정 카드
        collection_card = CardWidget()
        collection_layout = QVBoxLayout(collection_card)

        collection_layout.addWidget(SubtitleLabel("데이터 수집 설정"))

        # 거래소 선택
        print("[DEBUG-DataPageEnhanced] 거래소 선택 UI 생성 시작")
        exchange_layout = QHBoxLayout()
        exchange_layout.addWidget(BodyLabel("거래소:"))
        self.exchange_combo = ComboBox()

        # CCXT 지원 거래소 목록으로 채우기
        print(f"[DEBUG-DataPageEnhanced] 거래소 목록 추가: {len(ALL_EXCHANGE_IDS)}개")
        for ex_id in ALL_EXCHANGE_IDS:
            ex_data = SUPPORTED_EXCHANGES.get(ex_id, {})
            ex_name = ex_data.get("name", ex_id.upper())
            rank = ex_data.get("rank", 999)
            display_name = f"{ex_name} (#{rank})" if rank != 999 else ex_name
            self.exchange_combo.addItem(display_name, ex_id)

        # 기본값 OKX로 설정
        okx_index = next((i for i, ex_id in enumerate(ALL_EXCHANGE_IDS) if ex_id == "okx"), 0)
        self.exchange_combo.setCurrentIndex(okx_index)
        self.exchange_combo.currentTextChanged.connect(self._update_symbols_for_exchange)
        exchange_layout.addWidget(self.exchange_combo)
        exchange_layout.addStretch()
        collection_layout.addLayout(exchange_layout)
        print("[DEBUG-DataPageEnhanced] 거래소 선택 UI 생성 완료")

        # 기간 설정
        period_layout = QHBoxLayout()
        period_layout.addWidget(BodyLabel("백필 기간:"))
        self.period_combo = ComboBox()
        self.period_combo.addItems(["최근 7일", "최근 30일", "최근 90일", "전체 기간", "직접 선택"])
        self.period_combo.setCurrentText("최근 7일")
        self.period_combo.currentTextChanged.connect(self._update_period)
        period_layout.addWidget(self.period_combo)
        period_layout.addStretch()
        collection_layout.addLayout(period_layout)

        # 날짜 선택 (직접 선택일 때만 표시)
        self.date_layout = QHBoxLayout()
        self.date_layout.addWidget(BodyLabel("시작일:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setVisible(False)
        self.date_layout.addWidget(self.start_date)

        self.date_layout.addWidget(BodyLabel("종료일:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setVisible(False)
        self.date_layout.addWidget(self.end_date)

        self.date_layout.addStretch()
        collection_layout.addLayout(self.date_layout)

        layout.addWidget(collection_card)

        # 심볼 선택 카드
        symbols_card = CardWidget()
        symbols_layout = QVBoxLayout(symbols_card)

        symbols_layout.addWidget(SubtitleLabel("심볼 선택"))

        # 심볼 리스트
        self.symbols_table = QTableWidget()
        self.symbols_table.setColumnCount(5)
        self.symbols_table.setHorizontalHeaderLabels(["선택", "거래소", "심볼", "상태", "마지막 업데이트"])

        # 테이블 설정
        header = self.symbols_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setResizeMode(4, QHeaderView.ResizeToContents)

        self.symbols_table.setMaximumHeight(200)
        symbols_layout.addWidget(self.symbols_table)

        # 전체 선택/해제 체크박스
        checkbox_layout = QHBoxLayout()
        self.select_all_checkbox = CheckBox("전체 선택")
        self.select_all_checkbox.stateChanged.connect(self._toggle_all_symbols)
        checkbox_layout.addWidget(self.select_all_checkbox)
        checkbox_layout.addStretch()
        symbols_layout.addLayout(checkbox_layout)

        layout.addWidget(symbols_card)

        # 타임프레임 카드
        timeframe_card = CardWidget()
        timeframe_layout = QVBoxLayout(timeframe_card)

        timeframe_layout.addWidget(SubtitleLabel("타임프레임 선택"))

        # 타임프레임 체크박스들
        self.timeframe_checkboxes = {}
        for timeframe in TIMEFRAMES:
            checkbox = CheckBox(f"{timeframe}")
            checkbox.setChecked(True)  # 기본적으로 모두 선택
            self.timeframe_checkboxes[timeframe] = checkbox
            timeframe_layout.addWidget(checkbox)

        layout.addWidget(timeframe_card)

        # 저장 설정 카드
        storage_card = CardWidget()
        storage_layout = QVBoxLayout(storage_card)

        storage_layout.addWidget(SubtitleLabel("저장 설정"))

        # 보조지표 계산
        self.calculate_indicators_checkbox = SwitchButton()
        self.calculate_indicators_checkbox.setChecked(True)
        self.calculate_indicators_checkbox.setText("보조지표 함께 저장")
        storage_layout.addWidget(self.calculate_indicators_checkbox)

        # 자동 삭제 설정
        self.auto_delete_checkbox = SwitchButton()
        self.auto_delete_checkbox.setChecked(True)
        self.auto_delete_checkbox.setText(f"{DATA_RETENTION_DAYS}일 이전 데이터 자동 삭제")
        storage_layout.addWidget(self.auto_delete_checkbox)

        layout.addWidget(storage_card)

        # 수집 버튼
        button_layout = QHBoxLayout()
        self.collection_button = PushButton("데이터 수집 시작")
        self.collection_button.clicked.connect(self.toggle_collection)
        self.collection_button.setMaximumWidth(200)  # 최대 너비 200px로 제한
        button_layout.addWidget(self.collection_button)
        button_layout.addStretch()  # 버튼 오른쪽에 빈 공간 추가
        layout.addLayout(button_layout)

        # 진행률 표시줄
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 상태 표시
        self.status_label = BodyLabel("준비 완료")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()
        scroll.setWidget(widget)
        return scroll

    def _create_data_view_widget(self) -> QWidget:
        """데이터 조회 위젯 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 조회 설정 카드
        query_card = CardWidget()
        query_layout = QVBoxLayout(query_card)

        query_layout.addWidget(SubtitleLabel("데이터 조회"))

        # 필터 설정
        filter_layout = QFormLayout()

        # 거래소 필터
        query_exchange_combo = ComboBox()
        query_exchange_combo.addItems(["OKX", "전체"])
        query_exchange_combo.setCurrentText("OKX")
        filter_layout.addRow("거래소:", query_exchange_combo)

        # 심볼 필터
        query_symbol_edit = QLineEdit()
        query_symbol_edit.setPlaceholderText("BTC/USDT, ETH/USDT 등 (쉼표 구분자 사용)")
        filter_layout.addRow("심볼:", query_symbol_edit)

        # 타임프레임 필터
        query_timeframe_combo = ComboBox()
        query_timeframe_combo.addItems(TIMEFRAMES + ["전체"])
        query_timeframe_combo.setCurrentText("1m")
        filter_layout.addRow("타임프레임:", query_timeframe_combo)

        # 날짜 범위 설정
        query_date_layout = QHBoxLayout()

        query_date_layout.addWidget(BodyLabel("시작일:"))
        self.query_start_date = QDateEdit()
        self.query_start_date.setDate(QDate.currentDate().addDays(-1))
        self.query_start_date.setCalendarPopup(True)
        query_date_layout.addWidget(self.query_start_date)

        query_date_layout.addWidget(BodyLabel("종료일:"))
        query_end_date = QDateEdit()
        query_end_date.setDate(QDate.currentDate())
        query_end_date.setCalendarPopup(True)
        query_date_layout.addWidget(query_end_date)

        query_date_layout.addStretch()
        filter_layout.addRow("날짜 범위:", query_date_layout)

        # 개수 제한
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setRange(100, 50000)
        self.limit_spinbox.setValue(1000)
        self.limit_spinbox.setSuffix("개")
        filter_layout.addRow("최대 개수:", self.limit_spinbox)

        query_layout.addLayout(filter_layout)

        # 조회 버튼
        query_button = PushButton("데이터 조회")
        query_button.clicked.connect(self.query_data)
        query_layout.addRow("", query_button)

        layout.addWidget(query_card)

        # 데이터 테이블
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(8)
        self.data_table.setHorizontalHeaderLabels([
            "시간", "거래소", "심볼", "시가", "고가", "저가", "종가", "거래량"
        ])

        # 테이블 크기 조정
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.Stretch)

        layout.addWidget(self.data_table)

        # 초기 상태 메시지
        self._show_empty_state()

        return widget

    def _create_monitor_widget(self) -> QWidget:
        """수집 모니터 위젯"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 수집 상태 카드
        status_card = CardWidget()
        status_layout = QVBoxLayout(status_card)

        status_layout.addWidget(SubtitleLabel("수집 상태"))

        # 현재 수집 상태
        self.monitor_status_label = BodyLabel("대기 중...")
        self.monitor_status_label.setStyleSheet("color: #666; font-size: 14px;")
        status_layout.addWidget(self.monitor_status_label)

        # 진행률 표시
        self.monitor_progress_bar = ProgressBar()
        status_layout.addWidget(self.monitor_progress_bar)

        # 제어 버튼
        controls_layout = QHBoxLayout()

        self.stop_button = PushButton("수집 중지")
        self.stop_button.clicked.connect(self.stop_collection)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)

        controls_layout.addStretch()
        status_layout.addLayout(controls_layout)

        layout.addWidget(status_card)

        # 수집 로그
        log_card = CardWidget()
        log_layout = QVBoxLayout(log_card)

        log_layout.addWidget(SubtitleLabel("수집 로그"))

        self.monitor_log_text = QTextEdit()
        self.monitor_log_text.setMaximumHeight(300)
        self.monitor_log_text.setReadOnly(True)
        log_layout.addWidget(self.monitor_log_text)

        layout.addWidget(log_card)

        return widget

    def _connect_signals(self):
        """신호 연결"""
        # DataCollectorWorker 신호 연결
        self.progress_updated.connect(self.on_progress_updated)
        self.collection_completed.connect(self.on_collection_completed)
        self.error_occurred.connect(self.on_error_occurred)

    def _update_period(self):
        """기간 선택에 따라 날짜 업데이트"""
        period_text = self.period_combo.currentText()

        if period_text == "최근 7일":
            self.start_date.setDate(QDate.currentDate().addDays(-7))
            self.end_date.setDate(QDate.currentDate())
            self.start_date.setVisible(False)
            self.end_date.setVisible(False)
        elif period_text == "최근 30일":
            self.start_date.setDate(QDate.currentDate().addDays(-30))
            self.end_date.setDate(QDate.currentDate())
            self.start_date.setVisible(False)
            self.end_date.setVisible(False)
        elif period_text == "최근 90일":
            self.start_date.setDate(QDate.currentDate().addDays(-90))
            self.end_date.setDate(QDate.currentDate())
            self.start_date.setVisible(False)
            self.end_date.setVisible(False)
        elif period_text == "전체 기간":
            self.start_date.setDate(QDate.currentDate().addDays(-365))
            self.end_date.setDate(QDate.currentDate())
            self.start_date.setVisible(False)
            self.end_date.setVisible(False)
        elif period_text == "직접 선택":
            self.start_date.setVisible(True)
            self.end_date.setVisible(True)

    def _update_symbols_for_exchange(self):
        """거래소 변경에 따른 심볼 목록 업데이트"""
        try:
            # 선택된 거래소 ID 가져오기
            current_index = self.exchange_combo.currentIndex()
            if 0 <= current_index < len(ALL_EXCHANGE_IDS):
                exchange_id = ALL_EXCHANGE_IDS[current_index]
                exchange_name = SUPPORTED_EXCHANGES.get(exchange_id, {}).get("name", exchange_id.upper())
            else:
                exchange_id = "okx"
                exchange_name = "OKX"

            self.add_monitor_log(f"거래소 변경: {exchange_name}")

            # 레포지토리가 있다면 심볼 목록 새로고침
            if hasattr(self, 'symbols_repo') and self.symbols_repo:
                self._load_symbols()
            else:
                # 샘플 심볼 표시
                self._load_sample_symbols(exchange_id)

        except Exception as e:
            logger.error("DataPageEnhanced", f"거래소 변경 실패: {str(e)}")

    def _load_sample_symbols(self, exchange_id: str):
        """샘플 심볼 로드"""
        # 기본 심볼들 - 대부분의 거래소에서 지원
        base_symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT", "XRP/USDT:USDT", "DOGE/USDT:USDT"]

        # 거래소별 특수 심볼들
        exchange_specific = {
            "upbit": ["BTC/KRW", "ETH/KRW", "XRP/KRW", "DOGE/KRW", "ADA/KRW"],  # 한국 거래소 - 원화 페어
            "bithumb": ["BTC/KRW", "ETH/KRW", "XRP/KRW", "DOGE/KRW", "ADA/KRW"],  # 한국 거래소
            "coinone": ["BTC/KRW", "ETH/KRW", "XRP/KRW", "DOGE/KRW", "ADA/KRW"],  # 한국 거래소
            "huobi": ["BTC/USDT", "ETH/USDT", "HT/USDT", "DOT/USDT", "LINK/USDT"],  # HT 포함
            "kucoin": ["BTC/USDT", "ETH/USDT", "KCS/USDT", "DOT/USDT", "LINK/USDT"],  # KCS 포함
            "gate": ["BTC/USDT", "ETH/USDT", "GT/USDT", "DOT/USDT", "LINK/USDT"],  # GT 포함
        }

        # 거래소 데이터 가져오기
        ex_data = SUPPORTED_EXCHANGES.get(exchange_id, {})

        # 심볼 포맷 결정
        if exchange_id in ["upbit", "bithumb", "coinone"]:  # 한국 거래소
            symbols = exchange_specific.get(exchange_id, base_symbols[:5])
        elif exchange_id == "huobi":
            symbols = exchange_specific.get(exchange_id, base_symbols[:5])
        elif exchange_id == "kucoin":
            symbols = exchange_specific.get(exchange_id, base_symbols[:5])
        elif exchange_id == "gate":
            symbols = exchange_specific.get(exchange_id, base_symbols[:5])
        else:
            # 나머지 거래소는 기본 심볼 사용
            symbols = base_symbols[:5]

        self.symbols_table.setRowCount(len(symbols))
        for i, symbol in enumerate(symbols):
            # 체크박스
            checkbox = QCheckBox()
            checkbox.setChecked(i < 3)  # 기본적으로 첫 3개 선택
            self.symbols_table.setCellWidget(i, 0, checkbox)

            # 거래소
            exchange_name = ex_data.get("name", exchange_id.upper())
            self.symbols_table.setItem(i, 1, QTableWidgetItem(exchange_name))

            # 심볼
            self.symbols_table.setItem(i, 2, QTableWidgetItem(symbol))

            # 상태
            self.symbols_table.setItem(i, 3, QTableWidgetItem("대기 중"))

            # 마지막 업데이트
            self.symbols_table.setItem(i, 4, QTableWidgetItem("-"))

    def _toggle_all_symbols(self, state):
        """모든 심볼 선택 토글"""
        for i in range(self.symbols_table.rowCount()):
            item = self.symbols_table.item(i, 0)
            if item:
                item.setCheckState(Qt.Checked if state else Qt.Unchecked)

    def toggle_collection(self):
        """데이터 수집 토글"""
        if self.is_collecting:
            self.stop_collection()
        else:
            self.start_collection()

    def start_collection(self):
        """데이터 수집 시작"""
        # 선택된 심볼 목록 업데이트
        self.selected_symbols = []
        for i in range(self.symbols_table.rowCount()):
            item = self.symbols_table.item(i, 0)
            if item and item.checkState() == Qt.Checked:
                symbol = self.symbols_table.item(i, 2).text()
                self.selected_symbols.append(symbol)

        # 선택된 거래소 ID 가져오기
        current_index = self.exchange_combo.currentIndex()
        if 0 <= current_index < len(ALL_EXCHANGE_IDS):
            selected_exchange = ALL_EXCHANGE_IDS[current_index]
        else:
            selected_exchange = "okx"  # 기본값

        if not self.selected_symbols:
            InfoBar.warning(
                title="심볼 선택 필요",
                content="수집할 심볼을 선택해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        # 선택된 타임프레임 목록
        selected_timeframes = [
            tf for tf, cb in self.timeframe_checkboxes.items()
            if cb.isChecked()
        ]

        if not selected_timeframes:
            InfoBar.warning(
                title="타임프레임 선택 필요",
                content="수집할 타임프레임을 선택해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        # 시작일 계산
        if self.start_date.isVisible():
            start_date = self.start_date.date().toPython()
        else:
            days = {
                "최근 7일": 7,
                "최근 30일": 30,
                "최근 90일": 90,
                "전체 기간": 365,
                "직접 선택": 7
            }
            days = days.get(self.period_combo.currentText(), 7)
            start_date = datetime.now() - timedelta(days=days)

        self.collection_start_date = start_date

        # 데이터 수집 워커 생성 및 시작
        try:
            self.data_collector = DataCollectorWorker()
            self.collection_thread = QThread()
            self.data_collector.moveToThread(self.collection_thread)

            # 신호 연결
            self.data_collector.progress_updated.connect(self.on_progress_updated)
            self.data_collector.collection_completed.connect(self.on_collection_completed)
            self.data_collector.error_occurred.connect(self.on_error_occurred)
            self.data_collector.log_message.connect(self.add_monitor_log)

            self.collection_thread.started.connect(self.on_collection_started)
            self.collection_thread.finished.connect(self.on_collection_finished)

            # 수집 시작
            self.collection_thread.start()
            self.data_collector.backfill_data(self.selected_symbols, start_date, selected_exchange)

        except Exception as e:
            logger.error("DataPageEnhanced", f"데이터 수집 시작 실패: {str(e)}")
            self.on_error_occurred(f"데이터 수집 시작 실패: {str(e)}")

    def stop_collection(self):
        """데이터 수집 중지"""
        if self.data_collector:
            self.data_collector.stop_collection()

    def on_collection_started(self):
        """수집 시작 시 처리"""
        self.is_collecting = True
        self.collection_button.setText("수집 중지")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("데이터 수집 중...")

        # UI 상태 변경
        self.monitor_status_label.setText("데이터 수집 중...")
        self.monitor_progress_bar.setValue(0)
        self.stop_button.setEnabled(True)
        self.pivot.setCurrentItem("monitor")  # 모니터 탭으로 전환
        self.stack_widget.setCurrentIndex(2)

        self.add_monitor_log("데이터 수집이 시작되었습니다.")
        # 거래소 이름 표시
        current_index = self.exchange_combo.currentIndex()
        if 0 <= current_index < len(ALL_EXCHANGE_IDS):
            exchange_id = ALL_EXCHANGE_IDS[current_index]
            exchange_name = SUPPORTED_EXCHANGES.get(exchange_id, {}).get("name", exchange_id.upper())
        else:
            exchange_name = self.exchange_combo.currentText()

        self.add_monitor_log(f"거래소: {exchange_name}")
        self.add_monitor_log(f"심볼: {', '.join(self.selected_symbols)}")
        self.add_monitor_log(f"타임프레임: {', '.join([tf for tf, cb in self.timeframe_checkboxes.items() if cb.isChecked()])}")

    def on_collection_finished(self):
        """수집 완료 시 처리"""
        self.is_collecting = False
        self.collection_button.setText("데이터 수집 시작")
        self.progress_bar.setVisible(False)
        self.status_label.setText("수집 준비 완료")

        # UI 상태 복원
        self.monitor_status_label.setText("대기 중...")
        self.monitor_progress_bar.setValue(0)
        self.stop_button.setEnabled(False)

        self.add_monitor_log("데이터 수집이 완료되었습니다.")

    def on_progress_updated(self, message: str, current: int, total: int):
        """진행률 업데이트"""
        progress_percent = int((current / total) * 100) if total > 0 else 0

        self.progress_bar.setValue(progress_percent)
        self.monitor_progress_bar.setValue(progress_percent)

        self.status_label.setText(f"{message} ({current}/{total})")
        self.add_monitor_log(f"진행률: {progress_percent}% - {message}")

    def on_collection_completed(self):
        """수집 완료 처리"""
        self.add_monitor_log("✅ 모든 데이터 수집이 완료되었습니다.")
        InfoBar.success(
            title="수집 완료",
            content=f"{len(self.selected_symbols)}개 심볼의 데이터 수집이 완료되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def on_error_occurred(self, error_message: str):
        """오류 발생 처리"""
        self.status_label.setText(f"오류 발생: {error_message}")

        self.add_monitor_log(f"❌ 오류: {error_message}")
        InfoBar.error(
            title="수집 오류",
            content=error_message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=8000,
            parent=self
        )

    def query_data(self):
        """데이터 조회"""
        try:
            # 필터링
            exchange_filter = self.query_exchange_combo.currentText()
            symbol_filter = self.query_symbol_edit.text().strip()
            timeframe_filter = query_timeframe_combo.currentText()
            start_date = self.query_start_date.date().toPython()
            end_date = self.query_end_date.date().toPython()
            limit = self.limit_spinbox.value()

            # 데이터 조회
            candles_data = self._fetch_candles_data(
                exchange_filter, symbol_filter, timeframe_filter,
                start_date, end_date, limit
            )

            if candles_data:
                self._display_candles_data(candles_data)
                InfoBar.success(
                    title="조회 완료",
                    content=f"{len(candles_data)}개의 데이터를 조회했습니다.",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            else:
                self._show_empty_state()

        except Exception as e:
            logger.error("DataPageEnhanced", f"데이터 조회 실패: {str(e)}")
            InfoBar.error(
                title="조회 오류",
                content=f"데이터 조회 중 오류가 발생했습니다: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def _fetch_candles_data(self, exchange_filter, symbol_filter, timeframe_filter,
                          start_date, end_date, limit):
        """데이터 조회"""
        try:
            # 필터링 조건 구성
            conditions = ["1=1"]
            params = ()

            if exchange_filter != "전체":
                conditions.append("exchange_id = ?")
                params += (exchange_filter,)

            if symbol_filter:
                if "," in symbol_filter:
                    symbols = [s.strip() for s in symbol_filter.split(",")]
                    placeholders = ",".join(["?"] * len(symbols))
                    conditions.append(f"symbol IN ({placeholders})")
                    params += tuple(symbols)
                else:
                    conditions.append("symbol = ?")
                    params += (symbol_filter,)

            if timeframe_filter != "전체":
                conditions.append("timeframe = ?")
                params += (timeframe_filter,)

            conditions.append("timestamp BETWEEN ? AND ?")
            params += (
                start_date.strftime("%Y-%m-%d %H:%M:%S"),
                end_date.strftime("%Y-%m-%d %H:%M:%S")
            )

            conditions.append("1=1 ORDER BY timestamp DESC LIMIT ?")
            params += (limit,)

            sql = f"""
                SELECT timestamp, exchange_id, symbol, timeframe, open_price, high_price, low_price, close_price, volume
                FROM candles
                WHERE {' AND '.join(conditions)}
            """

            query = self.candles_repo.execute_query(sql, params)
            results = []

            while query.next():
                row = {}
                for i in range(query.record().count()):
                    row[query.record().fieldName(i)] = query.value(i)
                results.append(row)

            return results

        except Exception as e:
            logger.error("DataPageEnhanced", f"데이터 조회 실패: {str(e)}")
            return []

    def _display_candles_data(self, candles_data):
        """캔들 데이터 테이블에 표시"""
        self.data_table.setRowCount(len(candles_data))

        for row, data in enumerate(candles_data):
            # 시간 포맷팅
            timestamp = data['timestamp']
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_time = str(timestamp)
            else:
                dt = datetime.fromtimestamp(timestamp / 1000)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M")

            self.data_table.setItem(row, 0, QTableWidgetItem(formatted_time))
            self.data_table.setItem(row, 1, QTableWidgetItem(data['exchange_id']))
            self.data_table.setItem(row, 2, QTableWidgetItem(data['symbol']))
            self.data_table.setItem(row, 3, QTableWidgetItem(f"{data['open_price']:.2f}"))
            self.data_table.setItem(row, 4, QTableWidgetItem(f"{data['high_price']:.2f}"))
            self.data_table.setItem(row, 5, QTableWidgetItem(f"{data['low_price']:.2f}"))
            self.data_table.setItem(row, 6, QTableWidgetItem(f"{data['close_price']:.2f}"))
            self.data_table.setItem(row, 7, QTableWidgetItem(f"{data['volume']:.2f}"))

    def _show_empty_state(self):
        """빈 상태 표시"""
        self.data_table.setRowCount(1)
        item = QTableWidgetItem(
            "데이터를 조회하려면 설정 탭에서 조건을 설정하고 조회 버튼을 클릭하세요.\n\n"
            "팁: 캔들 데이터가 없는 경우 조회 버튼 클릭 후 수집을 먼저 진행해주세요."
        )
        item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        item.setStyleSheet("color: #666; padding: 20px;")
        self.data_table.setSpan(0, 0, 1, 8)
        self.data_table.setItem(0, 0, item)

    def add_monitor_log(self, message: str):
        """모니터링 로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.monitor_log_text.append(log_message)
        self.monitor_log_text.verticalScrollBar().setValue(
            self.monitor_log_text.verticalScrollBar().maximum()
        )

    def _load_symbols_data(self):
        """심볼 데이터 로드"""
        try:
            symbols_data = self.symbols_repo.get_all_symbols("okx")

            self.symbols_table.setRowCount(len(symbols_data))

            for i, symbol in enumerate(symbols_data):
                # 체크박스
                checkbox_item = QTableWidgetItem()
                checkbox_item.setCheckState(
                    Qt.Checked if symbol['symbol'] in self.selected_symbols else Qt.Unchecked
                )

                # 심볼 정보
                self.symbols_table.setItem(i, 0, checkbox_item)
                self.symbols_table.setItem(i, 1, QTableWidgetItem(symbol['exchange_id']))
                self.symbols_table.setItem(i, 2, QTableWidgetItem(symbol['symbol']))

                # 상태
                status_item = QTableWidgetItem("활성")
                status_item.setStyleSheet("color: #27ae60;")
                self.symbols_table.setItem(i, 3, status_item)

                # 마지막 업데이트
                try:
                    latest_ts = self.candles_repo.get_latest_timestamp(
                        symbol['exchange_id'], symbol['symbol'], "1m"
                    )
                    if latest_ts:
                        dt = datetime.fromisoformat(latest_ts)
                        formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                        last_update = f"{formatted_time}"
                    else:
                        last_update = "없음"
                except:
                    last_update = "오류"

                self.symbols_table.setItem(i, 4, QTableWidgetItem(last_update))

        except Exception as e:
            logger.error("DataPageEnhanced", f"심볼 데이터 로드 실패: {str(e)}")