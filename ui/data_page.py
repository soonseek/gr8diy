"""
데이터 페이지
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QScrollArea, QDateEdit
)
from PySide6.QtCore import Qt, QDate, QThread
from qfluentwidgets import (
    CardWidget, TitleLabel, SubtitleLabel, BodyLabel,
    PushButton, SwitchButton, CheckBox, ProgressBar,
    InfoBar, InfoBarPosition, Pivot
)
from datetime import datetime, timedelta

from database.repository import CandlesRepository, ActiveSymbolsRepository
from config.settings import DEFAULT_SYMBOLS, TIMEFRAMES, DATA_RETENTION_DAYS
from utils.time_helper import time_helper
from utils.logger import logger
from utils.crypto import CredentialManager
from config.settings import CREDENTIALS_PATH
from api.okx_client import OKXClient
from workers.data_collector import DataCollectorWorker


class DataPage(QWidget):
    """데이터 페이지"""
    
    def __init__(self):
        super().__init__()
        self.candles_repo = CandlesRepository()
        self.symbols_repo = ActiveSymbolsRepository()
        self.credential_manager = CredentialManager(CREDENTIALS_PATH)
        
        # 기본 심볼 초기화
        self.symbols_repo.init_default_symbols(DEFAULT_SYMBOLS)
        
        # 워커 관련
        self.collector_thread = None
        self.collector_worker = None
        self.collection_button = None
        
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 10, 10)
        layout.setSpacing(15)
        
        # 타이틀
        title = TitleLabel("데이터 수집")
        layout.addWidget(title)
        
        # Pivot (탭) - 좌측 정렬
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        
        self.stack_widget = QStackedWidget(self)
        
        # 설정 탭
        settings_widget = self._create_settings_widget()
        
        # 데이터 조회 탭
        data_view_widget = self._create_data_view_widget()
        
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
        
        # 스택 위젯에 추가
        self.stack_widget.addWidget(settings_widget)
        self.stack_widget.addWidget(data_view_widget)
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack_widget)
        
        # 기본 탭 선택
        self.pivot.setCurrentItem("settings")
    
    def _create_settings_widget(self) -> QWidget:
        """설정 위젯 생성"""
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
        
        # 수집 설정 카드
        collection_card = CardWidget()
        collection_layout = QVBoxLayout(collection_card)
        
        subtitle = SubtitleLabel("데이터 수집 설정")
        collection_layout.addWidget(subtitle)
        
        # 시작 날짜 설정
        date_layout = QHBoxLayout()
        date_label = BodyLabel("수집 시작 일시:")
        date_label.setFixedWidth(120)
        date_layout.addWidget(date_label, 0, Qt.AlignmentFlag.AlignVCenter)
        
        self.start_date_picker = QDateEdit()
        self.start_date_picker.setCalendarPopup(True)
        self.start_date_picker.setDisplayFormat("yyyy-MM-dd")
        self.start_date_picker.setMinimumHeight(40)
        self.start_date_picker.setMinimumWidth(150)
        default_start = QDate.currentDate().addDays(-10)
        self.start_date_picker.setDate(default_start)
        date_layout.addWidget(self.start_date_picker, 0, Qt.AlignmentFlag.AlignVCenter)
        date_layout.addStretch()
        
        collection_layout.addLayout(date_layout)
        
        # 안내 메시지
        info_text = BodyLabel(
            f"※ 최대 {DATA_RETENTION_DAYS}일 전까지 수집 가능합니다.\n"
            "※ 과거 데이터를 많이 수집할수록 시간이 오래 걸립니다.\n"
            "※ 고정 타임프레임: 1m, 5m, 15m, 1H, 4H, 1D"
        )
        info_text.setStyleSheet("color: #7f8c8d;")
        collection_layout.addWidget(info_text)
        
        # 저장 버튼
        self.collection_button = PushButton("데이터 수집 시작")
        self.collection_button.clicked.connect(self._start_data_collection)
        collection_layout.addWidget(self.collection_button)
        
        # 진행 상태 표시
        self.status_label = BodyLabel("")
        self.status_label.setVisible(False)
        self.status_label.setStyleSheet("color: #3498db; font-weight: bold;")
        collection_layout.addWidget(self.status_label)
        
        # 진행률
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
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
        switch_label.setMinimumWidth(120)
        switch_label.setWordWrap(False)
        self.realtime_switch = SwitchButton()
        self.realtime_switch.setMinimumHeight(40)
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
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def _create_data_view_widget(self) -> QWidget:
        """데이터 조회 위젯 생성"""
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
        
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
        
        # 초기 데이터 로드
        self._refresh_data_table()
        
        scroll.setWidget(widget)
        return scroll
    
    def _start_data_collection(self):
        """데이터 수집 시작"""
        try:
            start_date = self.start_date_picker.getDate()
            py_date = datetime(start_date.year(), start_date.month(), start_date.day())
            
            # timezone-aware로 변환
            py_date = time_helper.kst.localize(py_date)
            
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
                return
            
            okx_client = OKXClient(
                creds['api_key'],
                creds['secret'],
                creds['passphrase']
            )
            
            logger.info("Data", f"데이터 수집 시작: {py_date} ~ 현재, {len(active_symbols)}개 심볼")
            
            # 워커 스레드 생성 및 실행
            self.collector_thread = QThread()
            self.collector_worker = DataCollectorWorker(okx_client)
            self.collector_worker.moveToThread(self.collector_thread)
            
            # 시그널 연결
            self.collector_worker.progress_updated.connect(self._on_progress_updated)
            self.collector_worker.collection_completed.connect(self._on_collection_completed)
            self.collector_worker.error_occurred.connect(self._on_collection_error)
            
            # 스레드 시작 시 워커 실행
            self.collector_thread.started.connect(
                lambda: self.collector_worker.backfill_data(active_symbols, py_date)
            )
            
            # UI 상태 변경
            self.collection_button.setEnabled(False)
            self.collection_button.setText("수집 중...")
            self.status_label.setVisible(True)
            self.status_label.setText("데이터 수집 준비 중...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 스레드 시작
            self.collector_thread.start()
            
            InfoBar.info(
                title="수집 시작",
                content="백그라운드에서 데이터 수집이 시작되었습니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
        
        except Exception as e:
            import traceback
            error_msg = f"데이터 수집 시작 실패: {str(e)}"
            logger.error("Data", error_msg, traceback.format_exc())
            InfoBar.error(
                title="오류 발생",
                content=error_msg,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def _on_progress_updated(self, message: str, current: int, total: int):
        """진행률 업데이트"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"📊 {message} ({current}/{total})")
        logger.debug("Data", f"진행률: {progress}% - {message}")
    
    def _on_collection_completed(self):
        """수집 완료"""
        self.collection_button.setEnabled(True)
        self.collection_button.setText("데이터 수집 시작")
        self.status_label.setVisible(False)
        self.progress_bar.setVisible(False)
        
        if self.collector_thread:
            self.collector_thread.quit()
            self.collector_thread.wait()
        
        InfoBar.success(
            title="수집 완료",
            content="데이터 수집이 완료되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
        
        # 테이블 새로고침
        self._refresh_data_table()
    
    def _on_collection_error(self, error_msg: str):
        """수집 오류"""
        self.status_label.setText(f"❌ {error_msg}")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        InfoBar.error(
            title="수집 오류",
            content=error_msg,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _toggle_realtime(self, checked: bool):
        """실시간 최신화 토글"""
        logger.info("Data", f"실시간 최신화: {'활성' if checked else '비활성'}")
        
        if self.collector_worker:
            self.collector_worker.set_realtime_enabled(checked)
        
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


