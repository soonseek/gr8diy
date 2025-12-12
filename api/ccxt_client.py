"""
CCXT 통합 클라이언트
모든 거래소에 대한 공통 인터페이스 제공
"""
import time
import ccxt
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from config.exchanges import (
    SUPPORTED_EXCHANGES, TIMEFRAMES, get_exchange_info, 
    get_exchange_fee, parse_symbol
)
from utils.logger import logger
from utils.time_helper import time_helper


class CCXTClient:
    """CCXT 통합 클라이언트"""
    
    def __init__(self, exchange_id: str, api_key: str = "", secret: str = "", 
                 passphrase: str = "", is_testnet: bool = False):
        """
        Args:
            exchange_id: CCXT 거래소 ID (binance, bybit, okx 등)
            api_key: API 키
            secret: API 시크릿
            passphrase: 패스프레이즈 (OKX 등 일부 거래소)
            is_testnet: 테스트넷 사용 여부
        """
        self.exchange_id = exchange_id
        self.is_testnet = is_testnet
        self.exchange_info = get_exchange_info(exchange_id)
        
        # Rate Limiting
        self.request_timestamps = []
        self.rate_limit_per_second = 10
        self.cooldown_until = 0
        
        # CCXT 인스턴스 생성
        self.exchange = self._create_exchange(api_key, secret, passphrase, is_testnet)
        
        logger.info("CCXT", f"{exchange_id} 클라이언트 초기화 완료 (testnet={is_testnet})")
    
    def _create_exchange(self, api_key: str, secret: str, passphrase: str, 
                        is_testnet: bool) -> ccxt.Exchange:
        """CCXT 거래소 인스턴스 생성"""
        exchange_class = getattr(ccxt, self.exchange_id, None)
        if not exchange_class:
            raise ValueError(f"지원하지 않는 거래소: {self.exchange_id}")
        
        # 기본 설정
        config = {
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # 선물(영구) 거래
                'adjustForTimeDifference': True,
            }
        }
        
        # 패스프레이즈 필요한 거래소
        if passphrase and self.exchange_info.get('requires_passphrase'):
            config['password'] = passphrase
        
        # 테스트넷 설정
        if is_testnet:
            config['sandbox'] = True
        
        exchange = exchange_class(config)
        
        # 타임아웃 설정
        exchange.timeout = 30000  # 30초
        
        return exchange
    
    def _wait_for_rate_limit(self):
        """Rate Limit 대기"""
        current_time = time.time()
        
        # Cooldown 체크
        if current_time < self.cooldown_until:
            wait_time = self.cooldown_until - current_time
            logger.warning("CCXT", f"Rate limit cooldown 중... {wait_time:.1f}초 대기")
            time.sleep(wait_time)
            current_time = time.time()
        
        # 최근 1초 이내 요청 수 체크
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < 1.0
        ]
        
        if len(self.request_timestamps) >= self.rate_limit_per_second:
            sleep_time = 1.0 - (current_time - self.request_timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.request_timestamps.append(time.time())
    
    # ========== 연결 테스트 ==========
    
    def test_connection(self) -> Tuple[bool, str]:
        """연결 테스트"""
        try:
            # 서버 시간 조회 (공개 API)
            self.exchange.fetch_time()
            
            # API 키가 있으면 잔고 조회로 인증 테스트
            if self.exchange.apiKey and self.exchange.secret:
                self.exchange.fetch_balance()
                return True, f"{self.exchange_info.get('name', self.exchange_id)} 연동 성공"
            else:
                return True, f"{self.exchange_info.get('name', self.exchange_id)} 서버 연결 성공 (API 키 없음)"
                
        except ccxt.AuthenticationError as e:
            return False, f"API 인증 실패: {str(e)}"
        except ccxt.NetworkError as e:
            return False, f"네트워크 오류: {str(e)}"
        except Exception as e:
            return False, f"연결 테스트 실패: {str(e)}"
    
    # ========== 계정 관련 ==========
    
    def get_balance(self) -> Optional[Dict]:
        """잔고 조회"""
        try:
            self._wait_for_rate_limit()
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            logger.error("CCXT", f"잔고 조회 실패: {str(e)}")
            return None
    
    def get_usdt_balance(self) -> float:
        """USDT 잔고 조회"""
        try:
            balance = self.get_balance()
            if balance:
                usdt = balance.get('USDT', {})
                return float(usdt.get('free', 0))
            return 0.0
        except Exception as e:
            logger.error("CCXT", f"USDT 잔고 조회 실패: {str(e)}")
            return 0.0
    
    # ========== 시장 데이터 ==========
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """현재가 조회"""
        try:
            self._wait_for_rate_limit()
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': ticker['symbol'],
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['baseVolume'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.error("CCXT", f"현재가 조회 실패 ({symbol}): {str(e)}")
            return None
    
    def get_candles(self, symbol: str, timeframe: str = "1h", 
                   since: int = None, limit: int = 100) -> Optional[List[Dict]]:
        """
        캔들 데이터 조회
        
        Args:
            symbol: 심볼 (예: BTC/USDT:USDT)
            timeframe: 타임프레임 (1m, 5m, 15m, 1h, 4h, 1d)
            since: 시작 타임스탬프 (ms)
            limit: 최대 개수 (기본 100, 최대 거래소마다 다름)
        
        Returns:
            캔들 데이터 리스트 [{'timestamp', 'open', 'high', 'low', 'close', 'volume'}, ...]
        """
        try:
            self._wait_for_rate_limit()
            
            # CCXT 타임프레임 변환
            ccxt_timeframe = TIMEFRAMES.get(timeframe, timeframe)
            
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=ccxt_timeframe,
                since=since,
                limit=limit
            )
            
            if not ohlcv:
                return []
            
            candles = []
            for candle in ohlcv:
                ts_ms = candle[0]
                dt_kst = time_helper.timestamp_to_kst(ts_ms)
                
                candles.append({
                    'timestamp': time_helper.format_kst(dt_kst),
                    'timestamp_ms': ts_ms,
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[5])
                })
            
            return candles
            
        except Exception as e:
            logger.error("CCXT", f"캔들 조회 실패 ({symbol} {timeframe}): {str(e)}")
            return None
    
    def get_candles_since(self, symbol: str, timeframe: str, 
                         start_time: datetime) -> List[Dict]:
        """
        특정 시간 이후의 모든 캔들 조회 (페이지네이션)
        
        Args:
            symbol: 심볼
            timeframe: 타임프레임
            start_time: 시작 시간 (KST datetime)
        
        Returns:
            모든 캔들 데이터 리스트
        """
        all_candles = []
        since_ms = time_helper.kst_to_timestamp(start_time)
        
        while True:
            candles = self.get_candles(symbol, timeframe, since=since_ms, limit=1000)
            
            if not candles:
                break
            
            all_candles.extend(candles)
            
            # 다음 페이지
            if len(candles) < 1000:
                break
            
            # 마지막 캔들 시간 + 1ms
            since_ms = candles[-1]['timestamp_ms'] + 1
            
            # Rate limit
            time.sleep(0.1)
        
        return all_candles
    
    def get_markets(self) -> List[Dict]:
        """거래 가능한 마켓 목록 조회"""
        try:
            self._wait_for_rate_limit()
            self.exchange.load_markets()
            
            markets = []
            for symbol, market in self.exchange.markets.items():
                # 선물(swap) 마켓만 필터링
                if market.get('swap') or market.get('future'):
                    markets.append({
                        'symbol': symbol,
                        'base': market.get('base'),
                        'quote': market.get('quote'),
                        'active': market.get('active', True),
                        'type': market.get('type'),
                        'contract': market.get('contract', True)
                    })
            
            return markets
            
        except Exception as e:
            logger.error("CCXT", f"마켓 조회 실패: {str(e)}")
            return []
    
    # ========== 포지션 관련 ==========
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """포지션 조회"""
        try:
            self._wait_for_rate_limit()
            
            if symbol:
                positions = self.exchange.fetch_positions([symbol])
            else:
                positions = self.exchange.fetch_positions()
            
            result = []
            for pos in positions:
                size = abs(float(pos.get('contracts', 0) or pos.get('contractSize', 0) or 0))
                if size > 0 or pos.get('entryPrice'):
                    result.append({
                        'symbol': pos['symbol'],
                        'side': pos.get('side', 'long'),
                        'size': size,
                        'entry_price': float(pos.get('entryPrice', 0) or 0),
                        'mark_price': float(pos.get('markPrice', 0) or 0),
                        'liquidation_price': float(pos.get('liquidationPrice', 0) or 0),
                        'unrealized_pnl': float(pos.get('unrealizedPnl', 0) or 0),
                        'leverage': int(pos.get('leverage', 1) or 1),
                        'margin_mode': pos.get('marginMode', 'isolated'),
                    })
            
            return result
            
        except Exception as e:
            logger.error("CCXT", f"포지션 조회 실패: {str(e)}")
            return []
    
    def set_leverage(self, symbol: str, leverage: int, 
                    margin_mode: str = 'isolated') -> bool:
        """레버리지 설정"""
        try:
            self._wait_for_rate_limit()
            
            # 마진 모드 설정 (일부 거래소)
            try:
                self.exchange.set_margin_mode(margin_mode, symbol)
            except:
                pass  # 지원하지 않는 거래소는 무시
            
            # 레버리지 설정
            self.exchange.set_leverage(leverage, symbol)
            logger.info("CCXT", f"{symbol} 레버리지 {leverage}x 설정 완료")
            return True
            
        except Exception as e:
            logger.error("CCXT", f"레버리지 설정 실패: {str(e)}")
            return False
    
    # ========== 주문 관련 ==========
    
    def place_market_order(self, symbol: str, side: str, size: float, 
                          pos_side: str = None, reduce_only: bool = False,
                          params: dict = None) -> Optional[Dict]:
        """
        시장가 주문
        
        Args:
            symbol: 심볼
            side: 'buy' 또는 'sell'
            size: 수량
            pos_side: 포지션 방향 ('long', 'short') - 헤지 모드용
            reduce_only: 청산 전용 여부
            params: 추가 파라미터 (TP/SL 등)
        
        Returns:
            주문 결과
        """
        try:
            self._wait_for_rate_limit()
            
            order_params = params or {}
            
            if pos_side:
                order_params['posSide'] = pos_side
            if reduce_only:
                order_params['reduceOnly'] = True
            
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=size,
                params=order_params
            )
            
            logger.info("CCXT", f"시장가 주문 완료: {symbol} {side} {size}")
            
            # 안전한 float 변환
            avg_price = order.get('average') or order.get('price') or 0
            filled_amount = order.get('filled') or 0
            
            return {
                'order_id': order.get('id', ''),
                'symbol': order.get('symbol', symbol),
                'side': order.get('side', side),
                'type': order.get('type', 'market'),
                'size': float(order.get('amount') or size),
                'filled': float(filled_amount),
                'price': float(avg_price),
                'status': order.get('status', 'unknown'),
                'timestamp': order.get('timestamp', 0)
            }
            
        except Exception as e:
            logger.error("CCXT", f"시장가 주문 실패: {str(e)}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, size: float, 
                         price: float, pos_side: str = None, 
                         reduce_only: bool = False,
                         params: dict = None) -> Optional[Dict]:
        """
        지정가 주문
        
        Args:
            symbol: 심볼
            side: 'buy' 또는 'sell'
            size: 수량
            price: 가격
            pos_side: 포지션 방향 ('long', 'short')
            reduce_only: 청산 전용 여부
            params: 추가 파라미터
        
        Returns:
            주문 결과
        """
        try:
            self._wait_for_rate_limit()
            
            order_params = params or {}
            
            if pos_side:
                order_params['posSide'] = pos_side
            if reduce_only:
                order_params['reduceOnly'] = True
            
            order = self.exchange.create_limit_order(
                symbol=symbol,
                side=side,
                amount=size,
                price=price,
                params=order_params
            )
            
            logger.info("CCXT", f"지정가 주문 완료: {symbol} {side} {size} @ {price}")
            
            filled_amount = order.get('filled') or 0
            
            return {
                'order_id': order.get('id', ''),
                'symbol': order.get('symbol', symbol),
                'side': order.get('side', side),
                'type': order.get('type', 'limit'),
                'size': float(order.get('amount') or size),
                'price': float(order.get('price') or price),
                'filled': float(filled_amount),
                'status': order.get('status', 'unknown'),
                'timestamp': order.get('timestamp', 0)
            }
            
        except Exception as e:
            logger.error("CCXT", f"지정가 주문 실패: {str(e)}")
            return None
    
    def place_order_with_tp_sl(self, symbol: str, side: str, size: float,
                               tp_price: float = None, sl_price: float = None,
                               pos_side: str = None) -> Optional[Dict]:
        """
        시장가 주문 + TP/SL 설정
        
        거래소마다 TP/SL 설정 방식이 다르므로 별도 처리
        """
        try:
            order_params = {}
            
            if pos_side:
                order_params['posSide'] = pos_side
            
            # 거래소별 TP/SL 파라미터 설정
            if self.exchange_id == 'binance':
                # Binance는 별도 주문 필요
                pass
            elif self.exchange_id == 'bybit':
                if tp_price:
                    order_params['takeProfit'] = {
                        'triggerPrice': tp_price,
                        'type': 'market'
                    }
                if sl_price:
                    order_params['stopLoss'] = {
                        'triggerPrice': sl_price,
                        'type': 'market'
                    }
            elif self.exchange_id == 'okx':
                attach_algo = {}
                if tp_price:
                    attach_algo['tpTriggerPx'] = str(tp_price)
                    attach_algo['tpOrdPx'] = '-1'  # 시장가
                if sl_price:
                    attach_algo['slTriggerPx'] = str(sl_price)
                    attach_algo['slOrdPx'] = '-1'
                if attach_algo:
                    order_params['attachAlgoOrds'] = [attach_algo]
            
            # 시장가 주문 실행
            result = self.place_market_order(
                symbol=symbol,
                side=side,
                size=size,
                pos_side=pos_side,
                params=order_params
            )
            
            # Binance는 TP/SL 별도 주문
            if result and self.exchange_id == 'binance':
                if tp_price:
                    self._place_binance_tp_sl(symbol, 'tp', tp_price, size, pos_side)
                if sl_price:
                    self._place_binance_tp_sl(symbol, 'sl', sl_price, size, pos_side)
            
            return result
            
        except Exception as e:
            logger.error("CCXT", f"TP/SL 주문 실패: {str(e)}")
            return None
    
    def _place_binance_tp_sl(self, symbol: str, order_type: str, 
                             price: float, size: float, pos_side: str):
        """Binance TP/SL 주문 (별도 주문)"""
        try:
            side = 'sell' if pos_side == 'long' else 'buy'
            
            params = {
                'stopPrice': price,
                'reduceOnly': True
            }
            
            if pos_side:
                params['positionSide'] = pos_side.upper()
            
            if order_type == 'tp':
                params['type'] = 'TAKE_PROFIT_MARKET'
            else:
                params['type'] = 'STOP_MARKET'
            
            self.exchange.create_order(
                symbol=symbol,
                type='market',
                side=side,
                amount=size,
                params=params
            )
            
        except Exception as e:
            logger.error("CCXT", f"Binance TP/SL 주문 실패: {str(e)}")
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """주문 취소"""
        try:
            self._wait_for_rate_limit()
            self.exchange.cancel_order(order_id, symbol)
            logger.info("CCXT", f"주문 취소 완료: {order_id}")
            return True
        except Exception as e:
            logger.error("CCXT", f"주문 취소 실패: {str(e)}")
            return False
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """모든 주문 취소"""
        try:
            self._wait_for_rate_limit()
            self.exchange.cancel_all_orders(symbol)
            logger.info("CCXT", f"모든 주문 취소 완료: {symbol}")
            return True
        except Exception as e:
            logger.error("CCXT", f"주문 전체 취소 실패: {str(e)}")
            return False
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """미체결 주문 조회"""
        try:
            self._wait_for_rate_limit()
            
            if symbol:
                orders = self.exchange.fetch_open_orders(symbol)
            else:
                orders = self.exchange.fetch_open_orders()
            
            return [{
                'order_id': o['id'],
                'symbol': o['symbol'],
                'side': o['side'],
                'type': o['type'],
                'size': float(o.get('amount', 0)),
                'price': float(o.get('price', 0) or 0),
                'filled': float(o.get('filled', 0)),
                'status': o['status'],
                'timestamp': o.get('timestamp')
            } for o in orders]
            
        except Exception as e:
            logger.error("CCXT", f"미체결 주문 조회 실패: {str(e)}")
            return []
    
    def get_order(self, symbol: str, order_id: str) -> Optional[Dict]:
        """주문 상세 조회"""
        try:
            self._wait_for_rate_limit()
            order = self.exchange.fetch_order(order_id, symbol)
            
            return {
                'order_id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'size': float(order.get('amount', 0)),
                'price': float(order.get('price', 0) or 0),
                'average': float(order.get('average', 0) or 0),
                'filled': float(order.get('filled', 0)),
                'status': order['status'],
                'timestamp': order.get('timestamp')
            }
            
        except Exception as e:
            logger.error("CCXT", f"주문 조회 실패: {str(e)}")
            return None
    
    # ========== 유틸리티 ==========
    
    def get_min_order_size(self, symbol: str) -> float:
        """최소 주문 수량 조회"""
        try:
            self.exchange.load_markets()
            market = self.exchange.market(symbol)
            return float(market.get('limits', {}).get('amount', {}).get('min', 0.001))
        except:
            return 0.001
    
    def get_price_precision(self, symbol: str) -> int:
        """가격 소수점 자릿수 조회"""
        try:
            self.exchange.load_markets()
            market = self.exchange.market(symbol)
            return int(market.get('precision', {}).get('price', 2))
        except:
            return 2
    
    def get_amount_precision(self, symbol: str) -> int:
        """수량 소수점 자릿수 조회"""
        try:
            self.exchange.load_markets()
            market = self.exchange.market(symbol)
            return int(market.get('precision', {}).get('amount', 3))
        except:
            return 3
    
    def calculate_order_size(self, symbol: str, margin: float, 
                            leverage: int, price: float) -> float:
        """
        주문 수량 계산
        
        Args:
            symbol: 심볼
            margin: 증거금 (USDT)
            leverage: 레버리지
            price: 현재가
        
        Returns:
            주문 수량
        """
        raw_size = (margin * leverage) / price
        
        # 소수점 자릿수 조정
        precision = self.get_amount_precision(symbol)
        size = round(raw_size, precision)
        
        # 최소 수량 체크
        min_size = self.get_min_order_size(symbol)
        return max(size, min_size)
    
    def get_maker_fee(self) -> float:
        """메이커 수수료"""
        return get_exchange_fee(self.exchange_id, 'maker')
    
    def get_taker_fee(self) -> float:
        """테이커 수수료"""
        return get_exchange_fee(self.exchange_id, 'taker')
    
    # ========== 계정 설정 ==========
    
    def get_account_config(self) -> Optional[Dict]:
        """
        계정 설정 조회 (포지션 모드, 마진 모드 등)
        
        Returns:
            {acct_lv, pos_mode, ...} 또는 None
        """
        try:
            self._wait_for_rate_limit()
            
            # 거래소별 설정 조회
            if self.exchange_id == 'okx':
                # OKX 전용 API
                config = self.exchange.private_get_account_config()
                data = config.get('data', [{}])[0] if config.get('data') else {}
                return {
                    'acct_lv': data.get('acctLv', '1'),
                    'pos_mode': data.get('posMode', 'net_mode'),
                    'greeks_type': data.get('greeksType', ''),
                }
            elif self.exchange_id == 'binance':
                # Binance
                try:
                    pos_mode = self.exchange.fapiPrivateGetPositionSideDual()
                    return {
                        'pos_mode': 'long_short_mode' if pos_mode.get('dualSidePosition') else 'net_mode',
                        'acct_lv': '2'  # Binance는 선물 계정
                    }
                except:
                    return {'pos_mode': 'unknown', 'acct_lv': 'unknown'}
            elif self.exchange_id == 'bybit':
                # Bybit
                try:
                    config = self.exchange.private_get_v5_account_info()
                    data = config.get('result', {})
                    return {
                        'pos_mode': data.get('unifiedMarginStatus', 'unknown'),
                        'acct_lv': data.get('marginMode', 'unknown')
                    }
                except:
                    return {'pos_mode': 'unknown', 'acct_lv': 'unknown'}
            else:
                # 기타 거래소
                return {
                    'pos_mode': 'unknown',
                    'acct_lv': 'unknown'
                }
                
        except Exception as e:
            logger.error("CCXT", f"계정 설정 조회 실패: {str(e)}")
            return None
    
    def set_hedge_mode(self) -> bool:
        """
        헤지 모드 설정 (롱/숏 동시 보유)
        
        Returns:
            성공 여부
        """
        try:
            self._wait_for_rate_limit()
            
            if self.exchange_id == 'okx':
                # OKX
                self.exchange.private_post_account_set_position_mode({
                    'posMode': 'long_short_mode'
                })
            elif self.exchange_id == 'binance':
                # Binance
                self.exchange.fapiPrivatePostPositionSideDual({
                    'dualSidePosition': 'true'
                })
            elif self.exchange_id == 'bybit':
                # Bybit (기본이 헤지 모드)
                pass
            elif self.exchange_id == 'bitget':
                # Bitget
                self.exchange.private_post_api_mix_v1_account_setpositionmode({
                    'positionMode': 'hedge_mode'
                })
            
            logger.info("CCXT", f"{self.exchange_id} 헤지 모드 설정 완료")
            return True
            
        except Exception as e:
            logger.error("CCXT", f"헤지 모드 설정 실패: {str(e)}")
            return False

