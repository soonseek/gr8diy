"""
OKX WebSocket 클라이언트
"""
import json
import time
import hmac
import base64
import asyncio
import websockets
from typing import Callable, List, Optional
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QThread

from config.settings import OKX_WS_PUBLIC, OKX_WS_PRIVATE
from utils.logger import logger


class OKXWebSocketWorker(QObject):
    """OKX WebSocket 워커 (QThread에서 실행)"""
    
    # Signals
    connected = Signal()
    disconnected = Signal()
    message_received = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, api_key: str = "", secret: str = "", passphrase: str = ""):
        super().__init__()
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        
        self.ws = None
        self.is_running = False
        self.subscriptions = []
        self.reconnect_delay = 1
        self.max_reconnect_delay = 60
    
    def _generate_signature(self, timestamp: str, method: str, request_path: str) -> str:
        """WebSocket 인증 서명 생성"""
        message = timestamp + method + request_path
        mac = hmac.new(
            self.secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')
    
    async def _authenticate(self):
        """WebSocket 인증"""
        timestamp = str(int(time.time()))
        sign = self._generate_signature(timestamp, "GET", "/users/self/verify")
        
        auth_msg = {
            "op": "login",
            "args": [{
                "apiKey": self.api_key,
                "passphrase": self.passphrase,
                "timestamp": timestamp,
                "sign": sign
            }]
        }
        
        await self.ws.send(json.dumps(auth_msg))
        logger.info("OKX_WS", "인증 요청 전송")
    
    async def _subscribe(self, channels: List[dict]):
        """채널 구독"""
        sub_msg = {
            "op": "subscribe",
            "args": channels
        }
        await self.ws.send(json.dumps(sub_msg))
        logger.info("OKX_WS", f"구독 요청: {channels}")
    
    async def _handle_message(self, message: str):
        """메시지 처리"""
        try:
            data = json.loads(message)
            
            # 로그인 응답
            if data.get("event") == "login":
                if data.get("code") == "0":
                    logger.info("OKX_WS", "인증 성공")
                    # 구독 요청
                    if self.subscriptions:
                        await self._subscribe(self.subscriptions)
                else:
                    logger.error("OKX_WS", f"인증 실패: {data.get('msg')}")
                    self.error_occurred.emit(f"인증 실패: {data.get('msg')}")
            
            # 구독 응답
            elif data.get("event") == "subscribe":
                logger.info("OKX_WS", f"구독 성공: {data.get('arg')}")
            
            # 데이터 메시지
            elif data.get("data"):
                self.message_received.emit(data)
            
            # 에러
            elif data.get("event") == "error":
                logger.error("OKX_WS", f"WebSocket 오류: {data.get('msg')}")
                self.error_occurred.emit(data.get('msg'))
            
        except json.JSONDecodeError as e:
            logger.error("OKX_WS", f"JSON 파싱 오류: {str(e)}")
        except Exception as e:
            logger.error("OKX_WS", f"메시지 처리 오류: {str(e)}")
    
    async def _connect_and_run(self, use_private: bool = False):
        """WebSocket 연결 및 실행"""
        uri = OKX_WS_PRIVATE if use_private else OKX_WS_PUBLIC
        
        try:
            async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as ws:
                self.ws = ws
                logger.info("OKX_WS", "WebSocket 연결 성공")
                self.connected.emit()
                self.reconnect_delay = 1  # 연결 성공 시 재연결 딜레이 리셋
                
                # Private 채널이면 인증
                if use_private and self.api_key:
                    await self._authenticate()
                else:
                    # Public 채널은 바로 구독
                    if self.subscriptions:
                        await self._subscribe(self.subscriptions)
                
                # 메시지 수신 루프
                async for message in ws:
                    if not self.is_running:
                        break
                    await self._handle_message(message)
                    
        except websockets.exceptions.WebSocketException as e:
            logger.error("OKX_WS", f"WebSocket 오류: {str(e)}")
            self.error_occurred.emit(str(e))
        except Exception as e:
            logger.error("OKX_WS", f"연결 오류: {str(e)}")
            self.error_occurred.emit(str(e))
        finally:
            self.ws = None
            self.disconnected.emit()
    
    async def _run_with_reconnect(self, use_private: bool = False):
        """재연결 로직 포함 실행"""
        while self.is_running:
            try:
                await self._connect_and_run(use_private)
            except Exception as e:
                logger.error("OKX_WS", f"실행 오류: {str(e)}")
            
            if self.is_running:
                # 재연결 대기
                logger.info("OKX_WS", f"{self.reconnect_delay}초 후 재연결 시도...")
                await asyncio.sleep(self.reconnect_delay)
                # 지수 백오프
                self.reconnect_delay = min(
                    self.reconnect_delay * 2, 
                    self.max_reconnect_delay
                )
    
    def run(self, subscriptions: List[dict], use_private: bool = False):
        """워커 실행 (스레드에서 호출됨)"""
        self.is_running = True
        self.subscriptions = subscriptions
        
        # 이벤트 루프 생성 및 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._run_with_reconnect(use_private))
        finally:
            loop.close()
    
    def stop(self):
        """워커 중지"""
        self.is_running = False
        if self.ws:
            asyncio.create_task(self.ws.close())


class OKXWebSocketClient(QObject):
    """OKX WebSocket 클라이언트 (메인 클래스)"""
    
    # Signals
    connected = Signal()
    disconnected = Signal()
    position_updated = Signal(dict)
    price_updated = Signal(str, float)  # symbol, price
    order_updated = Signal(dict)
    
    def __init__(self, api_key: str = "", secret: str = "", passphrase: str = ""):
        super().__init__()
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        
        self.worker = None
        self.thread = None
    
    def start(self, symbols: List[str]):
        """WebSocket 시작"""
        if self.thread and self.thread.isRunning():
            logger.warning("OKX_WS", "이미 실행 중입니다")
            return
        
        # 구독 채널 설정
        subscriptions = []
        
        # 가격 채널 (Public)
        for symbol in symbols:
            subscriptions.append({
                "channel": "tickers",
                "instId": symbol
            })
        
        # 포지션 및 주문 채널 (Private)
        if self.api_key:
            subscriptions.extend([
                {"channel": "positions", "instType": "SWAP"},
                {"channel": "orders", "instType": "SWAP"}
            ])
        
        # 워커 및 스레드 생성
        self.worker = OKXWebSocketWorker(self.api_key, self.secret, self.passphrase)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        # Signal 연결
        self.worker.connected.connect(self._on_connected)
        self.worker.disconnected.connect(self._on_disconnected)
        self.worker.message_received.connect(self._on_message)
        self.worker.error_occurred.connect(self._on_error)
        
        # 스레드 시작
        self.thread.started.connect(
            lambda: self.worker.run(subscriptions, use_private=bool(self.api_key))
        )
        self.thread.start()
        
        logger.info("OKX_WS", "WebSocket 클라이언트 시작")
    
    def stop(self):
        """WebSocket 중지"""
        if self.worker:
            self.worker.stop()
        
        if self.thread:
            self.thread.quit()
            self.thread.wait(5000)
        
        logger.info("OKX_WS", "WebSocket 클라이언트 중지")
    
    def _on_connected(self):
        """연결 시"""
        logger.info("OKX_WS", "연결됨")
        self.connected.emit()
    
    def _on_disconnected(self):
        """연결 해제 시"""
        logger.info("OKX_WS", "연결 해제됨")
        self.disconnected.emit()
    
    def _on_message(self, data: dict):
        """메시지 수신 시"""
        try:
            channel = data.get("arg", {}).get("channel")
            
            if channel == "tickers":
                # 가격 업데이트
                for item in data.get("data", []):
                    symbol = item.get("instId")
                    price = float(item.get("last", 0))
                    self.price_updated.emit(symbol, price)
            
            elif channel == "positions":
                # 포지션 업데이트
                for item in data.get("data", []):
                    self.position_updated.emit(item)
            
            elif channel == "orders":
                # 주문 업데이트
                for item in data.get("data", []):
                    self.order_updated.emit(item)
                    
        except Exception as e:
            logger.error("OKX_WS", f"메시지 처리 오류: {str(e)}")
    
    def _on_error(self, error: str):
        """오류 시"""
        logger.error("OKX_WS", f"오류: {error}")


