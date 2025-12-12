"""
봇 페이지 (조건설정, 모니터링, 내역)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from qfluentwidgets import (
    Pivot, TitleLabel, FluentIcon
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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Pivot (탭) - 좌측 정렬
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        
        self.stack_widget = QStackedWidget(self)
        
        # 하위 위젯들
        self.conditions_widget = BotConditionsWidget()
        self.monitoring_widget = BotMonitoringWidget()
        self.history_widget = BotHistoryWidget()
        
        # 봇 실행 시 모니터링으로 전환
        self.conditions_widget.bot_started.connect(self._switch_to_monitoring)
        
        # Pivot 아이템 추가 및 워커 공유 설정
        def switch_to_conditions():
            self.stack_widget.setCurrentIndex(0)
        
        def switch_to_monitoring():
            self.stack_widget.setCurrentIndex(1)
            # 봇 워커 참조 업데이트
            if hasattr(self.conditions_widget, 'bot_workers'):
                self.monitoring_widget.set_bot_workers(self.conditions_widget.bot_workers)
        
        def switch_to_history():
            self.stack_widget.setCurrentIndex(2)
        
        self.pivot.addItem(
            routeKey="conditions",
            text="봇 생성",
            onClick=switch_to_conditions,
            icon=FluentIcon.ADD
        )
        self.pivot.addItem(
            routeKey="monitoring",
            text="모니터링",
            onClick=switch_to_monitoring,
            icon=FluentIcon.ROBOT
        )
        self.pivot.addItem(
            routeKey="history",
            text="내역",
            onClick=switch_to_history,
            icon=FluentIcon.HISTORY
        )
        
        # 스택 위젯에 추가
        self.stack_widget.addWidget(self.conditions_widget)
        self.stack_widget.addWidget(self.monitoring_widget)
        self.stack_widget.addWidget(self.history_widget)
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack_widget)
        
        # 기본 탭 선택
        self.pivot.setCurrentItem("conditions")
    
    def _switch_to_monitoring(self):
        """모니터링 탭으로 전환"""
        self.stack_widget.setCurrentIndex(1)
        self.pivot.setCurrentItem("monitoring")
        if hasattr(self.conditions_widget, 'bot_workers'):
            self.monitoring_widget.set_bot_workers(self.conditions_widget.bot_workers)


