"""
백테스트 엔진
마틴게일 DCA 전략 백테스트 실행
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from PySide6.QtCore import QObject, Signal

from database.repository import CandlesRepository, BacktestResultsRepository
from config.exchanges import get_exchange_fee
from utils.logger import logger
from utils.time_helper import time_helper


@dataclass
class BacktestConfig:
    """백테스트 설정"""
    exchange_id: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    
    # 전략 설정
    direction: str = "LONG"  # LONG or SHORT
    initial_capital: float = 1000.0  # 초기 자본 (USDT)
    leverage: int = 10
    margin_mode: str = "isolated"
    
    # TP/SL 설정
    tp_offset_pct: float = 1.0  # 익절 %
    sl_offset_pct: float = 2.0  # 손절 %
    
    # 마틴게일 설정
    martingale_enabled: bool = False
    martingale_steps: int = 5
    martingale_offset_pct: float = 1.0  # 각 단계 간격 %
    martingale_size_ratios: List[float] = field(
        default_factory=lambda: [1, 1, 2, 4, 8]
    )
    
    # 수수료
    use_exchange_fee: bool = True
    custom_fee: float = 0.0005  # 0.05%
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Trade:
    """개별 거래"""
    entry_time: str
    entry_price: float
    exit_time: str = ""
    exit_price: float = 0.0
    side: str = "long"
    size: float = 0.0
    leverage: int = 1
    pnl: float = 0.0
    fees: float = 0.0
    exit_reason: str = ""
    martingale_level: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Position:
    """포지션 상태"""
    is_open: bool = False
    side: str = "long"
    entry_price: float = 0.0
    entry_time: str = ""
    size: float = 0.0
    leverage: int = 1
    
    # 마틴게일 상태
    martingale_level: int = 0
    martingale_orders: List[Dict] = field(default_factory=list)
    total_size: float = 0.0
    avg_entry_price: float = 0.0
    
    # TP/SL 가격
    tp_price: float = 0.0
    sl_price: float = 0.0


class BacktestEngine(QObject):
    """백테스트 엔진"""
    
    # Signals
    progress_updated = Signal(str, int, int)  # message, current, total
    backtest_completed = Signal(dict)  # 결과
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.candles_repo = CandlesRepository()
        self.results_repo = BacktestResultsRepository()
        
        self.config: Optional[BacktestConfig] = None
        self.is_running = False
        
        # 백테스트 상태
        self.capital = 0.0
        self.position = Position()
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []
        
        # 수수료
        self.fee_rate = 0.0
    
    def run(self, config: BacktestConfig) -> Optional[Dict]:
        """
        백테스트 실행
        
        Args:
            config: 백테스트 설정
        
        Returns:
            백테스트 결과 또는 None
        """
        self.is_running = True
        self.config = config
        
        logger.info("Backtest", 
                   f"백테스트 시작: {config.exchange_id} {config.symbol} "
                   f"{config.start_date} ~ {config.end_date}")
        
        try:
            # 초기화
            self._initialize()
            
            # 캔들 데이터 로드
            candles = self._load_candles()
            if not candles:
                self.error_occurred.emit("캔들 데이터가 없습니다.")
                return None
            
            total_candles = len(candles)
            logger.info("Backtest", f"총 {total_candles}개 캔들 로드")
            
            # 캔들 순회하며 백테스트
            for i, candle in enumerate(candles):
                if not self.is_running:
                    logger.warning("Backtest", "백테스트 중단됨")
                    break
                
                self._process_candle(candle, i)
                
                # 진행률 업데이트 (100개마다)
                if i % 100 == 0:
                    self.progress_updated.emit(
                        f"처리 중: {candle['timestamp']}",
                        i + 1,
                        total_candles
                    )
            
            # 열린 포지션 강제 청산 (백테스트 종료)
            if self.position.is_open:
                last_candle = candles[-1]
                self._close_position(last_candle, "백테스트 종료")
            
            # 결과 계산
            result = self._calculate_results()
            
            # DB 저장
            result_id = self._save_results(result)
            result['id'] = result_id
            
            logger.info("Backtest", 
                       f"백테스트 완료: 수익률 {result['total_return']:.2f}%, "
                       f"MDD {result['max_drawdown']:.2f}%")
            
            self.backtest_completed.emit(result)
            return result
            
        except Exception as e:
            import traceback
            error_msg = f"백테스트 실패: {str(e)}"
            logger.error("Backtest", error_msg, traceback.format_exc())
            self.error_occurred.emit(error_msg)
            return None
        finally:
            self.is_running = False
    
    def _initialize(self):
        """백테스트 초기화"""
        self.capital = self.config.initial_capital
        self.position = Position()
        self.trades = []
        self.equity_curve = []
        
        # 수수료 설정
        if self.config.use_exchange_fee:
            self.fee_rate = get_exchange_fee(self.config.exchange_id, 'taker')
        else:
            self.fee_rate = self.config.custom_fee
    
    def _load_candles(self) -> List[Dict]:
        """캔들 데이터 로드"""
        return self.candles_repo.get_candles_for_backtest(
            exchange_id=self.config.exchange_id,
            symbol=self.config.symbol,
            timeframe=self.config.timeframe,
            start_time=self.config.start_date,
            end_time=self.config.end_date
        )
    
    def _process_candle(self, candle: Dict, index: int):
        """캔들 처리"""
        timestamp = candle['timestamp']
        open_price = candle['open']
        high = candle['high']
        low = candle['low']
        close = candle['close']
        
        if self.position.is_open:
            # 포지션 있음 - TP/SL 및 마틴게일 체크
            self._check_tp_sl(candle)
            
            if self.config.martingale_enabled and self.position.is_open:
                self._check_martingale(candle)
        else:
            # 포지션 없음 - 진입 (첫 캔들 이후부터)
            if index > 0:
                self._open_position(candle)
        
        # 자산 곡선 기록
        equity = self._calculate_equity(close)
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': equity,
            'price': close
        })
    
    def _open_position(self, candle: Dict):
        """포지션 진입"""
        price = candle['close']
        timestamp = candle['timestamp']
        
        # 포지션 크기 계산 (초기 증거금의 일부 사용)
        margin_per_trade = self.capital * 0.1  # 10% 사용
        size = (margin_per_trade * self.config.leverage) / price
        
        # 수수료
        fee = size * price * self.fee_rate
        self.capital -= fee
        
        # 포지션 설정
        self.position = Position(
            is_open=True,
            side="long" if self.config.direction == "LONG" else "short",
            entry_price=price,
            entry_time=timestamp,
            size=size,
            leverage=self.config.leverage,
            martingale_level=0,
            total_size=size,
            avg_entry_price=price
        )
        
        # TP/SL 가격 계산
        if self.config.direction == "LONG":
            self.position.tp_price = price * (1 + self.config.tp_offset_pct / 100)
            self.position.sl_price = price * (1 - self.config.sl_offset_pct / 100)
        else:
            self.position.tp_price = price * (1 - self.config.tp_offset_pct / 100)
            self.position.sl_price = price * (1 + self.config.sl_offset_pct / 100)
        
        # 마틴게일 주문 설정
        if self.config.martingale_enabled:
            self._setup_martingale_orders(price)
        
        logger.debug("Backtest", 
                    f"진입: {self.position.side} {size:.4f} @ {price:.2f}")
    
    def _setup_martingale_orders(self, entry_price: float):
        """마틴게일 주문 설정"""
        self.position.martingale_orders = []
        
        for i in range(self.config.martingale_steps):
            ratio = self.config.martingale_size_ratios[i] if i < len(self.config.martingale_size_ratios) else 1
            
            if self.config.direction == "LONG":
                # 롱: 가격 하락 시 추가 매수
                trigger_price = entry_price * (1 - (self.config.martingale_offset_pct * (i + 1)) / 100)
            else:
                # 숏: 가격 상승 시 추가 매도
                trigger_price = entry_price * (1 + (self.config.martingale_offset_pct * (i + 1)) / 100)
            
            self.position.martingale_orders.append({
                'level': i + 1,
                'trigger_price': trigger_price,
                'size_ratio': ratio,
                'filled': False
            })
    
    def _check_tp_sl(self, candle: Dict):
        """TP/SL 체크"""
        high = candle['high']
        low = candle['low']
        
        if self.config.direction == "LONG":
            # 롱 포지션
            if high >= self.position.tp_price:
                # 익절
                self._close_position(candle, "TP", self.position.tp_price)
            elif low <= self.position.sl_price:
                # 손절
                self._close_position(candle, "SL", self.position.sl_price)
        else:
            # 숏 포지션
            if low <= self.position.tp_price:
                # 익절
                self._close_position(candle, "TP", self.position.tp_price)
            elif high >= self.position.sl_price:
                # 손절
                self._close_position(candle, "SL", self.position.sl_price)
    
    def _check_martingale(self, candle: Dict):
        """마틴게일 체크"""
        high = candle['high']
        low = candle['low']
        
        for order in self.position.martingale_orders:
            if order['filled']:
                continue
            
            trigger_price = order['trigger_price']
            triggered = False
            
            if self.config.direction == "LONG":
                # 롱: 가격 하락 시 추가 매수
                if low <= trigger_price:
                    triggered = True
            else:
                # 숏: 가격 상승 시 추가 매도
                if high >= trigger_price:
                    triggered = True
            
            if triggered:
                self._execute_martingale(candle, order)
    
    def _execute_martingale(self, candle: Dict, order: Dict):
        """마틴게일 주문 실행"""
        price = order['trigger_price']
        base_size = self.position.size  # 초기 포지션 크기
        add_size = base_size * order['size_ratio']
        
        # 수수료
        fee = add_size * price * self.fee_rate
        self.capital -= fee
        
        # 평균 진입가 재계산
        total_value = (self.position.total_size * self.position.avg_entry_price) + (add_size * price)
        new_total_size = self.position.total_size + add_size
        self.position.avg_entry_price = total_value / new_total_size
        self.position.total_size = new_total_size
        self.position.martingale_level = order['level']
        
        order['filled'] = True
        
        # TP/SL 재설정 (평균가 기준)
        if self.config.direction == "LONG":
            self.position.tp_price = self.position.avg_entry_price * (1 + self.config.tp_offset_pct / 100)
            self.position.sl_price = self.position.avg_entry_price * (1 - self.config.sl_offset_pct / 100)
        else:
            self.position.tp_price = self.position.avg_entry_price * (1 - self.config.tp_offset_pct / 100)
            self.position.sl_price = self.position.avg_entry_price * (1 + self.config.sl_offset_pct / 100)
        
        logger.debug("Backtest", 
                    f"마틴 {order['level']}단계: +{add_size:.4f} @ {price:.2f}, "
                    f"평균가: {self.position.avg_entry_price:.2f}")
    
    def _close_position(self, candle: Dict, reason: str, exit_price: float = None):
        """포지션 청산"""
        if not self.position.is_open:
            return
        
        price = exit_price or candle['close']
        timestamp = candle['timestamp']
        
        # PnL 계산
        if self.config.direction == "LONG":
            pnl_pct = (price - self.position.avg_entry_price) / self.position.avg_entry_price
        else:
            pnl_pct = (self.position.avg_entry_price - price) / self.position.avg_entry_price
        
        # 레버리지 적용
        pnl_pct *= self.config.leverage
        
        # 실제 PnL (USDT)
        position_value = self.position.total_size * self.position.avg_entry_price / self.config.leverage
        pnl = position_value * pnl_pct
        
        # 수수료
        fee = self.position.total_size * price * self.fee_rate
        self.capital -= fee
        
        # 자본 업데이트
        self.capital += pnl
        
        # 거래 기록
        trade = Trade(
            entry_time=self.position.entry_time,
            entry_price=self.position.avg_entry_price,
            exit_time=timestamp,
            exit_price=price,
            side=self.position.side,
            size=self.position.total_size,
            leverage=self.config.leverage,
            pnl=pnl,
            fees=fee * 2,  # 진입 + 청산 수수료
            exit_reason=reason,
            martingale_level=self.position.martingale_level
        )
        self.trades.append(trade)
        
        logger.debug("Backtest", 
                    f"청산: {reason}, PnL: {pnl:.2f} USDT ({pnl_pct*100:.2f}%), "
                    f"마틴: {self.position.martingale_level}단계")
        
        # 포지션 초기화
        self.position = Position()
    
    def _calculate_equity(self, current_price: float) -> float:
        """현재 자산 계산"""
        equity = self.capital
        
        if self.position.is_open:
            # 미실현 PnL
            if self.config.direction == "LONG":
                pnl_pct = (current_price - self.position.avg_entry_price) / self.position.avg_entry_price
            else:
                pnl_pct = (self.position.avg_entry_price - current_price) / self.position.avg_entry_price
            
            pnl_pct *= self.config.leverage
            position_value = self.position.total_size * self.position.avg_entry_price / self.config.leverage
            unrealized_pnl = position_value * pnl_pct
            equity += unrealized_pnl
        
        return equity
    
    def _calculate_results(self) -> Dict:
        """결과 계산"""
        from backtest.metrics import BacktestMetrics
        
        metrics = BacktestMetrics.calculate(
            trades=self.trades,
            equity_curve=self.equity_curve,
            initial_capital=self.config.initial_capital,
            final_capital=self.capital
        )
        
        return {
            'exchange_id': self.config.exchange_id,
            'symbol': self.config.symbol,
            'timeframe': self.config.timeframe,
            'start_date': self.config.start_date,
            'end_date': self.config.end_date,
            'strategy_config': self.config.to_dict(),
            'initial_capital': self.config.initial_capital,
            'final_capital': self.capital,
            **metrics,
            'trades': [t.to_dict() for t in self.trades],
            'equity_curve': self.equity_curve
        }
    
    def _save_results(self, result: Dict) -> int:
        """결과 저장"""
        return self.results_repo.insert_result(result)
    
    def stop(self):
        """백테스트 중지"""
        self.is_running = False

