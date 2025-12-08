"""
봇 거래 내역 위젯
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    CardWidget, SubtitleLabel, ComboBox, DatePicker, PushButton, BodyLabel
)

from database.repository import TradesHistoryRepository


class BotHistoryWidget(QWidget):
    """봇 거래 내역 위젯"""
    
    def __init__(self):
        super().__init__()
        self.trades_repo = TradesHistoryRepository()
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 필터 카드
        filter_card = CardWidget()
        filter_layout = QHBoxLayout(filter_card)
        
        filter_layout.addWidget(BodyLabel("기간:"))
        
        self.period_combo = ComboBox()
        self.period_combo.addItems(["오늘", "이번 주", "이번 달", "사용자 지정"])
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        filter_layout.addWidget(self.period_combo)
        
        self.start_date_picker = DatePicker()
        self.start_date_picker.setVisible(False)
        filter_layout.addWidget(self.start_date_picker)
        
        self.end_date_picker = DatePicker()
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
        # TODO: 실제 DB 조회 및 테이블 채우기
        stats = self.trades_repo.get_statistics()
        
        stats_text = f"""
        총 거래 수: {stats['total_trades']}
        총 이익: ${stats['total_profit']:.2f}
        총 손실: ${stats['total_loss']:.2f}
        순 PnL: ${stats['net_pnl']:.2f}
        승률: {stats['win_rate']:.1f}%
        최대 연속 손실: {stats['max_consecutive_losses']}회
        최대 드로다운: ${stats['max_drawdown']:.2f}
        """
        
        self.stats_label.setText(stats_text)


