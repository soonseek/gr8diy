"""
데이터 수집 워커
CCXT 멀티 거래소 지원 버전
"""
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PySide6.QtCore import QObject, Signal, QThread

from api.ccxt_client import CCXTClient
from api.exchange_factory import get_public_client, get_exchange_factory
from database.repository import (
    CandlesRepository, IndicatorsRepository, ActiveSymbolsRepository
)
from indicators.calculator import IndicatorCalculator
from utils.logger import logger
from utils.time_helper import time_helper
from config.settings import TIMEFRAMES, DATA_RETENTION_DAYS, DATA_POLLING_INTERVAL


class DataCollectorWorker(QObject):
    """데이터 수집 워커 (멀티 거래소)"""
    
    # Signals
    progress_updated = Signal(str, int, int)  # message, current, total
    collection_completed = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, exchange_id: str = None, client: CCXTClient = None):
        """
        Args:
            exchange_id: 거래소 ID (client가 없을 때 사용)
            client: CCXT 클라이언트 (직접 전달)
        """
        super().__init__()
        
        self.exchange_id = exchange_id
        self.client = client
        
        self.candles_repo = CandlesRepository()
        self.indicators_repo = IndicatorsRepository()
        self.symbols_repo = ActiveSymbolsRepository()
        
        self.is_running = False
        self.is_realtime_enabled = False
    
    def _get_client(self) -> Optional[CCXTClient]:
        """클라이언트 조회"""
        if self.client:
            return self.client
        
        if self.exchange_id:
            return get_public_client(self.exchange_id)
        
        return None
    
    def set_exchange(self, exchange_id: str, client: CCXTClient = None):
        """거래소 변경"""
        self.exchange_id = exchange_id
        self.client = client
    
    def set_realtime_enabled(self, enabled: bool):
        """실시간 최신화 활성화 설정"""
        self.is_realtime_enabled = enabled
        logger.info("DataCollector", f"실시간 최신화: {'활성' if enabled else '비활성'}")
    
    def backfill_data(self, symbols: List[str], start_date: datetime, 
                     exchange_id: str = None):
        """
        과거 데이터 백필
        
        Args:
            symbols: 수집할 심볼 목록 (CCXT 형식: BTC/USDT:USDT)
            start_date: 시작 날짜 (KST)
            exchange_id: 거래소 ID (선택, 없으면 self.exchange_id 사용)
        """
        self.is_running = True
        
        ex_id = exchange_id or self.exchange_id
        if not ex_id:
            self.error_occurred.emit("거래소가 지정되지 않았습니다.")
            return
        
        # 클라이언트 조회
        client = self._get_client()
        if not client and exchange_id:
            client = get_public_client(exchange_id)
        
        if not client:
            self.error_occurred.emit(f"{ex_id} 클라이언트 생성 실패")
            return
        
        logger.info("DataCollector", f"데이터 백필 시작: {ex_id}, {len(symbols)}개 심볼")
        print("="*60)
        print(f"[WORKER] 데이터 백필 시작: {ex_id}, {len(symbols)}개 심볼")
        print(f"[WORKER] 수집할 타임프레임: {TIMEFRAMES}")
        print(f"[WORKER] 시작 날짜: {start_date}")
        print(f"[WORKER] 전체 작업량: {len(symbols)}개 심볼 × {len(TIMEFRAMES)}개 타임프레임 = {len(symbols) * len(TIMEFRAMES)}개 작업")
        print("="*60)

        total_tasks = len(symbols) * len(TIMEFRAMES)
        current_task = 0
        
        for symbol in symbols:
            for timeframe in TIMEFRAMES:
                if not self.is_running:
                    logger.warning("DataCollector", "데이터 백필 중단됨")
                    break
                
                current_task += 1
                print(f"[WORKER] ({current_task}/{total_tasks}) {ex_id} {symbol} {timeframe} 수집 시작...")
                self.progress_updated.emit(
                    f"{ex_id} {symbol} {timeframe} 수집 시작",
                    current_task,
                    total_tasks
                )
                
                try:
                    self._collect_candles(
                        client, ex_id, symbol, timeframe, 
                        start_date, current_task, total_tasks
                    )
                except Exception as e:
                    import traceback
                    error_msg = f"{symbol} {timeframe} 수집 실패: {str(e)}"
                    logger.error("DataCollector", error_msg, traceback.format_exc())
                    self.error_occurred.emit(error_msg)
        
        self.is_running = False
        logger.info("DataCollector", "데이터 백필 완료")
        print("="*60)
        print(f"[WORKER] 데이터 백필 완료! {ex_id}")
        print("="*60)
        self.collection_completed.emit()
    
    def _collect_candles(self, client: CCXTClient, exchange_id: str,
                        symbol: str, timeframe: str, start_date: datetime, 
                        current_task: int = 0, total_tasks: int = 0):
        """캔들 데이터 수집"""
        try:
            # 최신 타임스탬프 조회
            latest_ts_str = self.candles_repo.get_latest_timestamp(
                exchange_id, symbol, timeframe
            )
            
            if latest_ts_str:
                # 최신 데이터부터 수집
                latest_dt = datetime.fromisoformat(latest_ts_str)
                from_timestamp = time_helper.kst_to_timestamp(latest_dt)
                logger.info("DataCollector",
                           f"{exchange_id} {symbol} {timeframe} 최신 데이터부터: {latest_dt}")
            else:
                # 시작 날짜부터 수집
                from_timestamp = time_helper.kst_to_timestamp(start_date)
                logger.info("DataCollector",
                           f"{exchange_id} {symbol} {timeframe} {start_date}부터 수집 시작: {from_timestamp}")
            
            logger.debug("DataCollector", 
                        f"{exchange_id} {symbol} {timeframe} 수집 시작: {from_timestamp}")
                        
        except Exception as e:
            import traceback
            logger.error("DataCollector", 
                        f"{symbol} {timeframe} 타임스탬프 처리 실패: {str(e)}", 
                        traceback.format_exc())
            return
        
        # CCXT로 캔들 조회 (페이지네이션)
        all_candles = []
        since_ms = from_timestamp
        page_count = 0
        consecutive_empty_pages = 0
        max_empty_pages = 3  # 연속 3페이지가 비었으면 중단

        # OKX 1분봉은 더 작은 limit 사용
        limit = 300 if (exchange_id == "okx" and timeframe == "1m") else 1000

        while True:
            if not self.is_running:
                logger.warning("DataCollector", f"{symbol} {timeframe} 수집 중단")
                break

            try:
                logger.info("DataCollector",
                           f"{symbol} {timeframe} API 요청: since={since_ms}, limit={limit}")

                candles = client.get_candles(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=since_ms,
                    limit=limit
                )

                page_count += 1

                # UI 업데이트 (매 5페이지마다)
                if total_tasks > 0 and page_count % 5 == 0:
                    self.progress_updated.emit(
                        f"{exchange_id} {symbol} {timeframe} 수집 중 (페이지 {page_count})",
                        current_task,
                        total_tasks
                    )

                logger.info("DataCollector",
                           f"{symbol} {timeframe} 페이지 {page_count}: "
                           f"{len(candles) if candles else 0}개 캔들")

            except Exception as e:
                import traceback
                logger.error("DataCollector",
                            f"{symbol} {timeframe} API 호출 실패: {str(e)}",
                            traceback.format_exc())
                break

            if not candles:
                consecutive_empty_pages += 1
                logger.info("DataCollector",
                           f"{symbol} {timeframe}: 빈 페이지 {consecutive_empty_pages}/{max_empty_pages}")

                if consecutive_empty_pages >= max_empty_pages:
                    logger.info("DataCollector",
                               f"{symbol} {timeframe}: 연속 빈 페이지로 수집 완료")
                    break
                else:
                    # 다음 시도를 위해 잠시 대기
                    time.sleep(1)
                    continue
            else:
                consecutive_empty_pages = 0  # 빈 페이지 초기화
            
            # 캔들 변환 및 중복 확인
            new_candles_count = 0
            duplicate_count = 0

            for candle in candles:
                # 중복 타임스탬프 확인 (방지책)
                candle_timestamp = candle['timestamp']

                # 이미 있는 타임스탬프면 건너뛰
                if any(c['timestamp'] == candle_timestamp for c in all_candles):
                    duplicate_count += 1
                    continue

                all_candles.append({
                    "exchange_id": exchange_id,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "timestamp": candle['timestamp'],
                    "open": candle['open'],
                    "high": candle['high'],
                    "low": candle['low'],
                    "close": candle['close'],
                    "volume": candle['volume']
                })
                new_candles_count += 1

            if duplicate_count > 0:
                logger.info("DataCollector",
                           f"{symbol} {timeframe} 페이지 {page_count}: "
                           f"{new_candles_count}개 신규, {duplicate_count}개 중복 스킵")

            # 중간 저장 (10,000개 단위)
            if len(all_candles) >= 10000:
                try:
                    # 진행률 업데이트 (페이지 50개마다 업데이트)
                    if page_count % 50 == 0 or page_count < 10:
                        saved_count = 10000
                        self.progress_updated.emit(
                            f"{exchange_id} {symbol} {timeframe} 수집 및 저장 중... (총 {page_count}페이지, {saved_count * (page_count // 50 + 1)}개 저장 완료)",
                            current_task,
                            total_tasks
                        )

                    self.candles_repo.insert_candles_batch(all_candles)
                    logger.info("DataCollector",
                               f"{symbol} {timeframe}: 중간 저장 {len(all_candles)}개 캔들")

                    # 메모리 초기화
                    all_candles = []

                    # 짧은 대기로 DB 부하 완화
                    time.sleep(0.5)

                except Exception as e:
                    logger.error("DataCollector",
                               f"{symbol} {timeframe} 중간 저장 실패: {str(e)}")
                    # 저장 실패해도 계속 진행 (메모리 초기화하여 중복 방지)
                    all_candles = []
                    break

            # 다음 페이지 처리
            # limit보다 적게 받았으면 마지막 페이지로 간주
            if len(candles) < limit:
                logger.info("DataCollector",
                           f"{symbol} {timeframe}: 마지막 페이지 도달 ({len(candles)} < {limit})")
                break

            # 다음 페이지 요청을 위한 시간 계산
            if candles and len(candles) > 0:
                # 마지막 캔들 시간 + 1ms (timestamp_ms 또는 timestamp)
                if 'timestamp_ms' in candles[-1]:
                    since_ms = candles[-1]['timestamp_ms'] + 1
                elif 'timestamp' in candles[-1]:
                    # timestamp는 밀리초 단위라고 가정
                    since_ms = candles[-1]['timestamp'] + 1
                else:
                    # 기존 로직을 1분 증가
                    since_ms += 60 * 1000

                # 다음 요청까지의 대기 (레이트 리밋 준수)
                if exchange_id == "okx" and timeframe == "1m":
                    time.sleep(0.2)  # OKX 1분봉은 더 긴 대기
                else:
                    time.sleep(0.1)  # 기본 레이트 리밋
        
        # DB 저장
        if all_candles:
            try:
                # DB 저장 중 표시
                if total_tasks > 0:
                    total_pages = page_count if page_count > 0 else 1
                    self.progress_updated.emit(
                        f"{exchange_id} {symbol} {timeframe} 최종 저장 중... (총 {total_pages}페이지, {len(all_candles)}개 캔들)",
                        current_task,
                        total_tasks
                    )
                
                self.candles_repo.insert_candles_batch(all_candles)
                logger.info("DataCollector", 
                           f"{exchange_id} {symbol} {timeframe}: {len(all_candles)}개 캔들 저장")
                
                # 보조지표 계산
                if total_tasks > 0:
                    self.progress_updated.emit(
                        f"{exchange_id} {symbol} {timeframe} 지표 계산 중...",
                        current_task,
                        total_tasks
                    )
                
                self._calculate_and_save_indicators(exchange_id, symbol, timeframe)
                
            except Exception as e:
                import traceback
                logger.error("DataCollector", 
                            f"{symbol} {timeframe} DB 저장 실패: {str(e)}", 
                            traceback.format_exc())
        else:
            logger.warning("DataCollector", f"{symbol} {timeframe}: 수집된 캔들 없음")
    
    def _calculate_and_save_indicators(self, exchange_id: str, 
                                       symbol: str, timeframe: str):
        """보조지표 계산 및 저장"""
        # 최근 250개 캔들 조회
        candles = self.candles_repo.get_candles(
            exchange_id, symbol, timeframe, limit=250
        )

        # 최소 개수 조정 (일봉은 7개만 있어도 계산 가능하도록)
        min_required = 20 if timeframe == "1d" else 50

        if len(candles) < min_required:
            logger.warning("DataCollector",
                          f"{exchange_id} {symbol} {timeframe}: 지표 계산 불가 (캔들 부족: {len(candles)}/{min_required})")
            return
        
        # 최신 캔들 기준으로 지표 계산
        candles.reverse()  # 오래된 순으로 정렬
        indicators = IndicatorCalculator.calculate_all_indicators(candles)
        
        if indicators:
            latest_candle = candles[-1]
            self.indicators_repo.upsert_indicators(
                exchange_id,
                symbol,
                timeframe,
                latest_candle['timestamp'],
                indicators
            )
            logger.info("DataCollector",
                       f"{exchange_id} {symbol} {timeframe}: 지표 계산 완료 - "
                       f"MA20={indicators.get('ma_20', 'N/A')}, "
                       f"RSI={indicators.get('rsi', 'N/A')}, "
                       f"MACD={indicators.get('macd', 'N/A')}")
        else:
            logger.warning("DataCollector",
                          f"{exchange_id} {symbol} {timeframe}: 지표 계산 실패 (결과 없음)")
    
    def realtime_update(self, exchange_id: str, symbols: List[str]):
        """실시간 데이터 업데이트 (주기적 호출)"""
        if not self.is_realtime_enabled:
            return
        
        client = get_public_client(exchange_id)
        if not client:
            return
        
        for symbol in symbols:
            for timeframe in TIMEFRAMES:
                if not self.is_running:
                    break
                
                try:
                    # 최신 캔들만 가져오기
                    candles = client.get_candles(
                        symbol=symbol,
                        timeframe=timeframe,
                        limit=1
                    )
                    
                    if candles:
                        candle = candles[0]
                        self.candles_repo.insert_candle(
                            exchange_id,
                            symbol,
                            timeframe,
                            candle['timestamp'],
                            candle['open'],
                            candle['high'],
                            candle['low'],
                            candle['close'],
                            candle['volume']
                        )
                        
                        # 지표 재계산
                        self._calculate_and_save_indicators(exchange_id, symbol, timeframe)
                    
                except Exception as e:
                    logger.error("DataCollector", 
                               f"{exchange_id} {symbol} {timeframe} 실시간 업데이트 실패: {str(e)}")
                
                time.sleep(0.05)  # Rate limit
    
    def run_continuous(self, exchange_id: str, symbols: List[str], 
                      interval_seconds: int = None):
        """지속적 실행 (스레드에서 호출)"""
        self.is_running = True
        interval = interval_seconds or DATA_POLLING_INTERVAL
        
        logger.info("DataCollector", 
                   f"{exchange_id} 지속적 데이터 수집 시작 (간격: {interval}초)")
        
        while self.is_running:
            if self.is_realtime_enabled:
                self.realtime_update(exchange_id, symbols)
            
            time.sleep(interval)
        
        logger.info("DataCollector", "데이터 수집 중지")
    
    def stop(self):
        """워커 중지"""
        self.is_running = False


class MultiExchangeDataCollector(QObject):
    """멀티 거래소 데이터 수집기"""
    
    progress_updated = Signal(str, int, int)  # exchange_symbol_tf, current, total
    collection_completed = Signal(str)  # exchange_id
    all_completed = Signal()
    error_occurred = Signal(str, str)  # exchange_id, error_msg
    
    def __init__(self):
        super().__init__()
        self.workers: Dict[str, DataCollectorWorker] = {}
        self.is_running = False
    
    def collect_all_exchanges(self, exchanges_symbols: Dict[str, List[str]], 
                             start_date: datetime):
        """
        모든 거래소 데이터 수집
        
        Args:
            exchanges_symbols: {exchange_id: [symbol1, symbol2, ...]}
            start_date: 시작 날짜
        """
        self.is_running = True
        
        total_exchanges = len(exchanges_symbols)
        completed = 0
        
        for exchange_id, symbols in exchanges_symbols.items():
            if not self.is_running:
                break
            
            logger.info("MultiCollector", f"{exchange_id} 수집 시작")
            
            worker = DataCollectorWorker(exchange_id=exchange_id)
            worker.progress_updated.connect(
                lambda msg, cur, tot, ex=exchange_id: 
                self.progress_updated.emit(f"{ex}: {msg}", cur, tot)
            )
            worker.error_occurred.connect(
                lambda err, ex=exchange_id: self.error_occurred.emit(ex, err)
            )
            
            self.workers[exchange_id] = worker
            
            try:
                worker.backfill_data(symbols, start_date, exchange_id)
                completed += 1
                self.collection_completed.emit(exchange_id)
            except Exception as e:
                self.error_occurred.emit(exchange_id, str(e))
        
        self.is_running = False
        self.all_completed.emit()
    
    def stop(self):
        """모든 워커 중지"""
        self.is_running = False
        for worker in self.workers.values():
            worker.stop()
