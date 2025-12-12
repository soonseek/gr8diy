"""
백테스트 워커
QThread에서 백테스트 실행 및 진행 상황 전달
"""
from PySide6.QtCore import QObject, Signal, QThread
from typing import Dict, Optional

from backtest.engine import BacktestEngine, BacktestConfig
from utils.logger import logger


class BacktestWorker(QObject):
    """백테스트 워커"""
    
    # Signals
    progress_updated = Signal(str, int, int)  # message, current, total
    backtest_completed = Signal(dict)  # 결과
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.engine = BacktestEngine()
        self.is_running = False
        
        # 엔진 시그널 연결
        self.engine.progress_updated.connect(self.progress_updated.emit)
        self.engine.backtest_completed.connect(self._on_completed)
        self.engine.error_occurred.connect(self.error_occurred.emit)
    
    def run_backtest(self, config: BacktestConfig):
        """
        백테스트 실행
        
        Args:
            config: 백테스트 설정
        """
        self.is_running = True
        
        logger.info("BacktestWorker", 
                   f"백테스트 시작: {config.exchange_id} {config.symbol}")
        
        try:
            result = self.engine.run(config)
            
            if result:
                self.backtest_completed.emit(result)
            else:
                self.error_occurred.emit("백테스트 결과가 없습니다.")
                
        except Exception as e:
            import traceback
            error_msg = f"백테스트 실행 중 오류: {str(e)}"
            logger.error("BacktestWorker", error_msg, traceback.format_exc())
            self.error_occurred.emit(error_msg)
        finally:
            self.is_running = False
    
    def _on_completed(self, result: dict):
        """백테스트 완료 처리"""
        logger.info("BacktestWorker", 
                   f"백테스트 완료: 수익률 {result.get('total_return', 0):.2f}%")
    
    def stop(self):
        """백테스트 중지"""
        self.is_running = False
        self.engine.stop()


class BacktestRunner:
    """백테스트 러너 (스레드 관리)"""
    
    def __init__(self):
        self.thread: Optional[QThread] = None
        self.worker: Optional[BacktestWorker] = None
    
    def start(self, config: BacktestConfig, 
             on_progress=None, on_completed=None, on_error=None):
        """
        백테스트 시작 (새 스레드에서)
        
        Args:
            config: 백테스트 설정
            on_progress: 진행 콜백 (message, current, total)
            on_completed: 완료 콜백 (result)
            on_error: 에러 콜백 (error_msg)
        """
        # 이전 스레드 정리
        self.stop()
        
        # 새 스레드 및 워커 생성
        self.thread = QThread()
        self.worker = BacktestWorker()
        self.worker.moveToThread(self.thread)
        
        # 시그널 연결
        if on_progress:
            self.worker.progress_updated.connect(on_progress)
        if on_completed:
            self.worker.backtest_completed.connect(on_completed)
        if on_error:
            self.worker.error_occurred.connect(on_error)
        
        # 스레드 시작 시 백테스트 실행
        self.thread.started.connect(lambda: self.worker.run_backtest(config))
        
        # 완료 시 스레드 종료
        self.worker.backtest_completed.connect(self._cleanup)
        self.worker.error_occurred.connect(self._cleanup)
        
        # 스레드 시작
        self.thread.start()
        
        logger.info("BacktestRunner", "백테스트 스레드 시작")
    
    def stop(self):
        """백테스트 중지"""
        if self.worker:
            self.worker.stop()
        
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(5000)
        
        self.thread = None
        self.worker = None
    
    def _cleanup(self, *args):
        """스레드 정리"""
        if self.thread:
            self.thread.quit()
    
    def is_running(self) -> bool:
        """실행 중 여부"""
        return self.thread is not None and self.thread.isRunning()

