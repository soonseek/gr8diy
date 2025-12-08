"""
데이터 수집 워커
"""
import time
from datetime import datetime, timedelta
from typing import List
from PySide6.QtCore import QObject, Signal, QThread

from api.okx_client import OKXClient
from database.repository import CandlesRepository, IndicatorsRepository
from indicators.calculator import IndicatorCalculator
from utils.logger import logger
from utils.time_helper import time_helper
from config.settings import TIMEFRAMES, DATA_RETENTION_DAYS


class DataCollectorWorker(QObject):
    """데이터 수집 워커"""
    
    # Signals
    progress_updated = Signal(str, int, int)  # message, current, total
    collection_completed = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, okx_client: OKXClient):
        super().__init__()
        self.okx_client = okx_client
        self.candles_repo = CandlesRepository()
        self.indicators_repo = IndicatorsRepository()
        
        self.is_running = False
        self.is_realtime_enabled = False
    
    def set_realtime_enabled(self, enabled: bool):
        """실시간 최신화 활성화 설정"""
        self.is_realtime_enabled = enabled
        logger.info("DataCollector", f"실시간 최신화: {'활성' if enabled else '비활성'}")
    
    def backfill_data(self, symbols: List[str], start_date: datetime):
        """
        과거 데이터 백필
        
        symbols: 수집할 심볼 목록
        start_date: 시작 날짜 (KST)
        """
        logger.info("DataCollector", f"데이터 백필 시작: {len(symbols)}개 심볼")
        
        total_tasks = len(symbols) * len(TIMEFRAMES)
        current_task = 0
        
        for symbol in symbols:
            for timeframe in TIMEFRAMES:
                if not self.is_running:
                    break
                
                current_task += 1
                self.progress_updated.emit(
                    f"{symbol} - {timeframe} 수집 중...",
                    current_task,
                    total_tasks
                )
                
                try:
                    self._collect_candles(symbol, timeframe, start_date)
                except Exception as e:
                    error_msg = f"{symbol} {timeframe} 수집 실패: {str(e)}"
                    logger.error("DataCollector", error_msg)
                    self.error_occurred.emit(error_msg)
        
        logger.info("DataCollector", "데이터 백필 완료")
        self.collection_completed.emit()
    
    def _collect_candles(self, symbol: str, timeframe: str, start_date: datetime):
        """캔들 데이터 수집"""
        # 최신 타임스탬프 조회
        latest_ts_str = self.candles_repo.get_latest_timestamp(symbol, timeframe)
        
        if latest_ts_str:
            # 최신 데이터부터 수집
            latest_dt = datetime.fromisoformat(latest_ts_str)
            from_timestamp = time_helper.kst_to_timestamp(latest_dt)
        else:
            # 시작 날짜부터 수집
            from_timestamp = time_helper.kst_to_timestamp(start_date)
        
        # 현재까지 수집
        to_timestamp = time_helper.kst_to_timestamp(time_helper.now_kst())
        
        # OKX API로 캔들 조회 (페이지네이션)
        all_candles = []
        after = None
        
        while True:
            if not self.is_running:
                break
            
            candles = self.okx_client.get_candles(
                inst_id=symbol,
                bar=timeframe,
                after=after,
                limit=100
            )
            
            if not candles:
                break
            
            # 필터링 및 변환
            for candle in candles:
                ts_ms = int(candle[0])
                
                # 범위 체크
                if ts_ms < from_timestamp or ts_ms > to_timestamp:
                    continue
                
                dt_kst = time_helper.timestamp_to_kst(ts_ms)
                
                all_candles.append({
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "timestamp": time_helper.format_kst(dt_kst),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5])
                })
            
            # 다음 페이지
            if len(candles) < 100:
                break
            
            after = candles[-1][0]
            time.sleep(0.1)  # Rate limit
        
        # DB 저장
        if all_candles:
            self.candles_repo.insert_candles_batch(all_candles)
            logger.info("DataCollector", 
                       f"{symbol} {timeframe}: {len(all_candles)}개 캔들 저장")
            
            # 보조지표 계산
            self._calculate_and_save_indicators(symbol, timeframe)
    
    def _calculate_and_save_indicators(self, symbol: str, timeframe: str):
        """보조지표 계산 및 저장"""
        # 최근 250개 캔들 조회 (MA200 + 여유)
        candles = self.candles_repo.get_candles(symbol, timeframe, limit=250)
        
        if len(candles) < 200:
            logger.warning("DataCollector", 
                          f"{symbol} {timeframe}: 지표 계산 불가 (캔들 부족)")
            return
        
        # 최신 캔들 기준으로 지표 계산
        candles.reverse()  # 오래된 순으로 정렬
        indicators = IndicatorCalculator.calculate_all_indicators(candles)
        
        if indicators:
            latest_candle = candles[-1]
            self.indicators_repo.upsert_indicators(
                symbol,
                timeframe,
                latest_candle['timestamp'],
                indicators
            )
            logger.debug("DataCollector", 
                        f"{symbol} {timeframe}: 지표 계산 완료")
    
    def realtime_update(self, symbols: List[str]):
        """실시간 데이터 업데이트 (주기적 호출)"""
        if not self.is_realtime_enabled:
            return
        
        for symbol in symbols:
            for timeframe in TIMEFRAMES:
                if not self.is_running:
                    break
                
                try:
                    # 최신 캔들만 가져오기
                    candles = self.okx_client.get_candles(
                        inst_id=symbol,
                        bar=timeframe,
                        limit=1
                    )
                    
                    if candles:
                        candle = candles[0]
                        ts_ms = int(candle[0])
                        dt_kst = time_helper.timestamp_to_kst(ts_ms)
                        
                        self.candles_repo.insert_candle(
                            symbol,
                            timeframe,
                            time_helper.format_kst(dt_kst),
                            float(candle[1]),
                            float(candle[2]),
                            float(candle[3]),
                            float(candle[4]),
                            float(candle[5])
                        )
                        
                        # 지표 재계산
                        self._calculate_and_save_indicators(symbol, timeframe)
                    
                except Exception as e:
                    logger.error("DataCollector", 
                               f"{symbol} {timeframe} 실시간 업데이트 실패: {str(e)}")
                
                time.sleep(0.05)  # Rate limit
    
    def run_continuous(self, symbols: List[str], interval_seconds: int = 60):
        """지속적 실행 (스레드에서 호출)"""
        self.is_running = True
        logger.info("DataCollector", "지속적 데이터 수집 시작")
        
        while self.is_running:
            if self.is_realtime_enabled:
                self.realtime_update(symbols)
            
            time.sleep(interval_seconds)
        
        logger.info("DataCollector", "데이터 수집 중지")
    
    def stop(self):
        """워커 중지"""
        self.is_running = False


