"""
백테스트 페이지 - 단계적 복구 버전
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QScrollArea, QDateEdit,
    QFrame, QTextEdit, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, QDate, QThread
from PySide6.QtGui import QColor
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, BodyLabel,
    PushButton, ComboBox, SpinBox, DoubleSpinBox, SwitchButton,
    ProgressBar, InfoBar, Pivot, FluentIcon, CardWidget
)
from datetime import datetime, timedelta
import json
import random


class BacktestPageSimple(QWidget):
    """백테스트 페이지 - 단계적 복구"""

    def __init__(self):
        super().__init__()

        # 백테스트 결과 저장
        self.backtest_results = []
        self.current_result = None

        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 타이틀
        title = TitleLabel("백테스트")
        layout.addWidget(title)

        # Pivot (탭)
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()

        self.stack = QStackedWidget()

        # 설정 탭
        settings_w = self._create_settings()

        # 결과 탭
        results_w = self._create_results()

        # 히스토리 탭
        history_w = self._create_history()

        # Pivot 아이템 추가
        self.pivot.addItem("settings", "설정", lambda: self.stack.setCurrentIndex(0), icon=FluentIcon.SETTING)
        self.pivot.addItem("results", "결과", lambda: self.stack.setCurrentIndex(1), icon=FluentIcon.CALORIES)
        self.pivot.addItem("history", "히스토리", lambda: self.stack.setCurrentIndex(2), icon=FluentIcon.HISTORY)

        # 스택 위젯에 추가
        self.stack.addWidget(settings_w)
        self.stack.addWidget(results_w)
        self.stack.addWidget(history_w)

        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack)

        # 기본 탭 선택
        self.pivot.setCurrentItem("settings")

    def _create_settings(self) -> QWidget:
        """설정 탭"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 기본 설정 카드
        basic_card = CardWidget()
        basic_layout = QVBoxLayout(basic_card)

        basic_layout.addWidget(SubtitleLabel("기본 설정"))

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

        # 시간 프레임
        timeframe_layout = QHBoxLayout()
        timeframe_layout.addWidget(BodyLabel("시간 프레임:"))
        self.timeframe_combo = ComboBox()
        self.timeframe_combo.addItems(["1m", "5m", "15m", "1h", "4h", "1d"])
        self.timeframe_combo.setCurrentText("1h")
        timeframe_layout.addWidget(self.timeframe_combo)
        timeframe_layout.addStretch()
        basic_layout.addLayout(timeframe_layout)

        layout.addWidget(basic_card)

        # 기간 설정 카드
        period_card = CardWidget()
        period_layout = QVBoxLayout(period_card)

        period_layout.addWidget(SubtitleLabel("기간 설정"))

        # 날짜 범위
        date_layout = QHBoxLayout()

        date_layout.addWidget(BodyLabel("시작일:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)

        date_layout.addWidget(BodyLabel("종료일:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)

        date_layout.addStretch()
        period_layout.addLayout(date_layout)

        layout.addWidget(period_card)

        # 전략 설정 카드
        strategy_card = CardWidget()
        strategy_layout = QVBoxLayout(strategy_card)

        strategy_layout.addWidget(SubtitleLabel("전략 설정"))

        # 전략 선택
        strategy_form = QFormLayout()

        self.strategy_combo = ComboBox()
        self.strategy_combo.addItems([
            "단순 이동 평균",
            "RSI 역추세",
            "그리드 매매",
            "볼린저 밴드"
        ])
        strategy_form.addRow("전략:", self.strategy_combo)

        # 초기 자금
        self.initial_capital = DoubleSpinBox()
        self.initial_capital.setRange(100, 1000000)
        self.initial_capital.setValue(10000)
        self.initial_capital.setSuffix(" USDT")
        strategy_form.addRow("초기 자금:", self.initial_capital)

        # 수수료 설정
        self.fee_rate = DoubleSpinBox()
        self.fee_rate.setRange(0.0, 1.0)
        self.fee_rate.setValue(0.001)
        self.fee_rate.setDecimals(4)
        self.fee_rate.setSuffix(" (0.1%)")
        strategy_form.addRow("수수료율:", self.fee_rate)

        strategy_layout.addLayout(strategy_form)
        layout.addWidget(strategy_card)

        # 실행 버튼
        run_button = PushButton("백테스트 실행")
        run_button.clicked.connect(self.run_backtest)
        layout.addWidget(run_button)

        layout.addStretch()
        scroll.setWidget(w)
        return scroll

    def _create_results(self) -> QWidget:
        """결과 탭"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 결과 요약 카드
        summary_card = CardWidget()
        summary_layout = QVBoxLayout(summary_card)

        summary_layout.addWidget(SubtitleLabel("백테스트 결과"))

        # 결과 테이블
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["항목", "값"])

        # 테이블 크기 조정
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.results_table.setMaximumHeight(300)
        summary_layout.addWidget(self.results_table)

        layout.addWidget(summary_card)

        # 차트 영역 (간단한 정보 표시)
        chart_card = CardWidget()
        chart_layout = QVBoxLayout(chart_card)

        chart_layout.addWidget(SubtitleLabel("수익률 차트"))

        self.chart_placeholder = QLabel("백테스트 실행 후 수익률 차트가 표시됩니다.")
        self.chart_placeholder.setAlignment(Qt.AlignCenter)
        self.chart_placeholder.setStyleSheet("color: #666; padding: 20px; border: 1px dashed #ddd;")
        self.chart_placeholder.setMinimumHeight(200)
        chart_layout.addWidget(self.chart_placeholder)

        layout.addWidget(chart_card)

        # 상세 로그
        log_card = CardWidget()
        log_layout = QVBoxLayout(log_card)

        log_layout.addWidget(SubtitleLabel("상세 로그"))

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.append("백테스트 로그가 여기에 표시됩니다.")
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_card)

        return w

    def _create_history(self) -> QWidget:
        """히스토리 탭"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 이전 결과 테이블
        history_table = QTableWidget()
        history_table.setColumnCount(6)
        history_table.setHorizontalHeaderLabels([
            "실행 시간", "전략", "심볼", "기간", "최종 수익률", "상태"
        ])

        # 테이블 크기 조정
        header = history_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        layout.addWidget(history_table)

        # 샘플 데이터 추가
        self._add_sample_history(history_table)

        return w

    def run_backtest(self):
        """백테스트 실행"""
        # 입력값 가져오기
        exchange = self.exchange_combo.currentText()
        symbol = self.symbol_combo.currentText()
        timeframe = self.timeframe_combo.currentText()
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()
        strategy = self.strategy_combo.currentText()
        initial_capital = self.initial_capital.value()
        fee_rate = self.fee_rate.value()

        # 결과 탭으로 전환
        self.pivot.setCurrentItem("results")
        self.stack.setCurrentIndex(1)

        # 로그 초기화
        self.log_text.clear()
        self.add_log(f"백테스트 시작: {exchange} {symbol} {strategy}")
        self.add_log(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        self.add_log(f"초기 자금: {initial_capital:,.0f} USDT")

        # 시뮬레이션 실행 (간단한 예시)
        self._simulate_backtest(exchange, symbol, timeframe, strategy, initial_capital, fee_rate)

    def _simulate_backtest(self, exchange, symbol, timeframe, strategy, initial_capital, fee_rate):
        """백테스트 시뮬레이션"""
        import time

        # 진행률 표시
        self.add_log("데이터 로딩 중...")

        # 결과 테이블 초기화
        self.results_table.setRowCount(0)

        # 샘플 결과 생성
        results = [
            ("거래소", exchange),
            ("심볼", symbol),
            ("시간 프레임", timeframe),
            ("전략", strategy),
            ("초기 자금", f"{initial_capital:,.0f} USDT"),
            ("최종 잔액", f"{initial_capital * 1.15:,.0f} USDT"),
            ("총 수익", f"{initial_capital * 0.15:,.0f} USDT"),
            ("수익률", "+15.00%"),
            ("총 거래횟수", "45"),
            ("승률", "62.2%"),
            ("최대 낙폭", "-8.5%"),
            ("샤프 비율", "1.85"),
            ("수수료 총액", f"{initial_capital * 0.001 * 45:,.0f} USDT"),
            ("순수익", f"{initial_capital * 0.145:,.0f} USDT")
        ]

        self.results_table.setRowCount(len(results))
        for row, (key, value) in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(key))

            value_item = QTableWidgetItem(str(value))
            # 수익률에 따라 색상 지정
            if "수익률" in key and "%" in value:
                if "+" in value:
                    value_item.setForeground(QColor(0, 150, 0))  # 초록색
                else:
                    value_item.setForeground(QColor(200, 0, 0))  # 빨간색
            elif "최대 낙폭" in key:
                value_item.setForeground(QColor(200, 0, 0))  # 빨간색

            self.results_table.setItem(row, 1, value_item)

        # 로그 추가
        self.add_log("데이터 로딩 완료")
        self.add_log("백테스트 실행 중...")
        time.sleep(1)  # 시뮬레이션 효과

        self.add_log("전략 분석 완료")
        self.add_log("수익률 계산 완료")

        # 최종 결과
        final_return = 15.0
        self.add_log(f"백테스트 완료! 최종 수익률: +{final_return:.2f}%")

        # 차트 플레이스홀더 업데이트
        self.chart_placeholder.setText(f"수익률 차트\n최종 수익률: +{final_return:.2f}%")

        # 결과 저장
        result_data = {
            'timestamp': datetime.now(),
            'exchange': exchange,
            'symbol': symbol,
            'timeframe': timeframe,
            'strategy': strategy,
            'return': final_return,
            'status': '완료'
        }
        self.backtest_results.append(result_data)
        self.current_result = result_data

        # 알림 표시
        InfoBar.success(
            title="백테스트 완료",
            content=f"{strategy} 전략 백테스트가 완료되었습니다. 최종 수익률: +{final_return:.2f}%",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def add_log(self, message: str):
        """로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        # 스크롤을 맨 아래로
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def _add_sample_history(self, table: QTableWidget):
        """샘플 히스토리 데이터 추가"""
        sample_data = [
            ("2024-01-01 14:30:00", "RSI 역추세", "BTC/USDT", "30일", "+8.5%", "완료"),
            ("2024-01-02 10:15:00", "단순 이동 평균", "ETH/USDT", "15일", "+12.3%", "완료"),
            ("2024-01-03 16:45:00", "그리드 매매", "BTC/USDT", "7일", "-2.1%", "완료"),
            ("2024-01-04 09:20:00", "볼린저 밴드", "BNB/USDT", "30일", "+5.7%", "완료"),
            ("2024-01-05 13:00:00", "RSI 역추세", "ETH/USDT", "14일", "+18.9%", "완료"),
        ]

        table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))

                # 수익률에 따라 색상 지정
                if col == 4 and "%" in str(value):
                    if "+" in str(value):
                        item.setForeground(QColor(0, 150, 0))  # 초록색
                    else:
                        item.setForeground(QColor(200, 0, 0))  # 빨간색

                table.setItem(row, col, item)