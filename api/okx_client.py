"""
OKX REST API 클라이언트
"""
import time
import hmac
import base64
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import (
    OKX_API_BASE, OKX_RATE_LIMIT_PER_SECOND, 
    OKX_RATE_LIMIT_COOLDOWN
)
from utils.logger import logger


class OKXClient:
    """OKX REST API 클라이언트"""
    
    def __init__(self, api_key: str = "", secret: str = "", passphrase: str = ""):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.base_url = OKX_API_BASE
        
        # Rate Limiting
        self.rate_limit_per_second = OKX_RATE_LIMIT_PER_SECOND
        self.request_timestamps = []
        self.cooldown_until = 0
        
        # HTTP Session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _wait_for_rate_limit(self):
        """Rate Limit 대기"""
        current_time = time.time()
        
        # Cooldown 체크
        if current_time < self.cooldown_until:
            wait_time = self.cooldown_until - current_time
            logger.warning("OKX", f"Rate limit cooldown 중... {wait_time:.1f}초 대기")
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
    
    def _generate_signature(self, timestamp: str, method: str, 
                          request_path: str, body: str = "") -> str:
        """API 서명 생성"""
        message = timestamp + method + request_path + body
        mac = hmac.new(
            self.secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')
    
    def _get_headers(self, method: str, request_path: str, body: str = "") -> Dict:
        """요청 헤더 생성"""
        timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
        signature = self._generate_signature(timestamp, method, request_path, body)
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, 
                params: Dict = None, data: Dict = None) -> Optional[Dict]:
        """HTTP 요청"""
        self._wait_for_rate_limit()
        
        url = self.base_url + endpoint
        request_path = endpoint
        
        body = ""
        if data:
            body = json.dumps(data)
        
        headers = self._get_headers(method, request_path, body)
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=data, timeout=10)
            else:
                response = self.session.request(method, url, headers=headers, 
                                              params=params, json=data, timeout=10)
            
            # 429 Rate Limit 처리
            if response.status_code == 429:
                logger.error("OKX", "Rate limit 초과 (429)")
                self.cooldown_until = time.time() + OKX_RATE_LIMIT_COOLDOWN
                return None
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') != '0':
                logger.error("OKX", f"API 오류: {result.get('msg')} (code: {result.get('code')})")
                return None
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error("OKX", f"요청 실패: {str(e)}")
            return None
    
    def get(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """GET 요청"""
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """POST 요청"""
        return self._request("POST", endpoint, data=data)
    
    # ========== 계정 관련 ==========
    
    def get_account_config(self) -> Optional[Dict]:
        """계정 설정 조회"""
        result = self.get("/api/v5/account/config")
        if result and result.get('data'):
            return result['data'][0]
        return None
    
    def set_account_mode(self, acct_lv: int = 4) -> bool:
        """
        계정 모드 설정
        acct_lv: 1=간단, 2=단일통화마진, 3=다중통화마진, 4=포트폴리오마진
        """
        data = {"acctLv": acct_lv}
        result = self.post("/api/v5/account/set-account-level", data)
        return result is not None
    
    def set_position_mode(self, pos_mode: str = "long_short_mode") -> bool:
        """
        포지션 모드 설정
        pos_mode: long_short_mode (헤지모드), net_mode (단방향모드)
        """
        data = {"posMode": pos_mode}
        result = self.post("/api/v5/account/set-position-mode", data)
        return result is not None
    
    def get_balance(self) -> Optional[List[Dict]]:
        """잔고 조회"""
        result = self.get("/api/v5/account/balance")
        if result and result.get('data'):
            return result['data'][0].get('details', [])
        return None
    
    # ========== 시장 데이터 ==========
    
    def get_candles(self, inst_id: str, bar: str = "1m", 
                   after: str = None, before: str = None,
                   limit: int = 100) -> Optional[List]:
        """
        캔들 데이터 조회
        inst_id: BTC-USDT-SWAP 등
        bar: 1m, 5m, 15m, 1H, 4H, 1D 등
        after: 이 timestamp 이후 데이터 (pagination)
        before: 이 timestamp 이전 데이터
        limit: 최대 100
        """
        params = {
            "instId": inst_id,
            "bar": bar,
            "limit": limit
        }
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        
        result = self.get("/api/v5/market/candles", params)
        if result and result.get('data'):
            return result['data']
        return None
    
    def get_ticker(self, inst_id: str) -> Optional[Dict]:
        """현재가 조회"""
        params = {"instId": inst_id}
        result = self.get("/api/v5/market/ticker", params)
        if result and result.get('data'):
            return result['data'][0]
        return None
    
    # ========== 거래 ==========
    
    def set_leverage(self, inst_id: str, lever: int, 
                    mgn_mode: str = "isolated", pos_side: str = "long") -> bool:
        """
        레버리지 설정
        mgn_mode: isolated (격리), cross (교차)
        pos_side: long, short (hedge 모드에서)
        """
        data = {
            "instId": inst_id,
            "lever": str(lever),
            "mgnMode": mgn_mode,
            "posSide": pos_side
        }
        result = self.post("/api/v5/account/set-leverage", data)
        return result is not None
    
    def place_order(self, inst_id: str, side: str, ord_type: str,
                   sz: float, px: float = None, pos_side: str = None,
                   td_mode: str = "isolated", reduce_only: bool = False,
                   tp_trigger_px: str = None, tp_ord_px: str = None,
                   sl_trigger_px: str = None, sl_ord_px: str = None,
                   cl_ord_id: str = None) -> Optional[Dict]:
        """
        주문 생성
        side: buy, sell
        ord_type: market, limit, post_only 등
        sz: 수량
        px: 가격 (limit 주문 시)
        pos_side: long, short (hedge 모드에서)
        td_mode: isolated, cross
        """
        data = {
            "instId": inst_id,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": str(sz)
        }
        
        if px:
            data["px"] = str(px)
        if pos_side:
            data["posSide"] = pos_side
        if reduce_only:
            data["reduceOnly"] = "true"
        if tp_trigger_px:
            data["tpTriggerPx"] = str(tp_trigger_px)
            data["tpOrdPx"] = str(tp_ord_px) if tp_ord_px else "-1"
        if sl_trigger_px:
            data["slTriggerPx"] = str(sl_trigger_px)
            data["slOrdPx"] = str(sl_ord_px) if sl_ord_px else "-1"
        if cl_ord_id:
            data["clOrdId"] = cl_ord_id
        
        result = self.post("/api/v5/trade/order", data)
        if result and result.get('data'):
            return result['data'][0]
        return None
    
    def cancel_order(self, inst_id: str, ord_id: str = None, 
                    cl_ord_id: str = None) -> bool:
        """주문 취소"""
        data = {"instId": inst_id}
        if ord_id:
            data["ordId"] = ord_id
        if cl_ord_id:
            data["clOrdId"] = cl_ord_id
        
        result = self.post("/api/v5/trade/cancel-order", data)
        return result is not None
    
    def get_order(self, inst_id: str, ord_id: str = None,
                 cl_ord_id: str = None) -> Optional[Dict]:
        """주문 조회"""
        params = {"instId": inst_id}
        if ord_id:
            params["ordId"] = ord_id
        if cl_ord_id:
            params["clOrdId"] = cl_ord_id
        
        result = self.get("/api/v5/trade/order", params)
        if result and result.get('data'):
            return result['data'][0]
        return None
    
    def get_open_orders(self, inst_id: str = None) -> Optional[List[Dict]]:
        """미체결 주문 조회"""
        params = {}
        if inst_id:
            params["instId"] = inst_id
        
        result = self.get("/api/v5/trade/orders-pending", params)
        if result and result.get('data'):
            return result['data']
        return []
    
    def get_positions(self, inst_id: str = None) -> Optional[List[Dict]]:
        """포지션 조회"""
        params = {}
        if inst_id:
            params["instId"] = inst_id
        
        result = self.get("/api/v5/account/positions", params)
        if result and result.get('data'):
            return result['data']
        return []
    
    # ========== 연동 테스트 ==========
    
    def test_connection(self) -> tuple[bool, str]:
        """연결 테스트"""
        try:
            # 공개 API로 먼저 테스트
            result = self.get("/api/v5/public/time")
            if not result:
                return False, "OKX 서버 연결 실패"
            
            # 인증 필요한 API 테스트
            if self.api_key and self.secret and self.passphrase:
                balance = self.get_balance()
                if balance is None:
                    return False, "API 인증 실패 (키/시크릿/패스프레이즈 확인)"
                return True, "OKX 연동 성공"
            else:
                return False, "API 자격증명이 설정되지 않았습니다"
                
        except Exception as e:
            return False, f"연결 테스트 실패: {str(e)}"


