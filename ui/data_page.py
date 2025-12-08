"""
데이터 페이지
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from qfluentwidgets import (
    CardWidget, TitleLabel, SubtitleLabel, BodyLabel,
    PushButton, DatePicker, SwitchButton, CheckBox, ProgressBar,
    InfoBar, InfoBarPosition
)
from datetime import datetime, timedelta

from database.repository import CandlesRepository, ActiveSymbolsRepository
from config.settings import DEFAULT_SYMBOLS, TIMEFRAMES, DATA_RETENTION_DAYS
from utils.time_helper import time_helper
from utils.logger import logger


class DataPage(QWidget):
    """데이터 페이지"""
    
    def __init__(self):
        super().__init__()
        self.candles_repo = CandlesRepository()
        self.symbols_repo = ActiveSymbolsRepository()
        
        # 기본 심볼 초기화
        self.symbols_repo.init_default_symbols(DEFAULT_SYMBOLS)
        
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 타이틀
        title = TitleLabel("데이터 수집")
        layout.addWidget(title)
        
        # 수집 설정 카드
        collection_card = CardWidget()
        collection_layout = QVBoxLayout(collection_card)
        
        subtitle = SubtitleLabel("데이터 수집 설정")
        collection_layout.addWidget(subtitle)
        
        # 시작 날짜 설정
        form_layout = QFormLayout()
        
        self.start_date_picker = DatePicker()
        default_start = QDate.currentDate().addDays(-10)
        self.start_date_picker.setDate(default_start)
        form_layout.addRow("수집 시작 일시:", self.start_date_picker)
        
        collection_layout.addLayout(form_layout)
        
        # 안내 메시지
        info_text = BodyLabel(
            f"※ 최대 {DATA_RETENTION_DAYS}일 전까지 수집 가능합니다.\n"
            "※ 과거 데이터를 많이 수집할수록 시간이 오래 걸립니다.\n"
            "※ 고정 타임프레임: 1m, 5m, 15m, 1H, 4H, 1D"
        )
        info_text.setStyleSheet("color: #7f8c8d;")
        collection_layout.addWidget(info_text)
        
        # 저장 버튼
        save_btn = PushButton("데이터 수집 시작")
        save_btn.clicked.connect(self._start_data_collection)
        collection_layout.addWidget(save_btn)
        
        # 진행률
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        collection_layout.addWidget(self.progress_bar)
        
        layout.addWidget(collection_card)
        
        # 실시간 최신화 카드
        realtime_card = CardWidget()
        realtime_layout = QVBoxLayout(realtime_card)
        
        realtime_title = SubtitleLabel("실시간 최신화")
        realtime_layout.addWidget(realtime_title)
        
        realtime_desc = BodyLabel(
            "활성화하면 새로운 캔들 데이터를 실시간으로 수집하고 보조지표를 계산합니다."
        )
        realtime_layout.addWidget(realtime_desc)
        
        switch_layout = QHBoxLayout()
        switch_label = BodyLabel("실시간 최신화:")
        self.realtime_switch = SwitchButton()
        self.realtime_switch.checkedChanged.connect(self._toggle_realtime)
        switch_layout.addWidget(switch_label)
        switch_layout.addWidget(self.realtime_switch)
        switch_layout.addStretch()
        
        realtime_layout.addLayout(switch_layout)
        
        layout.addWidget(realtime_card)
        
        # 활성 심볼 카드
        symbols_card = CardWidget()
        symbols_layout = QVBoxLayout(symbols_card)
        
        symbols_title = SubtitleLabel("활성 심볼 관리")
        symbols_layout.addWidget(symbols_title)
        
        symbols_desc = BodyLabel(
            "데이터를 수집하고 봇에서 사용할 심볼을 선택하세요."
        )
        symbols_layout.addWidget(symbols_desc)
        
        self.symbol_checkboxes = {}
        for symbol in DEFAULT_SYMBOLS:
            checkbox = CheckBox(symbol)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(
                lambda state, s=symbol: self._toggle_symbol(s, state == Qt.Checked)
            )
            self.symbol_checkboxes[symbol] = checkbox
            symbols_layout.addWidget(checkbox)
        
        layout.addWidget(symbols_card)
        
        # 데이터 조회 카드
        view_card = CardWidget()
        view_layout = QVBoxLayout(view_card)
        
        view_title = SubtitleLabel("수집된 데이터 조회")
        view_layout.addWidget(view_title)
        
        # 간단한 테이블 (예시)
        self.data_table = QTableWidget(0, 4)
        self.data_table.setHorizontalHeaderLabels(["심볼", "타임프레임", "최신 시간", "캔들 수"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        view_layout.addWidget(self.data_table)
        
        refresh_btn = PushButton("새로고침")
        refresh_btn.clicked.connect(self._refresh_data_table)
        view_layout.addWidget(refresh_btn)
        
        layout.addWidget(view_card)
        
        layout.addStretch()
        
        # 초기 데이터 로드
        self._refresh_data_table()
    
    def _start_data_collection(self):
        """데이터 수집 시작"""
        start_date = self.start_date_picker.getDate()
        py_date = datetime(start_date.year(), start_date.month(), start_date.day())
        
        # 날짜 검증
        max_past = time_helper.days_ago_kst(DATA_RETENTION_DAYS)
        if py_date < max_past:
            InfoBar.warning(
                title="날짜 오류",
                content=f"최대 {DATA_RETENTION_DAYS}일 전까지만 수집 가능합니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        # 경고 (200일 근접 시)
        if (time_helper.now_kst() - py_date).days > 180:
            InfoBar.warning(
                title="수집 경고",
                content="많은 데이터를 수집하면 시간이 오래 걸리고 리소스를 많이 사용합니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        
        # 활성 심볼 가져오기
        active_symbols = self.symbols_repo.get_active_symbols()
        
        if not active_symbols:
            InfoBar.warning(
                title="심볼 없음",
                content="최소 1개 이상의 심볼을 활성화해주세요.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        logger.info("Data", f"데이터 수집 시작: {py_date} ~ 현재, {len(active_symbols)}개 심볼")
        
        # TODO: 실제로는 워커 스레드에서 백그라운드 수집
        # 여기서는 UI 구조만 제공
        
        InfoBar.info(
            title="수집 시작",
            content="백그라운드에서 데이터 수집이 시작되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _toggle_realtime(self, checked: bool):
        """실시간 최신화 토글"""
        logger.info("Data", f"실시간 최신화: {'활성' if checked else '비활성'}")
        
        # TODO: 워커에게 상태 전달
        
        status = "활성화" if checked else "비활성화"
        InfoBar.success(
            title="설정 변경",
            content=f"실시간 최신화가 {status}되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _toggle_symbol(self, symbol: str, is_active: bool):
        """심볼 활성화 토글"""
        self.symbols_repo.set_symbol_active(symbol, is_active)
        logger.info("Data", f"{symbol} {'활성화' if is_active else '비활성화'}")
    
    def _refresh_data_table(self):
        """데이터 테이블 새로고침"""
        self.data_table.setRowCount(0)
        
        active_symbols = self.symbols_repo.get_active_symbols()
        
        row = 0
        for symbol in active_symbols:
            for timeframe in TIMEFRAMES:
                latest_ts = self.candles_repo.get_latest_timestamp(symbol, timeframe)
                candles = self.candles_repo.get_candles(symbol, timeframe, limit=1000)
                
                self.data_table.insertRow(row)
                self.data_table.setItem(row, 0, QTableWidgetItem(symbol))
                self.data_table.setItem(row, 1, QTableWidgetItem(timeframe))
                self.data_table.setItem(row, 2, QTableWidgetItem(latest_ts or "없음"))
                self.data_table.setItem(row, 3, QTableWidgetItem(str(len(candles))))
                row += 1


