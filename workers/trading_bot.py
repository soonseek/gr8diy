"""
자동매매 봇 워커
CCXT 멀티 거래소 지원 버전
"""
import time
from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal
from datetime import datetime

from api.ccxt_client import CCXTClient
from database.repository import (
    BotConfigsRepository, OrdersRepository, 
    PositionsRepository, BotLogsRepository, TradesHistoryRepository
)
from utils.logger import logger
from utils.time_helper import time_helper


class TradingBotWorker(QObject):
    """자동매매 봇 워커 (CCXT)"""
    
    # Signals
    position_opened = Signal(str, str, float)  # symbol, side, size
    order_placed = Signal(str, str, str, float)  # symbol, order_type, side, price
    error_occurred = Signal(str, str)  # symbol, error_msg
    bot_stopped = Signal(str)  # symbol
    existing_position_found = Signal(str, str)  # symbol, message
    position_closed = Signal(str, float)  # symbol, pnl
    
    def __init__(self, client: CCXTClient, config: Dict):
        super().__init__()
        self.client = client  # CCXT 클라이언트
        self.config = config
        self.exchange_id = config.get('exchange_id', 'okx')
        self.is_running = False
        
        # Repositories
        self.orders_repo = OrdersRepository()
        self.positions_repo = PositionsRepository()
        self.bot_logs_repo = BotLogsRepository()
        self.trades_repo = TradesHistoryRepository()
        
        # 상태
        self.position_id = None
        self.entry_order_id = None
        self.tp_order_id = None
        self.sl_order_id = None
        self.martingale_level = 0
        self.martingale_order_ids = []
        
        # 제어
        self.auto_restart = True  # 익절/손절 후 자동 재실행
        self.stop_mode = None  # None, 'clean' (청산), 'keep' (유지)
    
    def start_trading(self):
        """거래 시작"""
        self.is_running = True
        symbol = self.config['symbol']
        
        try:
            logger.info("TradingBot", f"{symbol} 봇 시작")
            
            # 자동 재실행 루프
            while self.is_running and self.auto_restart:
                
                direction = self.config['direction']
                logger.info("TradingBot", f"{symbol} 새 사이클 시작 - {direction}")
                
                # 1. 기존 포지션 확인 및 정리
                if not self._check_and_close_existing_positions():
                    break
                
                # 2. 레버리지 설정
                if not self._set_leverage():
                    break
                
                # 3. 시장가 진입
                if not self._open_position():
                    break
                
                # 잠시 대기 (API 인증 안정화)
                time.sleep(1)
                
                # 4. 마틴게일 설정 (활성화된 경우)
                if self.config.get('martingale_enabled'):
                    self._setup_martingale_orders()
                    time.sleep(0.5)
                
                # 5. TP/SL은 이미 진입 주문 시 설정됨
                logger.info("TradingBot", f"{symbol} TP/SL은 진입 시 자동 설정됨")
                
                logger.info("TradingBot", f"{symbol} 초기 설정 완료")
                
                # 6. 모니터링 루프
                self._monitoring_loop()
                
                # 포지션 종료됨 - 재시작 전 대기
                if self.is_running and self.auto_restart:
                    logger.info("TradingBot", f"{symbol} 포지션 종료 - 3초 후 재시작")
                    time.sleep(3)
            
            logger.info("TradingBot", f"{symbol} 봇 완전 종료")
            
        except Exception as e:
            import traceback
            error_msg = f"{symbol} 봇 실행 실패: {str(e)}"
            logger.error("TradingBot", error_msg, traceback.format_exc())
            self.error_occurred.emit(symbol, error_msg)
            self.is_running = False
    
    def _check_and_close_existing_positions(self) -> bool:
        """기존 포지션 확인 및 강제 청산"""
        symbol = self.config['symbol']
        
        try:
            # 해당 심볼의 포지션 조회
            positions = self.client.get_positions(symbol)
            
            if not positions:
                # 포지션 없음 - 정상
                logger.info("TradingBot", f"{symbol} 기존 포지션 없음 - 정상 진행")
                return True
            
            # 포지션이 있는지 확인
            has_position = False
            positions_to_close = []
            
            for pos in positions:
                pos_size = abs(float(pos.get('pos', 0)))
                if pos_size > 0:
                    has_position = True
                    positions_to_close.append(pos)
            
            if not has_position:
                # 포지션 크기가 0 - 정상
                logger.info("TradingBot", f"{symbol} 기존 포지션 없음 - 정상 진행")
                return True
            
            # 기존 포지션 발견 - 경고 및 강제 청산
            logger.warning("TradingBot", f"{symbol} 기존 포지션 발견 - 강제 청산 시작")
            
            for pos in positions_to_close:
                pos_side = pos.get('posSide', '')
                pos_size = abs(float(pos.get('pos', 0)))
                
                # 반대 방향 시장가 주문으로 청산
                close_side = "sell" if pos_side == "long" else "buy"
                
                logger.warning("TradingBot", 
                             f"{symbol} 기존 포지션 청산: {pos_side} {pos_size}")
                
                # 시장가 청산 주문
                close_order = self.client.place_market_order(
                    symbol=symbol,
                    side=close_side,
                    size=pos_size,
                    pos_side=pos_side,
                    reduce_only=True
                )
                
                if close_order:
                    logger.info("TradingBot", 
                               f"{symbol} 기존 포지션 청산 완료: {close_order.get('ordId')}")
                else:
                    logger.error("TradingBot", f"{symbol} 기존 포지션 청산 실패")
            
            # UI 알림
            warning_msg = (
                f"기존 포지션이 발견되어 강제 청산했습니다.\n"
                f"청산된 포지션: {len(positions_to_close)}개\n"
                f"봇을 새로 시작합니다."
            )
            self.existing_position_found.emit(symbol, warning_msg)
            
            # 청산 완료 대기
            time.sleep(2)
            
            # 다시 확인
            check_positions = self.client.get_positions(symbol)
            if check_positions:
                for pos in check_positions:
                    if abs(float(pos.get('pos', 0))) > 0:
                        error_msg = f"{symbol} 포지션 청산 실패 - 봇 실행 중단"
                        logger.error("TradingBot", error_msg)
                        self.error_occurred.emit(symbol, error_msg)
                        return False
            
            logger.info("TradingBot", f"{symbol} 기존 포지션 정리 완료 - 봇 시작")
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"{symbol} 포지션 확인 중 오류: {str(e)}"
            logger.error("TradingBot", error_msg, traceback.format_exc())
            self.error_occurred.emit(symbol, error_msg)
            return False
    
    def _set_leverage(self) -> bool:
        """레버리지 설정"""
        symbol = self.config['symbol']
        leverage = self.config['leverage']
        margin_mode = self.config['margin_mode']
        direction = self.config['direction']
        
        try:
            # 포지션 측 결정 (헤지 모드)
            pos_side = "long" if direction == "LONG" else "short"
            
            success = self.client.set_leverage(
                symbol=symbol,
                leverage=leverage,
                margin_mode=margin_mode
            )
            
            if success:
                logger.info("TradingBot", f"{symbol} 레버리지 {leverage}x 설정 완료")
                return True
            else:
                error_msg = f"{symbol} 레버리지 설정 실패"
                logger.error("TradingBot", error_msg)
                self.error_occurred.emit(symbol, error_msg)
                return False
                
        except Exception as e:
            import traceback
            error_msg = f"{symbol} 레버리지 설정 중 오류: {str(e)}"
            logger.error("TradingBot", error_msg, traceback.format_exc())
            self.error_occurred.emit(symbol, error_msg)
            return False
    
    def _open_position(self) -> bool:
        """시장가 진입"""
        symbol = self.config['symbol']
        direction = self.config['direction']
        max_margin = self.config['max_margin']
        leverage = self.config['leverage']
        margin_mode = self.config['margin_mode']
        
        try:
            # 현재가 조회
            ticker = self.client.get_ticker(symbol)
            if not ticker:
                error_msg = f"{symbol} 현재가 조회 실패"
                logger.error("TradingBot", error_msg)
                self.error_occurred.emit(symbol, error_msg)
                return False
            
            current_price = float(ticker['last'])
            
            # 주문 수량 계산 (증거금 기반)
            # 수량 = (증거금 * 레버리지) / 가격
            raw_size = (max_margin * leverage) / current_price
            
            # 최소 주문 수량 적용 (심볼별)
            # OKX는 일반적으로 계약 1개가 최소 단위
            if "BTC" in symbol or "ETH" in symbol:
                # BTC/ETH는 소수점 많이 허용
                size = max(0.01, round(raw_size, 2))  # 최소 0.01
            elif "SOL" in symbol:
                size = max(0.1, round(raw_size, 1))  # 최소 0.1
            else:
                # 기타 코인은 정수 또는 소수점 1자리
                size = max(1, round(raw_size, 1))  # 최소 1
            
            logger.info("TradingBot", 
                       f"{symbol} 수량 계산: raw={raw_size:.4f}, adjusted={size}")
            
            # 주문 파라미터
            side = "buy" if direction == "LONG" else "sell"
            pos_side = "long" if direction == "LONG" else "short"
            
            # TP/SL 가격 미리 계산
            tp_offset = self.config['tp_offset_pct']
            sl_offset = self.config.get('sl_offset_pct')
            
            if direction == "LONG":
                tp_trigger = current_price * (1 + tp_offset / 100)
                sl_trigger = current_price * (1 - sl_offset / 100) if sl_offset else None
            else:
                tp_trigger = current_price * (1 - tp_offset / 100)
                sl_trigger = current_price * (1 + sl_offset / 100) if sl_offset else None
            
            logger.info("TradingBot", 
                       f"{symbol} 시장가 진입: {side} {size} @ {current_price:.2f}")
            
            sl_trigger_str = f"{sl_trigger:.2f}" if sl_trigger is not None else "None"
            logger.info("TradingBot",
                       f"{symbol} TP/SL 설정: TP={tp_trigger:.2f}, SL={sl_trigger_str}")
            
            # 시장가 주문 + TP/SL
            order = self.client.place_order_with_tp_sl(
                symbol=symbol,
                side=side,
                size=size,
                tp_price=tp_trigger,
                sl_price=sl_trigger,
                pos_side=pos_side
            )
            
            if not order:
                error_msg = f"{symbol} 진입 주문 실패 (수량: {size}, 가격: {current_price:.2f})"
                logger.error("TradingBot", error_msg)
                self.error_occurred.emit(symbol, error_msg)
                
                # 더 자세한 에러 정보 로그
                logger.error("TradingBot", 
                           f"주문 파라미터: side={side}, size={size}, pos_side={pos_side}, "
                           f"td_mode={margin_mode}, leverage={leverage}")
                return False
            
            self.entry_order_id = order['order_id']
            logger.info("TradingBot", f"{symbol} 진입 주문 성공: {self.entry_order_id}")
            
            # DB 저장
            self.orders_repo.insert_order({
                'exchange_id': self.config['exchange_id'],
                'order_id': self.entry_order_id,
                'symbol': symbol,
                'side': side,
                'type': 'market',
                'size': size,
                'status': 'filled'
            })
            
            # 포지션 정보 저장
            self.position_id = self.positions_repo.insert_position({
                'exchange_id': self.config['exchange_id'],
                'symbol': symbol,
                'side': pos_side,
                'size': size,
                'avg_price': current_price,
                'leverage': leverage
            })
            
            # 진입 시간 저장
            self.entry_time = time_helper.format_kst(time_helper.now_kst())
            self.entry_price = current_price
            self.position_size = size
            
            self.position_opened.emit(symbol, pos_side, size)
            
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"{symbol} 포지션 진입 중 오류: {str(e)}"
            logger.error("TradingBot", error_msg, traceback.format_exc())
            self.error_occurred.emit(symbol, error_msg)
            return False
    
    def _place_tp_sl_orders(self) -> bool:
        """TP/SL 주문 생성"""
        symbol = self.config['symbol']
        direction = self.config['direction']
        tp_offset = self.config['tp_offset_pct']
        sl_offset = self.config.get('sl_offset_pct')
        
        try:
            # 현재가 조회
            ticker = self.client.get_ticker(symbol)
            if not ticker:
                return False
            
            current_price = float(ticker['last'])
            
            # 포지션 조회 (재시도 로직 포함)
            position = None
            for retry in range(3):
                time.sleep(0.5)  # 짧은 대기
                position = self.client.get_positions(symbol)
                if position and len(position) > 0:
                    break
                logger.warning("TradingBot", f"{symbol} 포지션 조회 재시도 {retry + 1}/3")
            
            if not position or len(position) == 0:
                error_msg = f"{symbol} 포지션 조회 실패 (3회 재시도 후)"
                logger.error("TradingBot", error_msg)
                
                # 포지션 조회 실패해도 진입 시 저장한 정보 사용
                logger.warning("TradingBot", f"{symbol} 저장된 포지션 정보로 TP/SL 설정 시도")
                
                # 진입 주문 조회로 대체
                entry_order = self.client.get_order(symbol, ord_id=self.entry_order_id)
                if not entry_order:
                    logger.error("TradingBot", f"{symbol} 진입 주문 정보도 조회 실패")
                    return False
                
                pos_size = abs(float(entry_order.get('sz', 0)))
                if pos_size == 0:
                    return False
            else:
                pos_data = position[0]
                pos_size = pos_data.get('size', 0)
                
                if pos_size == 0:
                    error_msg = f"{symbol} 포지션 수량이 0입니다"
                    logger.error("TradingBot", error_msg)
                    return False
            
            # TP/SL 가격 계산
            if direction == "LONG":
                tp_price = current_price * (1 + tp_offset / 100)
                sl_price = current_price * (1 - sl_offset / 100) if sl_offset else None
                tp_side = "sell"
            else:  # SHORT
                tp_price = current_price * (1 - tp_offset / 100)
                sl_price = current_price * (1 + sl_offset / 100) if sl_offset else None
                tp_side = "buy"
            
            pos_side = "long" if direction == "LONG" else "short"
            
            sl_price_str = f"{sl_price:.2f}" if sl_price is not None else "None"
            logger.info("TradingBot", 
                       f"{symbol} TP/SL 설정: TP={tp_price:.2f}, SL={sl_price_str}")
            
            # TP 주문 - 단일 주문에 TP/SL 함께 설정
            # 이미 진입된 포지션에 대해 TP/SL 설정하려면 기존 포지션을 종료하는 주문 필요
            # 가장 간단한 방법: 진입 주문 시 TP/SL을 함께 설정하는 것이지만,
            # 이미 진입했으므로 조건부 주문(알고 주문) 사용이 필요
            
            # TP 지정가 주문
            tp_order = self.client.place_limit_order(
                symbol=symbol,
                side=tp_side,
                size=pos_size,
                price=tp_price,
                pos_side=pos_side,
                reduce_only=True
            )
            
            if tp_order:
                self.tp_order_id = tp_order['order_id']
                logger.info("TradingBot", f"{symbol} TP 주문 생성: {self.tp_order_id}")
                
                self.orders_repo.insert_order({
                    'exchange_id': self.config['exchange_id'],
                    'order_id': self.tp_order_id,
                    'symbol': symbol,
                    'side': tp_side,
                    'type': 'limit',
                    'price': tp_price,
                    'size': pos_size,
                    'status': 'open',
                    'position_id': self.position_id,
                    'related_order_type': 'tp'
                })
            
            # SL 주문 (설정된 경우)
            if sl_offset and sl_price:
                sl_order = self.client.place_limit_order(
                    symbol=symbol,
                    side=tp_side,
                    size=pos_size,
                    price=sl_price,
                    pos_side=pos_side,
                    reduce_only=True
                )
                
                if sl_order:
                    self.sl_order_id = sl_order['order_id']
                    logger.info("TradingBot", f"{symbol} SL 주문 생성: {self.sl_order_id}")
                    
                    self.orders_repo.insert_order({
                        'exchange_id': self.config['exchange_id'],
                        'order_id': self.sl_order_id,
                        'symbol': symbol,
                        'side': tp_side,
                        'type': 'limit',
                        'price': sl_price,
                        'size': pos_size,
                        'status': 'open',
                        'position_id': self.position_id,
                        'related_order_type': 'sl'
                    })
            
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"{symbol} TP/SL 주문 생성 중 오류: {str(e)}"
            logger.error("TradingBot", error_msg, traceback.format_exc())
            return False
    
    def _setup_martingale_orders(self):
        """마틴게일 주문 설정"""
        symbol = self.config['symbol']
        direction = self.config['direction']
        steps = self.config['martingale_steps']
        offset_pct = self.config['martingale_offset_pct']
        margin_mode = self.config['margin_mode']
        
        try:
            logger.info("TradingBot", f"{symbol} 마틴게일 설정 시작 - {steps}단계")
            
            # 현재가 조회
            ticker = self.client.get_ticker(symbol)
            if not ticker:
                logger.error("TradingBot", f"{symbol} 마틴게일 설정 실패 - 현재가 조회 실패")
                return
            
            entry_price = float(ticker['last'])
            
            # 초기 포지션 수량
            initial_size = float(self.config['max_margin']) * self.config['leverage'] / entry_price
            if "BTC" in symbol or "ETH" in symbol:
                initial_size = max(0.01, round(initial_size, 2))
            elif "SOL" in symbol:
                initial_size = max(0.1, round(initial_size, 1))
            else:
                initial_size = max(1, round(initial_size, 1))
            
            # 사이즈 비율 (1, 1, 2, 4, 8, ...)
            size_ratios = [1, 1] + [2 ** i for i in range(steps - 2)] if steps > 2 else [1] * steps
            
            side = "buy" if direction == "LONG" else "sell"
            pos_side = "long" if direction == "LONG" else "short"
            
            # 각 단계별 주문 생성
            for i in range(steps):
                # 마틴게일 가격 계산
                if direction == "LONG":
                    # 롱: 가격이 하락할 때 추가 매수
                    trigger_price = entry_price * (1 - (offset_pct * (i + 1)) / 100)
                else:
                    # 숏: 가격이 상승할 때 추가 매도
                    trigger_price = entry_price * (1 + (offset_pct * (i + 1)) / 100)
                
                # 마틴게일 수량 (비율 적용)
                martin_size = initial_size * size_ratios[i]
                
                logger.info("TradingBot", 
                           f"{symbol} 마틴 {i+1}단계: {side} {martin_size} @ {trigger_price:.2f} "
                           f"(비율: {size_ratios[i]}x)")
                
                # 지정가 주문
                order = self.client.place_limit_order(
                    symbol=symbol,
                    side=side,
                    size=martin_size,
                    price=trigger_price,
                    pos_side=pos_side
                )
                
                if order:
                    order_id = order['order_id']
                    self.martingale_order_ids.append(order_id)
                    logger.info("TradingBot", f"{symbol} 마틴 {i+1}단계 주문 생성: {order_id}")
                    
                    # DB 저장
                    self.orders_repo.insert_order({
                        'exchange_id': self.config['exchange_id'],
                        'order_id': order_id,
                        'symbol': symbol,
                        'side': side,
                        'type': 'limit',
                        'price': trigger_price,
                        'size': martin_size,
                        'status': 'open',
                        'position_id': self.position_id,
                        'related_order_type': f'martingale_{i+1}'
                    })
                else:
                    logger.error("TradingBot", f"{symbol} 마틴 {i+1}단계 주문 실패")
            
            logger.info("TradingBot", f"{symbol} 마틴게일 {steps}단계 주문 완료")
            
        except Exception as e:
            import traceback
            error_msg = f"{symbol} 마틴게일 설정 중 오류: {str(e)}"
            logger.error("TradingBot", error_msg, traceback.format_exc())
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        symbol = self.config['symbol']
        retry_count = 0
        max_retries = 3
        
        logger.info("TradingBot", f"{symbol} 모니터링 시작")
        
        while self.is_running:
            try:
                # 포지션 상태 확인
                position = self.client.get_positions(symbol)
                
                if not position or len(position) == 0:
                    # 조회 실패 시 재시도
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.warning("TradingBot", f"{symbol} 포지션 조회 실패 {max_retries}회 - 봇 중지")
                        self.is_running = False
                        self.bot_stopped.emit(symbol)
                        break
                    
                    logger.warning("TradingBot", f"{symbol} 포지션 조회 실패 - 재시도 {retry_count}/{max_retries}")
                    time.sleep(5)
                    continue
                
                # 조회 성공 시 재시도 카운트 리셋
                retry_count = 0
                
                pos_data = position[0]
                pos_size = pos_data.get('size', 0)
                
                if pos_size == 0:
                    logger.info("TradingBot", f"{symbol} 포지션 청산됨 (TP/SL 체결)")
                    
                    # 청산 시 PNL 저장 (마지막으로 조회한 포지션 정보 사용)
                    # 이전 루프에서 pos_data가 있었으므로 마지막 PNL 사용 가능
                    # 하지만 이미 청산되었으므로 포지션 조회 불가
                    # 대신 이전에 저장한 정보 사용
                    
                    # 청산 시간
                    exit_time = time_helper.format_kst(time_helper.now_kst())
                    
                    # 거래 내역 저장
                    try:
                        self._save_trade_history(exit_time, "TP/SL")
                        logger.info("TradingBot", f"{symbol} 거래 내역 저장 성공")
                    except Exception as e:
                        import traceback
                        logger.error("TradingBot", f"{symbol} 거래 내역 저장 실패: {str(e)}", 
                                   traceback.format_exc())
                    
                    # 미체결 마틴게일 주문 모두 취소
                    self._cancel_all_pending_orders()
                    
                    # PNL 정보는 저장된 값 사용
                    pnl = getattr(self, 'last_pnl', 0.0)
                    
                    self.position_closed.emit(symbol, pnl)
                    
                    # 자동 재실행 모드면 루프 계속, 아니면 종료
                    if self.auto_restart:
                        logger.info("TradingBot", f"{symbol} 자동 재실행 모드 - 다시 진입 준비")
                        break  # 모니터링 루프 탈출 → start_trading 루프로 돌아감
                    else:
                        self.is_running = False
                        self.bot_stopped.emit(symbol)
                        break
                
                # PNL 저장 (청산 시 사용)
                self.last_pnl = pos_data.get('unrealized_pnl', 0)
                self.last_mark_price = pos_data.get('mark_price', 0)
                
                # 10초마다 상태 로그
                if int(time.time()) % 10 == 0:
                    logger.debug("TradingBot", 
                               f"{symbol} 모니터링 중 - 포지션: {pos_size}, "
                               f"가격: {self.last_mark_price:.2f}, "
                               f"PNL: {self.last_pnl:.2f}")
                
                # 1초 대기
                time.sleep(1)
                
            except Exception as e:
                logger.error("TradingBot", f"{symbol} 모니터링 중 오류: {str(e)}")
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error("TradingBot", f"{symbol} 오류 {max_retries}회 발생 - 봇 중지")
                    self.is_running = False
                    self.bot_stopped.emit(symbol)
                    break
                time.sleep(5)
    
    def stop_trading(self, clean_mode: bool = True):
        """
        거래 중지
        clean_mode: True = 포지션/주문 청산, False = 봇만 중지
        """
        self.auto_restart = False
        self.is_running = False
        
        symbol = self.config['symbol']
        
        if clean_mode:
            logger.info("TradingBot", f"{symbol} 봇 중지 (청산 모드) - 즉시 처리")
            
            # 즉시 청산 처리
            try:
                # 1. 모든 미체결 주문 취소
                self._cancel_all_pending_orders()
                
                # 2. 포지션 청산
                positions = self.client.get_positions(symbol)
                if positions:
                    for pos in positions:
                        pos_size = pos.get('size', 0)
                        if pos_size > 0:
                            pos_side = pos.get('side', 'long')
                            close_side = "sell" if pos_side == "long" else "buy"
                            
                            logger.info("TradingBot", f"{symbol} 포지션 청산: {pos_side} {pos_size}")
                            
                            close_order = self.client.place_market_order(
                                symbol=symbol,
                                side=close_side,
                                size=pos_size,
                                pos_side=pos_side,
                                reduce_only=True
                            )
                            
                            if close_order:
                                logger.info("TradingBot", f"{symbol} 청산 주문 성공")
                
                # 청산 후 거래 내역 저장
                exit_time = time_helper.format_kst(time_helper.now_kst())
                try:
                    self._save_trade_history(exit_time, "수동 청산")
                    logger.info("TradingBot", f"{symbol} 수동 청산 내역 저장 완료")
                except Exception as e:
                    logger.error("TradingBot", f"{symbol} 내역 저장 실패: {str(e)}")
                
                logger.info("TradingBot", f"{symbol} 청산 완료")
            except Exception as e:
                import traceback
                logger.error("TradingBot", f"{symbol} 청산 중 오류: {str(e)}", traceback.format_exc())
        else:
            logger.info("TradingBot", f"{symbol} 봇 중지 (유지 모드)")
    
    def _save_trade_history(self, exit_time: str, exit_reason: str):
        """거래 내역 저장"""
        symbol = self.config['symbol']
        
        try:
            # 진입/청산 정보
            entry_time = getattr(self, 'entry_time', time_helper.format_kst(time_helper.now_kst()))
            entry_price = getattr(self, 'entry_price', 0)
            exit_price = getattr(self, 'last_mark_price', 0)
            size = getattr(self, 'position_size', 0)
            leverage = self.config.get('leverage', 1)
            pnl = getattr(self, 'last_pnl', 0)
            fees = 0.0  # TODO: 실제 수수료 계산
            
            side = self.config['direction'].lower()
            
            logger.info("TradingBot", 
                       f"{symbol} 거래 내역 준비: entry={entry_price:.2f}, "
                       f"exit={exit_price:.2f}, pnl={pnl:.2f}")
            
            # DB 저장
            self.trades_repo.insert_trade({
                'exchange_id': self.config['exchange_id'],
                'symbol': symbol,
                'side': side,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'size': size,
                'leverage': leverage,
                'pnl': pnl,
                'fees': fees,
                'entry_time': entry_time,
                'exit_time': exit_time,
                'exit_reason': exit_reason
            })
            
            logger.info("TradingBot", 
                       f"{symbol} 거래 내역 저장: PNL {pnl:.2f} USDT, {exit_reason}")
            
        except Exception as e:
            import traceback
            logger.error("TradingBot", f"{symbol} 거래 내역 저장 실패: {str(e)}", 
                        traceback.format_exc())
    
    def _cancel_all_pending_orders(self):
        """미체결 주문 모두 취소"""
        symbol = self.config['symbol']
        
        try:
            # 마틴게일 주문 취소
            for order_id in self.martingale_order_ids:
                try:
                    self.client.cancel_order(symbol, order_id)
                    logger.debug("TradingBot", f"{symbol} 마틴게일 주문 취소: {order_id}")
                except:
                    pass
            
            self.martingale_order_ids = []
            
            # 모든 미체결 주문 조회 및 취소
            open_orders = self.client.get_open_orders(symbol)
            if open_orders:
                for order in open_orders:
                    order_id = order.get('id')
                    if order_id:
                        try:
                            self.client.cancel_order(symbol, ord_id=order_id)
                            logger.debug("TradingBot", f"{symbol} 주문 취소: {order_id}")
                        except:
                            pass
            
            logger.info("TradingBot", f"{symbol} 모든 미체결 주문 취소 완료")
            
        except Exception as e:
            logger.error("TradingBot", f"{symbol} 주문 취소 중 오류: {str(e)}")

