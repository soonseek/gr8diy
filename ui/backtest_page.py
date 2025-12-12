"""
백테스트 페이지
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QScrollArea, QDateEdit,
    QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, BodyLabel,
    PushButton, ComboBox, SpinBox, DoubleSpinBox, SwitchButton,
    ProgressBar, InfoBar, Pivot, FluentIcon
)
from datetime import datetime
import json

from database.repository import CandlesRepository, BacktestResultsRepository
from config.settings import DATA_RETENTION_DAYS
from config.exchanges import SUPPORTED_EXCHANGES, ALL_EXCHANGE_IDS, DEFAULT_EXCHANGE_ID, DEFAULT_SYMBOLS
from backtest.engine import BacktestConfig
from workers.backtest_worker import BacktestRunner
from utils.logger import logger


class BacktestPage(QWidget):
    """백테스트"""
    
    def __init__(self):
        super().__init__()
        self.candles_repo = CandlesRepository()
        self.results_repo = BacktestResultsRepository()
        
        self.exchange_ids = ALL_EXCHANGE_IDS.copy()
        self.runner = BacktestRunner()
        self.current_result = None
        
        self._init_ui()
    
    def _init_ui(self):
        """UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        layout.addWidget(TitleLabel("다음 개발 목표"))
        
        notice = BodyLabel("아직 작동하지 않거나 완전하지 않습니다")
        notice.setStyleSheet("color: #ffaa00; font-size: 14px; font-weight: bold;")
        layout.addWidget(notice)
        
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        
        self.stack = QStackedWidget()
        
        settings_w = self._create_settings()
        results_w = self._create_results()
        history_w = self._create_history()
        
        self.pivot.addItem("settings", "설정", lambda: self.stack.setCurrentIndex(0), icon=FluentIcon.SETTING)
        self.pivot.addItem("results", "결과", lambda: self.stack.setCurrentIndex(1), icon=FluentIcon.CALORIES)
        self.pivot.addItem("history", "히스토리", lambda: self.stack.setCurrentIndex(2), icon=FluentIcon.HISTORY)
        
        self.stack.addWidget(settings_w)
        self.stack.addWidget(results_w)
        self.stack.addWidget(history_w)
        
        layout.addLayout(pivot_layout)
        layout.addWidget(self.stack)
        
        self.pivot.setCurrentItem("settings")
    
    def _create_settings(self) -> QWidget:
        """설정"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        layout.addWidget(BodyLabel("백테스트 기능은 추후 개발 예정입니다."))
        layout.addStretch()
        
        return w
    
    def _create_results(self) -> QWidget:
        """결과"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        layout.addWidget(BodyLabel("백테스트 결과가 여기에 표시됩니다."))
        layout.addStretch()
        
        return w
    
    def _create_history(self) -> QWidget:
        """히스토리"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        layout.addWidget(BodyLabel("백테스트 히스토리가 여기에 표시됩니다."))
        layout.addStretch()
        
        return w
