"""
유지보수 워커
"""
import time
from PySide6.QtCore import QObject, Signal

from database.repository import (
    CandlesRepository, IndicatorsRepository, 
    SystemLogsRepository, BotLogsRepository
)
from utils.logger import logger
from config.settings import DATA_RETENTION_DAYS, LOG_RETENTION_DAYS


class MaintenanceWorker(QObject):
    """유지보수 워커 (주기적 데이터 정리)"""
    
    # Signals
    cleanup_completed = Signal(str)  # message
    
    def __init__(self):
        super().__init__()
        self.candles_repo = CandlesRepository()
        self.indicators_repo = IndicatorsRepository()
        self.system_logs_repo = SystemLogsRepository()
        self.bot_logs_repo = BotLogsRepository()
        
        self.is_running = False
    
    def cleanup_old_data(self):
        """오래된 데이터 정리"""
        try:
            # 캔들 데이터 삭제
            self.candles_repo.delete_old(DATA_RETENTION_DAYS)
            logger.info("Maintenance", 
                       f"{DATA_RETENTION_DAYS}일 이상 된 캔들 데이터 삭제")
            
            # 지표 데이터 삭제
            self.indicators_repo.delete_old(DATA_RETENTION_DAYS)
            logger.info("Maintenance", 
                       f"{DATA_RETENTION_DAYS}일 이상 된 지표 데이터 삭제")
            
            # 시스템 로그 삭제
            self.system_logs_repo.delete_old(LOG_RETENTION_DAYS)
            logger.info("Maintenance", 
                       f"{LOG_RETENTION_DAYS}일 이상 된 시스템 로그 삭제")
            
            self.cleanup_completed.emit("데이터 정리 완료")
            
        except Exception as e:
            error_msg = f"데이터 정리 실패: {str(e)}"
            logger.error("Maintenance", error_msg)
    
    def run_continuous(self, interval_seconds: int = 60):
        """지속적 실행 (1분 주기 권장)"""
        self.is_running = True
        logger.info("Maintenance", "유지보수 워커 시작 (1분 주기)")
        
        while self.is_running:
            self.cleanup_old_data()
            time.sleep(interval_seconds)
        
        logger.info("Maintenance", "유지보수 워커 중지")
    
    def stop(self):
        """워커 중지"""
        self.is_running = False


