"""
데이터 페이지 - 단계적 복구 버전
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QScrollArea, QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, QDate, QThread
from qfluentwidgets import (
    CardWidget, TitleLabel, SubtitleLabel, BodyLabel,
    PushButton, SwitchButton, CheckBox, ProgressBar, ComboBox,
    InfoBar, InfoBarPosition, Pivot
)
from datetime import datetime, timedelta

# 거래소별 무기한 선물 심볼 매핑
EXCHANGE_PERPETUAL_SYMBOLS = {
    "binance": {
        "BTC": "BTC/USDT:USDT",
        "ETH": "ETH/USDT:USDT",
        "SOL": "SOL/USDT:USDT",
        "XRP": "XRP/USDT:USDT",
        "DOGE": "DOGE/USDT:USDT"
    },
    "okx": {
        "BTC": "BTC-USDT-SWAP",
        "ETH": "ETH-USDT-SWAP",
        "SOL": "SOL-USDT-SWAP",
        "XRP": "XRP-USDT-SWAP",
        "DOGE": "DOGE-USDT-SWAP"
    },
    "bybit": {
        "BTC": "BTC/USDT:USDT",
        "ETH": "ETH/USDT:USDT",
        "SOL": "SOL/USDT:USDT",
        "XRP": "XRP/USDT:USDT",
        "DOGE": "DOGE/USDT:USDT"
    },
    "bitget": {
        "BTC": "BTCUSDT",
        "ETH": "ETHUSDT",
        "SOL": "SOLUSDT",
        "XRP": "XRPUSDT",
        "DOGE": "DOGEUSDT"
    },
    "huobi": {
        "BTC": "btcusdt",
        "ETH": "ethusdt",
        "SOL": "solusdt",
        "XRP": "xrpusdt",
        "DOGE": "dogeusdt"
    },
    "kucoin": {
        "BTC": "BTC-USDT",
        "ETH": "ETH-USDT",
        "SOL": "SOL-USDT",
        "XRP": "XRP-USDT",
        "DOGE": "DOGE-USDT"
    },
    "gate": {
        "BTC": "BTC_USDT",
        "ETH": "ETH_USDT",
        "SOL": "SOL_USDT",
        "XRP": "XRP_USDT",
        "DOGE": "DOGE_USDT"
    },
    "upbit": {
        "BTC": "KRW-BTC",  # Upbit는 현물만
        "ETH": "KRW-ETH",
        "SOL": "KRW-SOL",
        "XRP": "KRW-XRP",
        "DOGE": "KRW-DOGE"
    },
    "bithumb": {
        "BTC": "KRW-BTC",  # Bithumb는 현물만
        "ETH": "KRW-ETH",
        "SOL": "KRW-SOL",
        "XRP": "KRW-XRP",
        "DOGE": "KRW-DOGE"
    }
}


class DataPageSimple(QWidget):
    """데이터 페이지 - 단계적 복구"""

    def __init__(self):
        super().__init__()

        # 레포지토리는 나중에 초기화
        self.candles_repo = None
        self.symbols_repo = None

        # 워커 관련
        self.collector_thread = None
        self.collector_worker = None
        self.collection_button = None

        # 선택된 심볼들
        self.selected_symbols = []

        self._init_ui()
        self._update_symbols()

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 10, 10)
        layout.setSpacing(15)

        # 타이틀
        title = TitleLabel("데이터 수집 및 관리")
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
            text="데이터 수집",
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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 1. 거래소 섹션
        exchange_card = CardWidget()
        exchange_layout = QVBoxLayout(exchange_card)

        exchange_layout.addWidget(SubtitleLabel("1. 거래소 선택"))

        # 거래소 선택
        exchange_select_layout = QHBoxLayout()
        exchange_select_layout.addWidget(BodyLabel("거래소:"))
        self.exchange_combo = ComboBox()

        # 주요 거래소 목록
        self.exchange_combo.addItems([
            "OKX (#4)", "Binance (#1)", "Bybit (#3)", "Bitget (#6)",
            "KuCoin (#8)", "Gate (#9)", "MEXC (#10)", "Huobi (#15)",
            "Kraken (#20)", "Upbit", "Bithumb", "Coinone"
        ])
        self.exchange_combo.setCurrentText("OKX (#4)")
        self.exchange_combo.currentTextChanged.connect(self._update_symbols)
        exchange_select_layout.addWidget(self.exchange_combo)
        exchange_select_layout.addStretch()
        exchange_layout.addLayout(exchange_select_layout)

        # 수집 상태 표시
        self.exchange_status_label = BodyLabel("선택된 거래소 대기 중...")
        exchange_layout.addWidget(self.exchange_status_label)

        layout.addWidget(exchange_card)

        # 2. 심볼 섹션
        symbols_card = CardWidget()
        symbols_layout = QVBoxLayout(symbols_card)

        symbols_layout.addWidget(SubtitleLabel("2. 심볼 선택"))

        # 심볼 선택 정보
        symbols_info = BodyLabel("BTC, ETH, SOL, XRP, DOGE 거래소별 무기한 선물 심볼")
        symbols_layout.addWidget(symbols_info)

        # 심볼 선택 테이블
        self.symbols_table = QTableWidget()
        self.symbols_table.setColumnCount(3)
        self.symbols_table.setHorizontalHeaderLabels(["선택", "코인", "심볼"])

        # 테이블 크기 조정
        header = self.symbols_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 선택
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 코인
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 심볼

        self.symbols_table.setMaximumHeight(250)
        symbols_layout.addWidget(self.symbols_table)

        # 심볼 수집 상태 표시
        self.symbol_status_label = BodyLabel("선택된 심볼 대기 중...")
        symbols_layout.addWidget(self.symbol_status_label)

        layout.addWidget(symbols_card)

        # 3. 기간 섹션
        period_card = CardWidget()
        period_layout = QVBoxLayout(period_card)

        period_layout.addWidget(SubtitleLabel("3. 기간 설정"))

        # 기간 선택
        period_select_layout = QHBoxLayout()
        period_select_layout.addWidget(BodyLabel("수집 기간:"))
        self.period_combo = ComboBox()
        self.period_combo.addItems(["최근 7일", "최근 30일", "최근 90일", "최근 1년", "전체 기간"])
        self.period_combo.setCurrentText("최근 30일")
        period_select_layout.addWidget(self.period_combo)
        period_select_layout.addStretch()
        period_layout.addLayout(period_select_layout)

        # 진행률 표시줄 (기간 섹션에 포함)
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        period_layout.addWidget(self.progress_bar)

        # 데이터 수집 실행 버튼 (좌측 정렬, 강조 색상)
        period_button_container = QWidget()
        period_button_layout = QHBoxLayout(period_button_container)
        period_button_layout.setContentsMargins(0, 0, 0, 0)

        self.collect_button = PushButton("데이터 수집 실행")
        self.collect_button.setStyleSheet("""
            PushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            PushButton:hover {
                background-color: #106ebe;
            }
            PushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.collect_button.clicked.connect(self.start_data_collection)
        self.collect_button.setMaximumWidth(200)
        period_button_layout.addWidget(self.collect_button)
        period_button_layout.addStretch()

        period_layout.addWidget(period_button_container)

        # 수집 상태 표시
        self.status_label = BodyLabel("수집 대기 중...")
        period_layout.addWidget(self.status_label)

        layout.addWidget(period_card)

        # 남은 공간 채우기
        layout.addStretch()

        # 초기 심볼 데이터 설정
        self._update_symbols()

        scroll.setWidget(widget)
        return scroll

    def _update_symbols(self):
        """선택된 거래소에 맞는 심볼 업데이트"""
        print("[DEBUG] _update_symbols() 호출됨")
        try:
            # 선택된 거래소에서 실제 거래소 ID 추출
            exchange_text = self.exchange_combo.currentText()
            print(f"[DEBUG] 현재 선택된 거래소 텍스트: '{exchange_text}'")

            # 거래소 ID 매핑
            exchange_mapping = {
                "OKX (#4)": "okx",
                "Binance (#1)": "binance",
                "Bybit (#3)": "bybit",
                "Bitget (#6)": "bitget",
                "KuCoin (#8)": "kucoin",
                "Gate (#9)": "gate",
                "MEXC (#10)": "mexc",
                "Huobi (#15)": "huobi",
                "Kraken (#20)": "kraken",
                "Upbit": "upbit",
                "Bithumb": "bithumb",
                "Coinone": "coinone"
            }

            exchange_id = exchange_mapping.get(exchange_text, "okx")
            print(f"[DEBUG] 매핑된 거래소 ID: {exchange_id}")

            # 거래소별 심볼 가져오기
            symbols_data = EXCHANGE_PERPETUAL_SYMBOLS.get(exchange_id, EXCHANGE_PERPETUAL_SYMBOLS["okx"])
            print(f"[DEBUG] 심볼 데이터: {symbols_data}")

            # 테이블 설정
            old_row_count = self.symbols_table.rowCount()
            print(f"[DEBUG] 이전 테이블 행 수: {old_row_count}")
            self.symbols_table.setRowCount(len(symbols_data))
            print(f"[DEBUG] 새 테이블 행 수 설정: {len(symbols_data)}")

            for i, (coin, symbol) in enumerate(symbols_data.items()):
                print(f"[DEBUG] 행 {i} 처리 중: {coin} -> {symbol}")
                # 체크박스
                checkbox = QCheckBox()
                checkbox.setChecked(True)  # 기본적으로 모두 선택
                self.symbols_table.setCellWidget(i, 0, checkbox)
                print(f"[DEBUG] 체크박스 생성 및 설정 완료: checked={checkbox.isChecked()}")

                # 코인명
                coin_item = QTableWidgetItem(coin)
                self.symbols_table.setItem(i, 1, coin_item)
                print(f"[DEBUG] 코인명 아이템 설정 완료: {coin}")

                # 심볼명
                symbol_item = QTableWidgetItem(symbol)
                self.symbols_table.setItem(i, 2, symbol_item)
                print(f"[DEBUG] 심볼명 아이템 설정 완료: {symbol}")

            print(f"[DEBUG] 심볼 업데이트 완료: {exchange_id}, {len(symbols_data)}개 심볼")

            # 설정된 심볼 확인
            final_row_count = self.symbols_table.rowCount()
            print(f"[DEBUG] 최종 테이블 행 수: {final_row_count}")

        except Exception as e:
            print(f"[DEBUG] 심볼 업데이트 실패: {str(e)}")
            import traceback
            traceback.print_exc()

    
    def start_data_collection(self):
        """데이터 수집 시작 (거래소 AND 심볼 AND 기간 조건)"""
        print("="*50)
        print("[DEBUG] 데이터 수집 버튼 클릭됨!")
        print(f"[DEBUG] 버튼 상태: enabled={self.collect_button.isEnabled()}")
        print(f"[DEBUG] 버튼 텍스트: '{self.collect_button.text()}'")
        print("="*50)

        try:
            # 0. 버튼 상태 확인 및 비활성화
            if not self.collect_button.isEnabled():
                print("[DEBUG] 버튼이 이미 비활성화되어 있음")
                return

            self.collect_button.setEnabled(False)
            self.collect_button.setText("데이터 수집 중...")

            # 1. 거래소 확인
            print("[DEBUG] 거래소 선택 확인 중...")
            try:
                exchange_text = self.exchange_combo.currentText()
                print(f"[DEBUG] 선택된 거래소 텍스트: '{exchange_text}'")
            except Exception as e:
                print(f"[DEBUG] 거래소 텍스트 가져오기 실패: {str(e)}")
                self.collect_button.setEnabled(True)
                self.collect_button.setText("데이터 수집 실행")
                return

            exchange_mapping = {
                "OKX (#4)": "okx",
                "Binance (#1)": "binance",
                "Bybit (#3)": "bybit",
                "Bitget (#6)": "bitget",
                "KuCoin (#8)": "kucoin",
                "Gate (#9)": "gate",
                "MEXC (#10)": "mexc",
                "Huobi (#15)": "huobi",
                "Kraken (#20)": "kraken",
                "Upbit": "upbit",
                "Bithumb": "bithumb",
                "Coinone": "coinone"
            }
            exchange_id = exchange_mapping.get(exchange_text, "okx")
            print(f"[DEBUG] 거래소 ID: {exchange_id}")

            # 2. 선택된 심볼 확인
            print("[DEBUG] 심볼 선택 확인 중...")
            try:
                table_row_count = self.symbols_table.rowCount()
                print(f"[DEBUG] 테이블 행 수: {table_row_count}")

                selected_symbols = []
                for i in range(table_row_count):
                    checkbox = self.symbols_table.cellWidget(i, 0)
                    if checkbox:
                        is_checked = checkbox.isChecked()
                        print(f"[DEBUG] 행 {i}: 체크박스 상태={is_checked}")
                        if is_checked:
                            try:
                                coin_item = self.symbols_table.item(i, 1)
                                symbol_item = self.symbols_table.item(i, 2)
                                if coin_item and symbol_item:
                                    coin = coin_item.text()
                                    symbol = symbol_item.text()
                                    selected_symbols.append((coin, symbol))
                                    print(f"[DEBUG] 선택된 심볼: {coin} -> {symbol}")
                            except Exception as e:
                                print(f"[DEBUG] 행 {i}에서 아이템 가져오기 실패: {str(e)}")
                print(f"[DEBUG] 총 선택된 심볼 수: {len(selected_symbols)}")
            except Exception as e:
                print(f"[DEBUG] 심볼 선택 확인 실패: {str(e)}")
                self.collect_button.setEnabled(True)
                self.collect_button.setText("데이터 수집 실행")
                return

            if not selected_symbols:
                print("[DEBUG] 선택된 심볼이 없음 - InfoBar 표시")
                from qfluentwidgets import InfoBar, InfoBarPosition
                InfoBar.warning(
                    title="심볼 선택 필요",
                    content="수집할 심볼을 선택해주세요.",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                self.collect_button.setEnabled(True)
                self.collect_button.setText("데이터 수집 실행")
                return

            # 3. 기간 확인
            print("[DEBUG] 기간 선택 확인 중...")
            try:
                period_text = self.period_combo.currentText()
                print(f"[DEBUG] 선택된 기간: '{period_text}'")
            except Exception as e:
                print(f"[DEBUG] 기간 텍스트 가져오기 실패: {str(e)}")
                self.collect_button.setEnabled(True)
                self.collect_button.setText("데이터 수집 실행")
                return

            # 4. UI 상태 업데이트
            print("[DEBUG] UI 상태 업데이트 중...")
            try:
                self.exchange_status_label.setText(f"선택: {exchange_text}")
                self.symbol_status_label.setText(f"선택: {len(selected_symbols)}개 심볼")
                self.status_label.setText("데이터 수집 중...")
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                print("[DEBUG] UI 상태 업데이트 완료")
            except Exception as e:
                print(f"[DEBUG] UI 상태 업데이트 실패: {str(e)}")

            # 5. 최종 로그 출력
            print("="*50)
            print(f"[DEBUG] 데이터 수집 시작 (AND 조건):")
            print(f"  - 거래소: {exchange_text} ({exchange_id})")
            print(f"  - 기간: {period_text}")
            print(f"  - 심볼: {[coin for coin, _ in selected_symbols]}")
            print("="*50)

            # 6. 실제 데이터 수집 로직 호출
            symbol_list = [symbol for _, symbol in selected_symbols]
            print(f"[DEBUG] 워커 시작 준비: {exchange_id}, {len(symbol_list)}개 심볼")

            try:
                self._start_collection_with_worker(exchange_id, symbol_list, period_text)
                print("[DEBUG] 워커 시작 호출 완료")
            except Exception as e:
                print(f"[DEBUG] 워커 시작 실패: {str(e)}")
                import traceback
                traceback.print_exc()
                raise

        except Exception as e:
            print(f"[DEBUG] 데이터 수집 시작 실패: {str(e)}")
            import traceback
            traceback.print_exc()

            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.error(
                title="데이터 수집 실패",
                content=f"데이터 수집 시작에 실패했습니다: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=-1,
                parent=self
            )
            # 실패 시 버튼 상태 복원
            print("[DEBUG] 버튼 상태 복원")
            self._reset_buttons()

    def _start_collection_with_worker(self, exchange_id: str, symbols: list, collection_type: str):
        """DataCollectorWorker를 사용한 실제 데이터 수집"""
        try:
            # 워커 스레드 생성
            from workers.data_collector_worker import DataCollectorWorker
            self.collector_worker = DataCollectorWorker()
            self.collector_thread = QThread()

            # 워커를 스레드로 이동
            self.collector_worker.moveToThread(self.collector_thread)

            # 시그널 연결
            self.collector_worker.progress_updated.connect(self._on_progress_updated)
            self.collector_worker.collection_completed.connect(self._on_collection_completed)
            self.collector_worker.error_occurred.connect(self._on_error_occurred)
            self.collector_worker.log_message.connect(self._on_log_message)

            # 스레드 시작
            self.collector_thread.started.connect(lambda: self._start_worker(collection_type, exchange_id, symbols))
            self.collector_thread.start()

            # 성공 메시지
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.success(
                title="데이터 수집 시작",
                content=f"{exchange_id.upper()}에서 {len(symbols)}개 심볼 데이터 수집을 시작합니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

        except Exception as e:
            print(f"[DEBUG] Worker 시작 실패: {str(e)}")
            # 실패 시 버튼 상태 복원
            self._reset_buttons()

    def _start_worker(self, period_text: str, exchange_id: str, symbols: list):
        """워커 시작"""
        try:
            # 기간 설정 계산
            from datetime import datetime, timedelta

            if period_text == "최근 7일":
                start_date = datetime.now() - timedelta(days=7)
            elif period_text == "최근 30일":
                start_date = datetime.now() - timedelta(days=30)
            elif period_text == "최근 90일":
                start_date = datetime.now() - timedelta(days=90)
            elif period_text == "최근 1년":
                start_date = datetime.now() - timedelta(days=365)
            else:  # 전체 기간
                start_date = datetime.now() - timedelta(days=365)  # 1년로 기본 설정

            print(f"[DEBUG] 기간 설정: {period_text} ({start_date.strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')})")

            # 워커의 backfill_data 메서드 호출
            self.collector_worker.backfill_data(symbols, start_date, exchange_id)

        except Exception as e:
            print(f"[DEBUG] 워커 실행 실패: {str(e)}")
            self.collector_worker.error_occurred.emit(f"워커 실행 실패: {str(e)}")

    def _on_progress_updated(self, message: str, current: int, total: int):
        """진행률 업데이트"""
        progress = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)
        print(f"[PROGRESS] {message} ({current}/{total}) - {progress}%")

    def _on_collection_completed(self):
        """수집 완료"""
        self._reset_buttons()
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.success(
            title="수집 완료",
            content="데이터 수집이 완료되었습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

    def _on_error_occurred(self, error_message: str):
        """에러 발생"""
        self._reset_buttons()
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.error(
            title="수집 에러",
            content=error_message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=-1,
            parent=self
        )

    def _on_log_message(self, message: str):
        """로그 메시지"""
        print(f"[COLLECTION] {message}")

    def _reset_buttons(self):
        """버튼 상태 리셋"""
        self.collect_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("수집 대기 중...")
        self.exchange_status_label.setText("선택된 거래소 대기 중...")
        self.symbol_status_label.setText("선택된 심볼 대기 중...")

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

        # 날짜 범위 설정
        date_layout = QHBoxLayout()
        date_layout.addWidget(BodyLabel("시작일:"))

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)

        date_layout.addWidget(BodyLabel("종료일:"))

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)

        date_layout.addStretch()
        query_layout.addLayout(date_layout)

        # 조회 버튼
        query_button = PushButton("데이터 조회")
        query_button.clicked.connect(self.query_data)
        query_layout.addWidget(query_button)

        layout.addWidget(query_card)

        # 데이터 테이블
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels(["시간", "거래소", "심볼", "시가", "고가", "저가", "종가", "거래량"])

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

    def _load_initial_data_safe(self):
        """안전한 초기 데이터 로드"""
        try:
            # 나중에 레포지토리를 안전하게 초기화
            self.symbols_table.setRowCount(3)

            # 샘플 데이터 표시
            sample_data = [
                ("OKX", "BTC/USDT", "활성", "기본 설정"),
                ("OKX", "ETH/USDT", "활성", "기본 설정"),
                ("OKX", "BNB/USDT", "활성", "기본 설정"),
            ]

            for row, (exchange, symbol, status, config) in enumerate(sample_data):
                self.symbols_table.setItem(row, 0, QTableWidgetItem(exchange))
                self.symbols_table.setItem(row, 1, QTableWidgetItem(symbol))
                self.symbols_table.setItem(row, 2, QTableWidgetItem(status))
                self.symbols_table.setItem(row, 3, QTableWidgetItem(config))

        except Exception as e:
            InfoBar.warning(
                title="로딩 경고",
                content=f"심볼 데이터 로딩 중 오류: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def _show_empty_state(self):
        """빈 상태 표시"""
        self.data_table.setRowCount(1)
        item = QTableWidgetItem("데이터를 조회하려면 설정 탭에서 날짜를 선택하고 조회 버튼을 클릭하세요.")
        item.setTextAlignment(Qt.AlignCenter)
        self.data_table.setSpan(0, 0, 1, 8)
        self.data_table.setItem(0, 0, item)

    def query_data(self):
        """데이터 조회"""
        # 샘플 데이터 표시
        self.data_table.setRowCount(5)
        sample_candles = [
            ("2024-01-01 00:00:00", "OKX", "BTC/USDT", "42000", "42500", "41800", "42300", "150.5"),
            ("2024-01-01 01:00:00", "OKX", "BTC/USDT", "42300", "42800", "42000", "42600", "180.2"),
            ("2024-01-01 02:00:00", "OKX", "BTC/USDT", "42600", "42900", "42200", "42700", "165.8"),
            ("2024-01-01 03:00:00", "OKX", "BTC/USDT", "42700", "43100", "42400", "43000", "195.3"),
            ("2024-01-01 04:00:00", "OKX", "BTC/USDT", "43000", "43200", "42600", "42800", "142.7"),
        ]

        for row, data in enumerate(sample_candles):
            for col, value in enumerate(data):
                self.data_table.setItem(row, col, QTableWidgetItem(str(value)))

        InfoBar.success(
            title="조회 완료",
            content=f"{len(sample_candles)}개의 데이터를 조회했습니다.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )