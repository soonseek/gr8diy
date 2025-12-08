"""
로그 위젯 (하단 시스템 로그)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QColor
from qfluentwidgets import (
    PushButton, ComboBox, TitleLabel
)
from utils.logger import INFO, WARNING, ERROR, CRITICAL
from config.settings import LOG_VIEW_MAX_LINES


class LogWidget(QWidget):
    """시스템 로그 위젯"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self.log_level_filter = "ALL"
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 상단 컨트롤
        control_layout = QHBoxLayout()
        
        # 타이틀
        title = TitleLabel("시스템 로그")
        control_layout.addWidget(title)
        
        control_layout.addStretch()
        
        # 필터 콤보박스
        self.level_combo = ComboBox()
        self.level_combo.addItems(["ALL", "INFO", "WARNING", "ERROR"])
        self.level_combo.currentTextChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.level_combo)
        
        # 클리어 버튼
        clear_btn = PushButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)
        control_layout.addWidget(clear_btn)
        
        layout.addLayout(control_layout)
        
        # 로그 텍스트
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        # PySide6에서는 document()를 통해 설정
        self.log_text.document().setMaximumBlockCount(LOG_VIEW_MAX_LINES)
        layout.addWidget(self.log_text)
    
    def add_log(self, timestamp: str, level: int, module: str, 
                message: str, stacktrace: str = ""):
        """로그 추가"""
        # 레벨 필터링
        level_name = self._get_level_name(level)
        if self.log_level_filter != "ALL" and level_name != self.log_level_filter:
            return
        
        # 로그 포맷
        log_line = f"[{timestamp}] [{level_name}] [{module}] {message}"
        
        # 색상 설정
        color = self._get_level_color(level)
        
        # 텍스트 추가
        self.log_text.setTextColor(color)
        self.log_text.append(log_line)
        
        if stacktrace:
            self.log_text.append(f"  {stacktrace}")
        
        # 스크롤을 맨 아래로
        self.log_text.moveCursor(QTextCursor.End)
    
    def clear_logs(self):
        """로그 클리어"""
        self.log_text.clear()
    
    def _on_filter_changed(self, text: str):
        """필터 변경"""
        self.log_level_filter = text
    
    @staticmethod
    def _get_level_name(level: int) -> str:
        """레벨 이름 반환"""
        if level >= CRITICAL:
            return "CRITICAL"
        elif level >= ERROR:
            return "ERROR"
        elif level >= WARNING:
            return "WARNING"
        else:
            return "INFO"
    
    @staticmethod
    def _get_level_color(level: int) -> QColor:
        """레벨별 색상 반환"""
        if level >= ERROR:
            return QColor("#e74c3c")  # 빨강
        elif level >= WARNING:
            return QColor("#f39c12")  # 주황
        elif level >= INFO:
            return QColor("#3498db")  # 파랑
        else:
            return QColor("#95a5a6")  # 회색


