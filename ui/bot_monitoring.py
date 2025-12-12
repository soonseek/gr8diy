"""
봇 모니터링 위젯 - CCXT
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from qfluentwidgets import SubtitleLabel, PushButton, InfoBar, InfoBarPosition
from database.repository import PositionsRepository, OrdersRepository
from config.exchanges import SUPPORTED_EXCHANGES
from utils.logger import logger


class BotMonitoringWidget(QWidget):
    """봇 모니터링 위젯"""
    
    def __init__(self):
        super().__init__()
        self.positions_repo = PositionsRepository()
        self.orders_repo = OrdersRepository()
        
        self.bot_workers = {}
        
        self._init_ui()
        
        # 자동 새로고침 (5초)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_data)
        self.refresh_timer.start(5000)
    
    def _init_ui(self):
        """UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 컨트롤
        title_layout = QHBoxLayout()
        title = SubtitleLabel("실시간 모니터링")
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        refresh_btn = PushButton("새로고침")
        refresh_btn.setFixedHeight(28)
        refresh_btn.clicked.connect(self._refresh_data)
        title_layout.addWidget(refresh_btn)
        
        self.stop_keep_btn = PushButton("전체 봇만 중지")
        self.stop_keep_btn.setFixedHeight(28)
        self.stop_keep_btn.clicked.connect(lambda: self._stop_all_bots(clean=False))
        title_layout.addWidget(self.stop_keep_btn)
        
        self.stop_clean_btn = PushButton("전체 봇 중지(청산)")
        self.stop_clean_btn.setFixedHeight(28)
        self.stop_clean_btn.setStyleSheet("background-color: #e74c3c; color: white; border: none;")
        self.stop_clean_btn.clicked.connect(lambda: self._stop_all_bots(clean=True))
        title_layout.addWidget(self.stop_clean_btn)
        
        layout.addLayout(title_layout)
        
        # 포지션 테이블
        layout.addWidget(SubtitleLabel("열린 포지션"))
        
        self.position_table = QTableWidget(0, 10)
        self.position_table.setHorizontalHeaderLabels([
            "거래소", "심볼", "방향", "수량", "진입가", "현재가", "손익", "레버리지", "액션1", "액션2"
        ])
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.position_table.verticalHeader().setVisible(False)
        self.position_table.setMinimumHeight(300)
        layout.addWidget(self.position_table)
        
        # 주문 테이블
        layout.addWidget(SubtitleLabel("열린 주문"))
        
        self.order_table = QTableWidget(0, 6)
        self.order_table.setHorizontalHeaderLabels([
            "심볼", "타입", "방향", "가격", "수량", "상태"
        ])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.setMinimumHeight(200)
        layout.addWidget(self.order_table)
    
    def _refresh_data(self):
        """데이터 새로고침"""
        try:
            self._refresh_positions()
            self._refresh_orders()
        except Exception as e:
            logger.error("Monitoring", f"새로고침 실패: {str(e)}")
    
    def _refresh_positions(self):
        """포지션 새로고침"""
        self.position_table.setRowCount(0)
        
        if not self.bot_workers:
            return
        
        # 각 봇의 클라이언트로 포지션 조회
        for symbol, worker in self.bot_workers.items():
            try:
                client = worker.client
                positions = client.get_positions(symbol)
                
                if not positions:
                    continue
                
                for pos in positions:
                    pos_size = pos.get('size', 0)
                    entry_price = pos.get('entry_price', 0)
                    # 크기 > 0이고 진입가도 있어야 유효한 포지션
                    if pos_size == 0 or entry_price == 0:
                        continue
                    
                    row = self.position_table.rowCount()
                    self.position_table.insertRow(row)
                    
                    # 거래소
                    ex_name = SUPPORTED_EXCHANGES.get(worker.config.get('exchange_id', ''), {}).get('name', '')
                    self.position_table.setItem(row, 0, QTableWidgetItem(ex_name))
                    
                    # 심볼
                    self.position_table.setItem(row, 1, QTableWidgetItem(pos.get('symbol', '')))
                    
                    # 방향
                    side = pos.get('side', '')
                    self.position_table.setItem(row, 2, QTableWidgetItem(side.upper()))
                    
                    # 수량
                    self.position_table.setItem(row, 3, QTableWidgetItem(f"{pos_size:.4f}"))
                    
                    # 진입가
                    entry_price = pos.get('entry_price', 0)
                    self.position_table.setItem(row, 4, QTableWidgetItem(f"{entry_price:.2f}"))
                    
                    # 현재가
                    mark_price = pos.get('mark_price', 0)
                    self.position_table.setItem(row, 5, QTableWidgetItem(f"{mark_price:.2f}"))
                    
                    # 손익
                    upl = pos.get('unrealized_pnl', 0)
                    upl_text = f"{upl:.2f} USDT"
                    upl_item = QTableWidgetItem(upl_text)
                    if upl >= 0:
                        upl_item.setForeground(Qt.green)
                    else:
                        upl_item.setForeground(Qt.red)
                    self.position_table.setItem(row, 6, upl_item)
                    
                    # 레버리지
                    lev = pos.get('leverage', 1)
                    self.position_table.setItem(row, 7, QTableWidgetItem(f"{lev}x"))
                    
                    # 액션 버튼
                    sym = pos.get('symbol', '')
                    
                    # 봇만 중지
                    stop_keep = PushButton("봇만 중지")
                    stop_keep.setFixedHeight(28)
                    # 클로저로 심볼 캡처
                    def make_stop_keep(s):
                        return lambda: self._stop_single_bot(s, False)
                    stop_keep.clicked.connect(make_stop_keep(sym))
                    self.position_table.setCellWidget(row, 8, stop_keep)
                    
                    # 청산
                    stop_clean = PushButton("청산")
                    stop_clean.setFixedHeight(28)
                    stop_clean.setStyleSheet("background-color: #e74c3c; color: white; border: none;")
                    def make_stop_clean(s):
                        return lambda: self._stop_single_bot(s, True)
                    stop_clean.clicked.connect(make_stop_clean(sym))
                    self.position_table.setCellWidget(row, 9, stop_clean)
                    
            except Exception as e:
                logger.error("Monitoring", f"{symbol} 포지션 조회 실패: {str(e)}")
    
    def _refresh_orders(self):
        """주문 새로고침"""
        self.order_table.setRowCount(0)
        
        if not self.bot_workers:
            return
        
        # 각 봇의 클라이언트로 주문 조회
        for symbol, worker in self.bot_workers.items():
            try:
                client = worker.client
                orders = client.get_open_orders(symbol)
                
                if not orders:
                    continue
                
                for order in orders:
                    row = self.order_table.rowCount()
                    self.order_table.insertRow(row)
                    
                    # 심볼
                    self.order_table.setItem(row, 0, QTableWidgetItem(order.get('symbol', '')))
                    
                    # 타입
                    ord_type = order.get('type', '')
                    self.order_table.setItem(row, 1, QTableWidgetItem(ord_type))
                    
                    # 방향
                    side = order.get('side', '')
                    self.order_table.setItem(row, 2, QTableWidgetItem(side.upper()))
                    
                    # 가격
                    price = order.get('price', 0)
                    self.order_table.setItem(row, 3, QTableWidgetItem(f"{price:.2f}"))
                    
                    # 수량
                    size = order.get('amount', 0)
                    self.order_table.setItem(row, 4, QTableWidgetItem(f"{size:.4f}"))
                    
                    # 상태
                    status = order.get('status', '')
                    self.order_table.setItem(row, 5, QTableWidgetItem(status))
                    
            except Exception as e:
                logger.error("Monitoring", f"{symbol} 주문 조회 실패: {str(e)}")
    
    def set_bot_workers(self, bot_workers: dict):
        """봇 워커 참조 설정"""
        self.bot_workers = bot_workers
    
    def _stop_all_bots(self, clean: bool):
        """전체 봇 중지"""
        if not self.bot_workers:
            InfoBar.warning("실행 중인 봇 없음", "", parent=self)
            return
        
        mode = "청산 후 중지" if clean else "봇만 중지"
        
        for symbol, worker in list(self.bot_workers.items()):
            worker.stop_trading(clean_mode=clean)
            logger.info("Monitoring", f"{symbol} 전체 봇 중지: {mode}")
        
        InfoBar.success("전체 봇 중지", f"{len(self.bot_workers)}개 - {mode}", parent=self)
    
    def _stop_single_bot(self, symbol: str, clean: bool):
        """개별 봇 중지"""
        if symbol not in self.bot_workers:
            InfoBar.warning("봇 없음", f"{symbol} 실행 중 아님", parent=self)
            return
        
        mode = "청산" if clean else "봇만 중지"
        
        worker = self.bot_workers[symbol]
        worker.stop_trading(clean_mode=clean)
        
        logger.info("Monitoring", f"{symbol} 개별 봇 중지: {mode}")
        InfoBar.success(f"{symbol} 봇 중지", mode, parent=self)
