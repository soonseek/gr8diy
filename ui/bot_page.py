"""
봇 페이지 (조건설정, 모니터링, 내역)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from qfluentwidgets import (
    Pivot, TitleLabel
)

from ui.bot_conditions import BotConditionsWidget
from ui.bot_monitoring import BotMonitoringWidget
from ui.bot_history import BotHistoryWidget


class BotPage(QWidget):
    """봇 페이지"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 타이틀
        title = TitleLabel("자동매매 봇")
        layout.addWidget(title)
        
        # Pivot (탭)
        self.pivot = Pivot(self)
        self.stack_widget = QStackedWidget(self)
        
        # 하위 위젯들
        self.conditions_widget = BotConditionsWidget()
        self.monitoring_widget = BotMonitoringWidget()
        self.history_widget = BotHistoryWidget()
        
        # Pivot 아이템 추가
        self.pivot.addItem(
            routeKey="conditions",
            text="조건설정",
            onClick=lambda: self.stack_widget.setCurrentIndex(0)
        )
        self.pivot.addItem(
            routeKey="monitoring",
            text="모니터링",
            onClick=lambda: self.stack_widget.setCurrentIndex(1)
        )
        self.pivot.addItem(
            routeKey="history",
            text="내역",
            onClick=lambda: self.stack_widget.setCurrentIndex(2)
        )
        
        # 스택 위젯에 추가
        self.stack_widget.addWidget(self.conditions_widget)
        self.stack_widget.addWidget(self.monitoring_widget)
        self.stack_widget.addWidget(self.history_widget)
        
        layout.addWidget(self.pivot)
        layout.addWidget(self.stack_widget)


