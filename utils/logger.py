"""
로깅 유틸리티
"""
import logging
from datetime import datetime
from typing import Optional
from PySide6.QtCore import QObject, Signal
import pytz
from config.settings import TIMEZONE

# 로그 레벨
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class LogEmitter(QObject):
    """로그를 Qt Signal로 전달하는 핸들러"""
    log_signal = Signal(str, int, str, str, str)  # timestamp, level, module, message, stacktrace


class AppLogger:
    """애플리케이션 전역 로거"""
    
    _instance = None
    _emitter = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._emitter = LogEmitter()
        return cls._instance
    
    def __init__(self):
        self.kst = pytz.timezone(TIMEZONE)
        self.logger = logging.getLogger("TradingBot")
        self.logger.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러 추가
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _get_kst_timestamp(self) -> str:
        """KST 기준 타임스탬프"""
        return datetime.now(self.kst).strftime("%Y-%m-%d %H:%M:%S")
    
    def log(self, level: int, module: str, message: str, stacktrace: str = ""):
        """로그 기록"""
        timestamp = self._get_kst_timestamp()
        
        # 콘솔 출력
        if level >= ERROR:
            self.logger.error(f"[{module}] {message}")
            if stacktrace:
                self.logger.error(stacktrace)
        elif level >= WARNING:
            self.logger.warning(f"[{module}] {message}")
        elif level >= INFO:
            self.logger.info(f"[{module}] {message}")
        else:
            self.logger.debug(f"[{module}] {message}")
        
        # UI로 Signal 전송
        self._emitter.log_signal.emit(timestamp, level, module, message, stacktrace)
    
    def debug(self, module: str, message: str):
        self.log(DEBUG, module, message)
    
    def info(self, module: str, message: str):
        self.log(INFO, module, message)
    
    def warning(self, module: str, message: str):
        self.log(WARNING, module, message)
    
    def error(self, module: str, message: str, stacktrace: str = ""):
        self.log(ERROR, module, message, stacktrace)
    
    def critical(self, module: str, message: str, stacktrace: str = ""):
        self.log(CRITICAL, module, message, stacktrace)
    
    @property
    def emitter(self) -> LogEmitter:
        """LogEmitter 인스턴스 반환"""
        return self._emitter


# 전역 로거 인스턴스
logger = AppLogger()


