"""
로그 위젯 (하단 시스템 로그)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QColor
from qfluentwidgets import (
    PushButton, ComboBox, TitleLabel, Pivot
)
from utils.logger import INFO, WARNING, ERROR, CRITICAL
from config.settings import LOG_VIEW_MAX_LINES


class LogWidget(QWidget):
    """시스템 로그 위젯"""
    
    def __init__(self):
        super().__init__()
        self.error_count = 0
        self._init_ui()
    
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
        
        # 클리어 버튼
        clear_btn = PushButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)
        control_layout.addWidget(clear_btn)
        
        layout.addLayout(control_layout)
        
        # Pivot (탭)
        self.pivot = Pivot(self)
        self.stack_widget = QStackedWidget(self)
        
        # 전체 로그 텍스트
        self.all_log_text = QTextEdit()
        self.all_log_text.setReadOnly(True)
        self.all_log_text.document().setMaximumBlockCount(LOG_VIEW_MAX_LINES)
        
        # 에러 전용 로그 텍스트
        self.error_log_text = QTextEdit()
        self.error_log_text.setReadOnly(True)
        self.error_log_text.document().setMaximumBlockCount(LOG_VIEW_MAX_LINES)
        
        # 스택 위젯에 추가
        self.stack_widget.addWidget(self.all_log_text)
        self.stack_widget.addWidget(self.error_log_text)
        
        # Pivot 아이템 추가
        self.pivot.addItem(
            routeKey="all",
            text="전체 로그",
            onClick=lambda: self.stack_widget.setCurrentIndex(0)
        )
        self.pivot.addItem(
            routeKey="errors",
            text="에러",
            onClick=lambda: self.stack_widget.setCurrentIndex(1)
        )
        
        layout.addWidget(self.pivot)
        layout.addWidget(self.stack_widget)
    
    def add_log(self, timestamp: str, level: int, module: str, 
                message: str, stacktrace: str = ""):
        """로그 추가"""
        level_name = self._get_level_name(level)
        
        # 로그 포맷
        log_line = f"[{timestamp}] [{level_name}] [{module}] {message}"
        
        # 색상 설정
        color = self._get_level_color(level)
        
        # 전체 로그에 추가
        self.all_log_text.setTextColor(color)
        self.all_log_text.append(log_line)
        if stacktrace:
            self.all_log_text.append(f"  {stacktrace}")
        self.all_log_text.moveCursor(QTextCursor.End)
        
        # 에러 로그에도 추가 (ERROR 이상만)
        if level >= ERROR:
            self.error_count += 1
            self._update_error_tab_title()
            
            self.error_log_text.setTextColor(color)
            self.error_log_text.append(log_line)
            if stacktrace:
                self.error_log_text.append(f"  {stacktrace}")
            self.error_log_text.moveCursor(QTextCursor.End)
    
    def clear_logs(self):
        """로그 클리어"""
        self.all_log_text.clear()
        self.error_log_text.clear()
        self.error_count = 0
        self._update_error_tab_title()
    
    def _update_error_tab_title(self):
        """에러 탭 제목 업데이트"""
        # Pivot에서 직접 아이템을 찾아서 업데이트하는 것은 복잡하므로
        # 간단하게 에러 카운트만 표시
        # TODO: QFluentWidgets Pivot API를 사용하여 동적 업데이트 구현
        pass
    
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


