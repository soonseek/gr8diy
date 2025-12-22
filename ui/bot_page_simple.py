"""
봇 페이지 - 단계적 복구 버전
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QPushButton,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    Pivot, TitleLabel, SubtitleLabel, BodyLabel,
    PushButton as FluentButton, SwitchButton, CardWidget,
    InfoBar, InfoBarPosition, ComboBox, FluentIcon, Slider
)
from datetime import datetime, timedelta


class BotPageSimple(QWidget):
    """봇 페이지 - 단계적 복구"""

    def __init__(self):
        super().__init__()

        # 봇 상태 관리
        self.bots = []  # 생성된 봇 목록
        self.running_bots = {}  # 실행 중인 봇

        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 10, 10)
        layout.setSpacing(15)

        # 타이틀
        title = TitleLabel("자동매매 봇")
        layout.addWidget(title)

        # Pivot (탭) - 좌측 정렬
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()

        self.stack_widget = QStackedWidget(self)

        # 봇 생성 탭
        conditions_widget = self._create_conditions_widget()

        # 모니터링 탭
        monitoring_widget = self._create_monitoring_widget()

        # 내역 탭
        history_widget = self._create_history_widget()

        # Pivot 아이템 추가
        self.pivot.addItem(
            routeKey="conditions",
            text="봇 생성",
            onClick=lambda: self.stack_widget.setCurrentIndex(0),
            icon=FluentIcon.ADD
        )
        self.pivot.addItem(
            routeKey="monitoring",
            text="모니터링",
            onClick=lambda: self.stack_widget.setCurrentIndex(1),
            icon=FluentIcon.ROBOT
        )
        self.pivot.addItem(
            routeKey="history",
            text="내역",
            onClick=lambda: self.stack_widget.setCurrentIndex(2),
            icon=FluentIcon.HISTORY
        )

        # 스택 위젯에 추가
        self.stack_widget.addWidget(conditions_widget)
        self.stack_widget.addWidget(monitoring_widget)
        self.stack_widget.addWidget(history_widget)

        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack_widget)

        # 기본 탭 선택
        self.pivot.setCurrentItem("conditions")

    def _create_conditions_widget(self) -> QWidget:
        """봇 생성 위젯"""
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 기본 설정 카드
        basic_card = CardWidget()
        basic_layout = QVBoxLayout(basic_card)

        basic_layout.addWidget(SubtitleLabel("기본 설정"))

        # 봇 이름
        name_layout = QHBoxLayout()
        name_layout.addWidget(BodyLabel("봇 이름:"))
        self.bot_name_edit = QLineEdit()
        self.bot_name_edit.setPlaceholderText("예: BTC_봇_1")
        name_layout.addWidget(self.bot_name_edit)
        name_layout.addStretch()
        basic_layout.addLayout(name_layout)

        # 거래소 선택
        exchange_layout = QHBoxLayout()
        exchange_layout.addWidget(BodyLabel("거래소:"))
        self.exchange_combo = ComboBox()
        self.exchange_combo.addItems(["OKX", "Binance", "Upbit"])
        self.exchange_combo.setCurrentText("OKX")
        exchange_layout.addWidget(self.exchange_combo)
        exchange_layout.addStretch()
        basic_layout.addLayout(exchange_layout)

        # 심볼 선택
        symbol_layout = QHBoxLayout()
        symbol_layout.addWidget(BodyLabel("심볼:"))
        self.symbol_combo = ComboBox()
        self.symbol_combo.addItems(["BTC/USDT", "ETH/USDT", "BNB/USDT"])
        self.symbol_combo.setCurrentText("BTC/USDT")
        symbol_layout.addWidget(self.symbol_combo)
        symbol_layout.addStretch()
        basic_layout.addLayout(symbol_layout)

        layout.addWidget(basic_card)

        # 매매 전략 카드
        strategy_card = CardWidget()
        strategy_layout = QVBoxLayout(strategy_card)

        strategy_layout.addWidget(SubtitleLabel("매매 전략"))

        # 전략 타입
        strategy_type_layout = QHBoxLayout()
        strategy_type_layout.addWidget(BodyLabel("전략:"))
        self.strategy_combo = ComboBox()
        self.strategy_combo.addItems(["단순 매매", "그리드 매매", "모멘텀 매매"])
        self.strategy_combo.setCurrentText("단순 매매")
        strategy_type_layout.addWidget(self.strategy_combo)
        strategy_type_layout.addStretch()
        strategy_layout.addLayout(strategy_type_layout)

        # 투자금 설정
        capital_layout = QHBoxLayout()
        capital_layout.addWidget(BodyLabel("투자금:"))
        self.capital_edit = QLineEdit("1000")
        capital_layout.addWidget(self.capital_edit)
        capital_layout.addWidget(BodyLabel("USDT"))
        capital_layout.addStretch()
        strategy_layout.addLayout(capital_layout)

        layout.addWidget(strategy_card)

        # 매매 조건 카드
        conditions_card = CardWidget()
        conditions_layout = QVBoxLayout(conditions_card)

        conditions_layout.addWidget(SubtitleLabel("매매 조건"))

        # 진입 조건
        entry_layout = QFormLayout()

        self.rsi_enabled = SwitchButton()
        self.rsi_enabled.setChecked(True)
        entry_layout.addRow("RSI 사용:", self.rsi_enabled)

        self.rsi_oversold = QSpinBox()
        self.rsi_oversold.setRange(10, 40)
        self.rsi_oversold.setValue(30)
        entry_layout.addRow("RSI 과매도:", self.rsi_oversold)

        self.rsi_overbought = QSpinBox()
        self.rsi_overbought.setRange(60, 90)
        self.rsi_overbought.setValue(70)
        entry_layout.addRow("RSI 과매수:", self.rsi_overbought)

        conditions_layout.addLayout(entry_layout)

        layout.addWidget(conditions_card)

        # TP/SL 설정 카드
        tp_sl_card = CardWidget()
        tp_sl_layout = QVBoxLayout(tp_sl_card)

        tp_sl_layout.addWidget(SubtitleLabel("TP/SL 설정"))

        tp_sl_form = QFormLayout()

        self.tp_enabled = SwitchButton()
        self.tp_enabled.setChecked(True)
        tp_sl_form.addRow("익절 사용:", self.tp_enabled)

        self.tp_percentage = QDoubleSpinBox()
        self.tp_percentage.setRange(0.1, 20.0)
        self.tp_percentage.setValue(2.0)
        self.tp_percentage.setSuffix("%")
        tp_sl_form.addRow("익절률:", self.tp_percentage)

        self.sl_enabled = SwitchButton()
        self.sl_enabled.setChecked(True)
        tp_sl_form.addRow("손절 사용:", self.sl_enabled)

        self.sl_percentage = QDoubleSpinBox()
        self.sl_percentage.setRange(0.1, 10.0)
        self.sl_percentage.setValue(1.0)
        self.sl_percentage.setSuffix("%")
        tp_sl_form.addRow("손절률:", self.sl_percentage)

        tp_sl_layout.addLayout(tp_sl_form)

        layout.addWidget(tp_sl_card)

        # 봇 생성 버튼
        create_button = FluentButton("봇 생성")
        create_button.clicked.connect(self.create_bot)
        layout.addWidget(create_button)

        # 남은 공간 채우기
        layout.addStretch()

        scroll.setWidget(widget)
        return scroll

    def _create_monitoring_widget(self) -> QWidget:
        """모니터링 위젯"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 봇 상태 카드
        status_card = CardWidget()
        status_layout = QVBoxLayout(status_card)

        status_layout.addWidget(SubtitleLabel("봇 상태"))

        # 봇 상태 테이블
        self.bot_table = QTableWidget()
        self.bot_table.setColumnCount(7)
        self.bot_table.setHorizontalHeaderLabels([
            "봇 이름", "거래소", "심볼", "상태", "수익률", "진입가", "현재가"
        ])

        # 테이블 크기 조정
        header = self.bot_table.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        self.bot_table.setMaximumHeight(200)
        status_layout.addWidget(self.bot_table)

        # 제어 버튼들
        controls_layout = QHBoxLayout()

        start_button = FluentButton("전체 시작")
        start_button.clicked.connect(self.start_all_bots)
        controls_layout.addWidget(start_button)

        stop_button = FluentButton("전체 중지")
        stop_button.clicked.connect(self.stop_all_bots)
        controls_layout.addWidget(stop_button)

        controls_layout.addStretch()

        status_layout.addLayout(controls_layout)
        layout.addWidget(status_card)

        # 로그 카드
        log_card = CardWidget()
        log_layout = QVBoxLayout(log_card)

        log_layout.addWidget(SubtitleLabel("봇 로그"))

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # 로그 초기화
        self.add_log("봇 모니터링 시스템이 준비되었습니다.")

        layout.addWidget(log_card)

        return widget

    def _create_history_widget(self) -> QWidget:
        """내역 위젯"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 필터 카드
        filter_card = CardWidget()
        filter_layout = QVBoxLayout(filter_card)

        filter_layout.addWidget(SubtitleLabel("거래 내역 필터"))

        # 날짜 범위
        date_layout = QHBoxLayout()
        date_layout.addWidget(BodyLabel("기간:"))
        # 여기에 날짜 선택 위젯 추가 가능

        date_layout.addStretch()
        filter_layout.addLayout(date_layout)

        layout.addWidget(filter_card)

        # 거래 내역 테이블
        history_table = QTableWidget()
        history_table.setColumnCount(8)
        history_table.setHorizontalHeaderLabels([
            "시간", "봇 이름", "거래소", "심볼", "타입", "가격", "수량", "수익"
        ])

        # 테이블 크기 조정
        header = history_table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        layout.addWidget(history_table)

        # 샘플 데이터 표시
        self._add_sample_history(history_table)

        return widget

    def create_bot(self):
        """봇 생성"""
        bot_name = self.bot_name_edit.text() or f"봇_{len(self.bots)+1}"

        bot_config = {
            'name': bot_name,
            'exchange': self.exchange_combo.currentText(),
            'symbol': self.symbol_combo.currentText(),
            'strategy': self.strategy_combo.currentText(),
            'capital': float(self.capital_edit.text() or "1000"),
            'rsi_enabled': self.rsi_enabled.isChecked(),
            'rsi_oversold': self.rsi_oversold.value(),
            'rsi_overbought': self.rsi_overbought.value(),
            'tp_enabled': self.tp_enabled.isChecked(),
            'tp_percentage': self.tp_percentage.value(),
            'sl_enabled': self.sl_enabled.isChecked(),
            'sl_percentage': self.sl_percentage.value(),
            'status': '정지',
            'created_at': datetime.now()
        }

        self.bots.append(bot_config)

        InfoBar.success(
            title="봇 생성 성공",
            content=f"{bot_name} 봇이 생성되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

        # 모니터링 탭으로 자동 전환
        self.pivot.setCurrentItem("monitoring")
        self.stack_widget.setCurrentIndex(1)

        self.update_bot_table()
        self.add_log(f"{bot_name} 봇이 생성되었습니다.")

    def update_bot_table(self):
        """봇 테이블 업데이트"""
        self.bot_table.setRowCount(len(self.bots))

        for row, bot in enumerate(self.bots):
            self.bot_table.setItem(row, 0, QTableWidgetItem(bot['name']))
            self.bot_table.setItem(row, 1, QTableWidgetItem(bot['exchange']))
            self.bot_table.setItem(row, 2, QTableWidgetItem(bot['symbol']))
            self.bot_table.setItem(row, 3, QTableWidgetItem(bot['status']))
            self.bot_table.setItem(row, 4, QTableWidgetItem("0.00%"))
            self.bot_table.setItem(row, 5, QTableWidgetItem("-"))
            self.bot_table.setItem(row, 6, QTableWidgetItem("-"))

    def start_all_bots(self):
        """모든 봇 시작"""
        for bot in self.bots:
            if bot['status'] == '정지':
                bot['status'] = '실행 중'
                self.running_bots[bot['name']] = bot

        self.update_bot_table()

        InfoBar.success(
            title="봇 시작",
            content=f"{len(self.running_bots)}개의 봇이 실행 중입니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

        self.add_log("모든 봇이 시작되었습니다.")

    def stop_all_bots(self):
        """모든 봇 중지"""
        for bot in self.bots:
            bot['status'] = '정지'

        stopped_count = len(self.running_bots)
        self.running_bots.clear()

        self.update_bot_table()

        InfoBar.info(
            title="봇 중지",
            content=f"{stopped_count}개의 봇이 중지되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

        self.add_log("모든 봇이 중지되었습니다.")

    def add_log(self, message: str):
        """로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        # 스크롤을 맨 아래로
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def _add_sample_history(self, table: QTableWidget):
        """샘플 거래 내역 추가"""
        sample_data = [
            ("2024-01-01 10:30:00", "BTC_봇_1", "OKX", "BTC/USDT", "매수", "42000", "0.024", "+150.5"),
            ("2024-01-01 11:15:00", "BTC_봇_1", "OKX", "BTC/USDT", "매도", "42300", "0.024", "+72.0"),
            ("2024-01-01 14:20:00", "ETH_봇_1", "OKX", "ETH/USDT", "매수", "2200", "0.45", "+18.5"),
            ("2024-01-01 15:45:00", "ETH_봇_1", "OKX", "ETH/USDT", "매도", "2250", "0.45", "+22.5"),
            ("2024-01-01 16:30:00", "BTC_봇_2", "OKX", "BTC/USDT", "매수", "42500", "0.023", "-23.0"),
        ]

        table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                table.setItem(row, col, QTableWidgetItem(str(value)))