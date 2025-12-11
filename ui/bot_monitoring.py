"""
봇 모니터링 위젯
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from qfluentwidgets import CardWidget, SubtitleLabel, BodyLabel, PushButton
from database.repository import PositionsRepository, OrdersRepository
from utils.crypto import CredentialManager
from config.settings import CREDENTIALS_PATH
from api.okx_client import OKXClient
from utils.logger import logger
from qfluentwidgets import InfoBar, InfoBarPosition


class BotMonitoringWidget(QWidget):
    """봇 모니터링 위젯"""
    
    def __init__(self):
        super().__init__()
        self.positions_repo = PositionsRepository()
        self.orders_repo = OrdersRepository()
        self.credential_manager = CredentialManager(CREDENTIALS_PATH)
        
        # OKX 클라이언트
        self.okx_client = None
        self._init_okx_client()
        
        # 봇 워커 참조 (외부에서 설정)
        self.bot_workers = {}
        
        self._init_ui()
        
        # 자동 새로고침 타이머 (5초마다)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_data)
        self.refresh_timer.start(5000)
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 타이틀 및 컨트롤
        title_layout = QHBoxLayout()
        title = SubtitleLabel("실시간 모니터링")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        refresh_btn = PushButton("새로고침")
        refresh_btn.clicked.connect(self._refresh_data)
        title_layout.addWidget(refresh_btn)
        
        # 전체 봇 중지 버튼들
        self.stop_keep_btn = PushButton("전체 봇만 중지")
        self.stop_keep_btn.clicked.connect(lambda: self._stop_all_bots(clean=False))
        title_layout.addWidget(self.stop_keep_btn)
        
        self.stop_clean_btn = PushButton("전체 봇 중지(청산)")
        self.stop_clean_btn.clicked.connect(lambda: self._stop_all_bots(clean=True))
        self.stop_clean_btn.setStyleSheet("background-color: #e74c3c;")
        title_layout.addWidget(self.stop_clean_btn)
        
        layout.addLayout(title_layout)
        
        # 포지션 테이블
        position_card = CardWidget()
        position_layout = QVBoxLayout(position_card)
        
        position_title = SubtitleLabel("열린 포지션")
        position_layout.addWidget(position_title)
        
        self.position_table = QTableWidget(0, 9)
        self.position_table.setHorizontalHeaderLabels([
            "심볼", "방향", "수량", "진입가", "현재가", "손익", "레버리지", "액션1", "액션2"
        ])
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        position_layout.addWidget(self.position_table)
        
        layout.addWidget(position_card)
        
        # 주문 테이블
        order_card = CardWidget()
        order_layout = QVBoxLayout(order_card)
        
        order_title = SubtitleLabel("열린 주문")
        order_layout.addWidget(order_title)
        
        self.order_table = QTableWidget(0, 6)
        self.order_table.setHorizontalHeaderLabels([
            "심볼", "타입", "방향", "가격", "수량", "상태"
        ])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        order_layout.addWidget(self.order_table)
        
        layout.addWidget(order_card)
    
    def _init_okx_client(self):
        """OKX 클라이언트 초기화"""
        try:
            creds = self.credential_manager.get_okx_credentials()
            if all(creds.values()):
                self.okx_client = OKXClient(
                    creds['api_key'],
                    creds['secret'],
                    creds['passphrase']
                )
        except Exception as e:
            logger.error("Monitoring", f"OKX 클라이언트 초기화 실패: {str(e)}")
    
    def _refresh_data(self):
        """데이터 새로고침"""
        if not self.okx_client:
            return
        
        try:
            # 포지션 조회
            self._refresh_positions()
            
            # 주문 조회
            self._refresh_orders()
            
        except Exception as e:
            logger.error("Monitoring", f"데이터 새로고침 실패: {str(e)}")
    
    def _refresh_positions(self):
        """포지션 새로고침"""
        self.position_table.setRowCount(0)
        
        # OKX에서 모든 포지션 조회
        positions = self.okx_client.get_positions()
        if not positions:
            return
        
        for pos in positions:
            pos_size = float(pos.get('pos', 0))
            if pos_size == 0:
                continue
            
            row = self.position_table.rowCount()
            self.position_table.insertRow(row)
            
            # 심볼
            self.position_table.setItem(row, 0, QTableWidgetItem(pos.get('instId', '')))
            
            # 방향
            side = pos.get('posSide', '')
            self.position_table.setItem(row, 1, QTableWidgetItem(side.upper()))
            
            # 수량
            self.position_table.setItem(row, 2, QTableWidgetItem(str(abs(pos_size))))
            
            # 진입가
            avg_px = float(pos.get('avgPx', 0))
            self.position_table.setItem(row, 3, QTableWidgetItem(f"{avg_px:.2f}"))
            
            # 현재가
            mark_px = float(pos.get('markPx', 0))
            self.position_table.setItem(row, 4, QTableWidgetItem(f"{mark_px:.2f}"))
            
            # 손익
            upl = float(pos.get('upl', 0))
            upl_ratio = float(pos.get('uplRatio', 0)) * 100
            upl_text = f"{upl:.2f} ({upl_ratio:.2f}%)"
            upl_item = QTableWidgetItem(upl_text)
            if upl >= 0:
                upl_item.setForeground(Qt.green)
            else:
                upl_item.setForeground(Qt.red)
            self.position_table.setItem(row, 5, upl_item)
            
            # 레버리지
            lever = pos.get('lever', '1')
            self.position_table.setItem(row, 6, QTableWidgetItem(f"{lever}x"))
            
            # 액션 버튼들
            symbol_name = pos.get('instId', '')
            
            # 봇만 중지 버튼
            stop_keep_btn = PushButton("봇만 중지")
            stop_keep_btn.setFixedHeight(28)
            stop_keep_btn.clicked.connect(
                lambda checked, s=symbol_name: self._stop_single_bot(s, clean=False)
            )
            self.position_table.setCellWidget(row, 7, stop_keep_btn)
            
            # 봇 중지(청산) 버튼
            stop_clean_btn = PushButton("청산")
            stop_clean_btn.setFixedHeight(28)
            stop_clean_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            stop_clean_btn.clicked.connect(
                lambda checked, s=symbol_name: self._stop_single_bot(s, clean=True)
            )
            self.position_table.setCellWidget(row, 8, stop_clean_btn)
    
    def _refresh_orders(self):
        """주문 새로고침"""
        self.order_table.setRowCount(0)
        
        # OKX에서 미체결 주문 조회
        orders = self.okx_client.get_open_orders()
        if not orders:
            return
        
        for order in orders:
            row = self.order_table.rowCount()
            self.order_table.insertRow(row)
            
            # 심볼
            self.order_table.setItem(row, 0, QTableWidgetItem(order.get('instId', '')))
            
            # 타입
            ord_type = order.get('ordType', '')
            self.order_table.setItem(row, 1, QTableWidgetItem(ord_type))
            
            # 방향
            side = order.get('side', '')
            self.order_table.setItem(row, 2, QTableWidgetItem(side.upper()))
            
            # 가격
            px = float(order.get('px', 0))
            self.order_table.setItem(row, 3, QTableWidgetItem(f"{px:.2f}"))
            
            # 수량
            sz = float(order.get('sz', 0))
            self.order_table.setItem(row, 4, QTableWidgetItem(f"{sz}"))
            
            # 상태
            state = order.get('state', '')
            self.order_table.setItem(row, 5, QTableWidgetItem(state))
    
    def set_bot_workers(self, bot_workers: dict):
        """봇 워커 참조 설정 (외부에서 호출)"""
        self.bot_workers = bot_workers
    
    def _stop_all_bots(self, clean: bool):
        """전체 봇 중지"""
        if not self.bot_workers:
            InfoBar.warning(
                title="실행 중인 봇 없음",
                content="실행 중인 봇이 없습니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        mode_str = "청산 후 중지" if clean else "봇만 중지 (포지션 유지)"
        
        # 모든 봇에 중지 신호
        for symbol, worker in list(self.bot_workers.items()):
            worker.stop_trading(clean_mode=clean)
            logger.info("Monitoring", f"{symbol} 전체 봇 중지 요청: {mode_str}")
        
        InfoBar.success(
            title="전체 봇 중지",
            content=f"{len(self.bot_workers)}개 봇 중지 요청: {mode_str}",
            orient=Qt.Horizontal,
            isClosable=True,
            duration=5000,
            position=InfoBarPosition.TOP,
            parent=self
        )
    
    def _stop_single_bot(self, symbol: str, clean: bool):
        """개별 봇 중지"""
        if symbol not in self.bot_workers:
            InfoBar.warning(
                title="봇 없음",
                content=f"{symbol} 봇이 실행 중이지 않습니다.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        mode_str = "청산" if clean else "봇만 중지"
        
        # 해당 봇만 중지
        worker = self.bot_workers[symbol]
        worker.stop_trading(clean_mode=clean)
        
        logger.info("Monitoring", f"{symbol} 개별 봇 중지 요청: {mode_str}")
        
        InfoBar.success(
            title=f"{symbol} 봇 중지",
            content=f"{mode_str} 요청",
            orient=Qt.Horizontal,
            isClosable=True,
            duration=3000,
            position=InfoBarPosition.TOP,
            parent=self
        )


