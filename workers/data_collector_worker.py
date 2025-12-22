"""
데이터 수집 워커
"""
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict
from PySide6.QtCore import QObject, Signal, QThread

from indicators.calculator import IndicatorCalculator
from database.repository import CandlesRepository, IndicatorsRepository
from api.okx_client import OKXClient
from api.exchange_factory import ExchangeFactory
from utils.logger import logger
from utils.time_helper import time_helper
from config.settings import TIMEFRAMES, DATA_RETENTION_DAYS
import pandas as pd


class DataCollectorWorker(QObject):
    """데이터 수집 워커"""

    # Signals
    progress_updated = Signal(str, int, int)  # message, current, total
    collection_completed = Signal()
    error_occurred = Signal(str)
    log_message = Signal(str)  # 로그 메시지

    def __init__(self):
        super().__init__()
        self.indicator_calc = IndicatorCalculator()

        # 데이터베이스 연결 (나중에 초기화)
        self.candles_repo = None
        self.indicators_repo = None

        self.is_running = False
        self.is_realtime_enabled = False

        # 쓰레딩 락크
        self.collection_lock = threading.Lock()

    def init_repositories(self):
        """레포지토리 초기화"""
        try:
            self.candles_repo = CandlesRepository()
            self.indicators_repo = IndicatorsRepository()
            logger.info("DataCollectorWorker", "레포지토리 초기화 성공")
        except Exception as e:
            logger.error("DataCollectorWorker", f"레포지토리 초기화 실패: {str(e)}")
            raise

    def set_realtime_enabled(self, enabled: bool):
        """실시간 최신화 활성화 설정"""
        self.is_realtime_enabled = enabled
        logger.info("DataCollectorWorker", f"실시간 최신화: {'활성' if enabled else '비활성'}")
        self.log_message.emit(f"실시간 최신화: {'활성' if enabled else '비활성'}")

    def backfill_data(self, symbols: List[str], start_date: datetime, exchange_id: str = "okx"):
        """
        과거 데이터 백필

        Args:
            symbols: 수집할 심볼 목록
            start_date: 시작 날짜 (KST)
            exchange_id: 거래소 ID
        """
        # 레포지토리가 초기화되지 않았으면 초기화
        if self.candles_repo is None:
            self.init_repositories()

        with self.collection_lock:
            self.is_running = True

        self.log_message.emit(f"{exchange_id.upper()} 거래소 데이터 백필 시작: {len(symbols)}개 심볼")
        logger.info("DataCollectorWorker", f"{exchange_id.upper()} 거래소 데이터 백필 시작: {len(symbols)}개 심볼")

        total_tasks = len(symbols) * len(TIMEFRAMES)
        current_task = 0

        try:
            # 거래소 클라이언트 생성
            client = self._get_exchange_client(exchange_id)
            if not client:
                raise Exception(f"{exchange_id} 거래소 클라이언트 생성 실패")

            for symbol in symbols:
                if not self.is_running:
                    self.log_message.emit("데이터 백필 중단됨")
                    logger.warning("DataCollectorWorker", "데이터 백필 중단됨")
                    break

                for timeframe in TIMEFRAMES:
                    if not self.is_running:
                        break

                    current_task += 1
                    progress_msg = f"[{exchange_id.upper()}] {symbol} {timeframe} 수집 시작"

                    self.progress_updated.emit(progress_msg, current_task, total_tasks)
                    self.log_message.emit(progress_msg)

                    try:
                        self._collect_candles_with_indicators(client, symbol, timeframe, start_date, exchange_id)
                    except Exception as e:
                        error_msg = f"[{exchange_id.upper()}] {symbol} {timeframe} 수집 실패: {str(e)}"
                        logger.error("DataCollectorWorker", error_msg)
                        self.error_occurred.emit(error_msg)
                        continue

        finally:
            with self.collection_lock:
                self.is_running = False

        self.log_message.emit(f"{exchange_id.upper()} 거래소 데이터 백필 완료")
        logger.info("DataCollectorWorker", f"{exchange_id.upper()} 거래소 데이터 백필 완료")
        self.collection_completed.emit()

    def _get_exchange_client(self, exchange_id: str):
        """거래소 클라이언트 생성"""
        try:
            if exchange_id.lower() == "okx":
                return OKXClient()
            else:
                # ExchangeFactory를 사용한 다른 거래소 클라이언트 생성
                return ExchangeFactory.create_client(exchange_id)
        except Exception as e:
            logger.error("DataCollectorWorker", f"거래소 클라이언트 생성 실패: {str(e)}")
            return None

    def _collect_candles_with_indicators(self, client, symbol: str, timeframe: str, start_date: datetime, exchange_id: str):
        """캔들 데이터와 보조지표 함께 수집"""
        try:

            # 최신 타임스탬프 조회
            latest_timestamp = self._get_latest_timestamp(symbol, timeframe, exchange_id)

            if latest_timestamp:
                # 최신 데이터부터 수집
                from_ts = latest_timestamp + timedelta(minutes=1)  # 다음 1분봉부터
            else:
                # 시작 날짜부터 수집
                from_ts = start_date

            to_timestamp = datetime.now()

            self.log_message.emit(f"[{exchange_id.upper()}] {symbol} {timeframe} 수집 범위: {from_ts.strftime('%Y-%m-%d %H:%M')} ~ {to_timestamp.strftime('%Y-%m-%d %H:%M')}")

            # 1분봉 데이터 수집
            candles_data = self._fetch_minute_candles(client, symbol, from_ts, to_timestamp)

            if not candles_data:
                self.log_message.emit(f"[{exchange_id.upper()}] {symbol} {timeframe} 수집할 데이터 없음")
                return

            # DataFrame으로 변환
            df = pd.DataFrame(candles_data)

            # 보조지표 계산
            self.log_message.emit(f"[{exchange_id.upper()}] {symbol} {timeframe} 보조지표 계산 중...")
            indicators = self.indicator_calc.calculate_all_indicators(df)

            # 데이터베이스에 저장
            self._save_candles_with_indicators(df, indicators, symbol, timeframe, exchange_id)

            self.log_message.emit(f"[{exchange_id.upper()}] {symbol} {timeframe} {len(df)}개 데이터 저장 완료")

        except Exception as e:
            logger.error("DataCollectorWorker", f"{symbol} {timeframe} 수집 실패: {str(e)}")
            raise

    def _fetch_minute_candles(self, client: OKXClient, symbol: str, from_ts: datetime, to_ts: datetime) -> List[Dict]:
        """1분봉 데이터 수집"""
        candles = []
        current_from = from_ts
        batch_size = 1440  # 1일치 1분봉 (최대 요청 개수 고려)

        while current_from < to_ts:
            current_to = min(current_from + timedelta(minutes=batch_size), to_ts)

            try:
                # OKX API에서 1분봉 데이터 조회
                batch_candles = client.get_candles(symbol, "1m", current_from, current_to)

                if batch_candles:
                    candles.extend(batch_candles)
                    self.log_message.emit(f"  {len(batch_candles)}개 수집 (잔여: {(to_timestamp - current_to).total_seconds() // 60:.0f}분)")

                # API 레이트 리밋 방지
                time.sleep(0.2)

            except Exception as e:
                logger.error("DataCollectorWorker", f"API 호출 실패: {str(e)}")
                self.log_message.emit(f"API 호출 실패: {str(e)}")
                time.sleep(1)  # 오류 시 대기 후 재시도

            current_from = current_to

        return candles

    def _get_latest_timestamp(self, symbol: str, timeframe: str, exchange_id: str) -> datetime:
        """최신 타임스탬프 조회"""
        try:
            latest_ts_str = self.candles_repo.get_latest_timestamp(exchange_id, symbol, timeframe)
            if latest_ts_str:
                return datetime.fromisoformat(latest_ts_str)
            return None
        except Exception as e:
            logger.warning("DataCollectorWorker", f"최신 타임스탬프 조회 실패: {str(e)}")
            return None

    def _save_candles_with_indicators(self, df: pd.DataFrame, indicators: Dict, symbol: str, timeframe: str, exchange_id: str):
        """캔들과 보조지표 데이터베이스 저장"""
        try:
            # 캔들 데이터 저장
            for _, row in df.iterrows():
                timestamp = row['timestamp']
                open_price = float(row['open'])
                high_price = float(row['high'])
                low_price = float(row['low'])
                close_price = float(row['close'])
                volume = float(row['volume'])

                self.candles_repo.insert_candle(
                    exchange_id=exchange_id,
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume
                )

            # 보조지표 저장 (최신 데이터만)
            if indicators:
                self.indicators_repo.update_indicators(
                    exchange_id=exchange_id,
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=df['timestamp'].iloc[-1],  # 최신 타임스탬프
                    indicators=indicators
                )

        except Exception as e:
            logger.error("DataCollectorWorker", f"데이터 저장 실패: {str(e)}")
            raise

    def stop_collection(self):
        """데이터 수집 중지"""
        with self.collection_lock:
            self.is_running = False

        self.log_message.emit("데이터 수집 중지 요청")
        logger.info("DataCollectorWorker", "데이터 수집 중지됨")