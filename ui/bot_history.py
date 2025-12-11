"""
봇 거래 내역 위젯
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QDateEdit
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    CardWidget, SubtitleLabel, ComboBox, PushButton, BodyLabel
)

from database.repository import TradesHistoryRepository
from utils.time_helper import time_helper
from datetime import timedelta
from utils.logger import logger


class BotHistoryWidget(QWidget):
    """봇 거래 내역 위젯"""
    
    def __init__(self):
        super().__init__()
        self.trades_repo = TradesHistoryRepository()
        self._init_ui()
        
        # 초기 데이터 로드
        self._search_trades()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 필터 카드
        filter_card = CardWidget()
        filter_layout = QHBoxLayout(filter_card)
        
        filter_layout.addWidget(BodyLabel("기간:"))
        
        self.period_combo = ComboBox()
        self.period_combo.addItems(["오늘", "이번 주", "이번 달", "사용자 지정"])
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        filter_layout.addWidget(self.period_combo)
        
        self.start_date_picker = QDateEdit()
        self.start_date_picker.setCalendarPopup(True)
        self.start_date_picker.setDisplayFormat("yyyy-MM-dd")
        self.start_date_picker.setMinimumHeight(40)
        self.start_date_picker.setMinimumWidth(150)
        self.start_date_picker.setVisible(False)
        filter_layout.addWidget(self.start_date_picker)
        
        self.end_date_picker = QDateEdit()
        self.end_date_picker.setCalendarPopup(True)
        self.end_date_picker.setDisplayFormat("yyyy-MM-dd")
        self.end_date_picker.setMinimumHeight(40)
        self.end_date_picker.setMinimumWidth(150)
        self.end_date_picker.setVisible(False)
        filter_layout.addWidget(self.end_date_picker)
        
        search_btn = PushButton("조회")
        search_btn.clicked.connect(self._search_trades)
        filter_layout.addWidget(search_btn)
        
        filter_layout.addStretch()
        
        layout.addWidget(filter_card)
        
        # 통계 카드
        stats_card = CardWidget()
        stats_layout = QVBoxLayout(stats_card)
        
        stats_title = SubtitleLabel("거래 통계")
        stats_layout.addWidget(stats_title)
        
        self.stats_label = BodyLabel("통계를 조회하려면 '조회' 버튼을 클릭하세요.")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_card)
        
        # 거래 내역 테이블
        self.trades_table = QTableWidget(0, 9)
        self.trades_table.setHorizontalHeaderLabels([
            "심볼", "방향", "진입가", "청산가", "사이즈", 
            "레버리지", "PnL", "수수료", "청산 시간"
        ])
        self.trades_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.trades_table)
    
    def _on_period_changed(self, index: int):
        """기간 선택 변경"""
        is_custom = (index == 3)
        self.start_date_picker.setVisible(is_custom)
        self.end_date_picker.setVisible(is_custom)
    
    def _search_trades(self):
        """거래 내역 조회"""
        try:
            # 기간 설정
            period = self.period_combo.currentText()
            start_date = None
            end_date = None
            
            if period == "오늘":
                start_date = time_helper.format_kst(time_helper.now_kst().replace(hour=0, minute=0, second=0))
            elif period == "이번 주":
                start_date = time_helper.format_kst(time_helper.now_kst() - timedelta(days=7))
            elif period == "이번 달":
                start_date = time_helper.format_kst(time_helper.now_kst() - timedelta(days=30))
            elif period == "사용자 지정":
                start_qdate = self.start_date_picker.date()
                end_qdate = self.end_date_picker.date()
                start_date = f"{start_qdate.year()}-{start_qdate.month():02d}-{start_qdate.day():02d}"
                end_date = f"{end_qdate.year()}-{end_qdate.month():02d}-{end_qdate.day():02d}"
            
            # 거래 내역 조회
            trades = self.trades_repo.get_trades(start_date=start_date, end_date=end_date)
            
            logger.info("History", f"조회된 거래 내역: {len(trades)}개 (기간: {period})")
            
            # 테이블 업데이트
            self.trades_table.setRowCount(0)
            
            if not trades:
                # 내역이 없으면 안내 메시지
                self.stats_label.setText(
                    "📭 거래 내역이 없습니다.\n\n"
                    "💡 포지션이 청산되면 자동으로 내역이 저장됩니다.\n"
                    "   (TP/SL 체결, 수동 청산, 봇 중지 등)"
                )
                self.stats_label.setStyleSheet("color: #95a5a6;")
                return
            
            for trade in trades:
                row = self.trades_table.rowCount()
                self.trades_table.insertRow(row)
                
                # 심볼
                self.trades_table.setItem(row, 0, QTableWidgetItem(trade['symbol']))
                
                # 방향
                side = trade['side'].upper()
                self.trades_table.setItem(row, 1, QTableWidgetItem(side))
                
                # 진입가
                self.trades_table.setItem(row, 2, QTableWidgetItem(f"{trade['entry_price']:.2f}"))
                
                # 청산가
                self.trades_table.setItem(row, 3, QTableWidgetItem(f"{trade['exit_price']:.2f}"))
                
                # 사이즈
                self.trades_table.setItem(row, 4, QTableWidgetItem(f"{trade['size']}"))
                
                # 레버리지
                self.trades_table.setItem(row, 5, QTableWidgetItem(f"{trade['leverage']}x"))
                
                # PnL (색상 표시)
                pnl = trade['pnl']
                pnl_item = QTableWidgetItem(f"{pnl:+.2f}")
                if pnl >= 0:
                    pnl_item.setForeground(Qt.green)
                else:
                    pnl_item.setForeground(Qt.red)
                self.trades_table.setItem(row, 6, pnl_item)
                
                # 수수료
                self.trades_table.setItem(row, 7, QTableWidgetItem(f"{trade['fees']:.2f}"))
                
                # 청산 시간
                exit_time = trade.get('exit_time', '')
                if len(exit_time) > 16:
                    exit_time = exit_time[:16]  # 초 제거
                self.trades_table.setItem(row, 8, QTableWidgetItem(exit_time))
            
            # 통계 업데이트
            stats = self.trades_repo.get_statistics(start_date=start_date, end_date=end_date)
            
            stats_text = (
                f"📊 총 거래: {stats['total_trades']}회  |  "
                f"✅ 승률: {stats['win_rate']:.1f}%  |  "
                f"💰 순 PnL: {stats['net_pnl']:+.2f} USDT  |  "
                f"📈 총 이익: +{stats['total_profit']:.2f}  |  "
                f"📉 총 손실: {stats['total_loss']:.2f}  |  "
                f"⚠️ 최대 연속 손실: {stats['max_consecutive_losses']}회"
            )
            
            self.stats_label.setText(stats_text)
            
            if stats['net_pnl'] >= 0:
                self.stats_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            else:
                self.stats_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            
            logger.info("History", f"{len(trades)}개 거래 내역 조회 완료")
            
        except Exception as e:
            import traceback
            logger.error("History", f"거래 내역 조회 실패: {str(e)}", traceback.format_exc())
            self.stats_label.setText(f"조회 실패: {str(e)}")


