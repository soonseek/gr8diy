"""
봇 모니터링 위젯
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QPushButton
)
from PySide6.QtCore import Qt
from qfluentwidgets import CardWidget, SubtitleLabel, BodyLabel, PushButton


class BotMonitoringWidget(QWidget):
    """봇 모니터링 위젯"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # 좌측: 활성 심볼/포지션 목록 (20%)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_title = SubtitleLabel("활성 포지션")
        left_layout.addWidget(left_title)
        
        self.position_list = QListWidget()
        left_layout.addWidget(self.position_list)
        
        # 정지 버튼
        stop_btn = PushButton("봇 정지")
        stop_btn.clicked.connect(self._stop_bot)
        left_layout.addWidget(stop_btn)
        
        left_widget.setMaximumWidth(300)
        layout.addWidget(left_widget)
        
        # 우측: 상세 로그 (80%)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_title = SubtitleLabel("거래 로그")
        right_layout.addWidget(right_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        right_layout.addWidget(self.log_text)
        
        layout.addWidget(right_widget)
    
    def _stop_bot(self):
        """봇 정지"""
        from utils.logger import logger
        logger.info("Bot", "봇 정지 요청")
        
        # TODO: 실제 봇 워커 중지


