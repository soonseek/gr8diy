"""
거래소 팩토리
거래소 인스턴스 생성 및 관리
"""
from typing import Dict, Optional, List
from api.ccxt_client import CCXTClient
from database.repository import ExchangeCredentialsRepository, ExchangesRepository
from config.exchanges import SUPPORTED_EXCHANGES, DEFAULT_ENABLED_EXCHANGES
from utils.logger import logger
from utils.crypto import CredentialManager
from config.settings import CREDENTIALS_PATH


class ExchangeFactory:
    """거래소 팩토리 (싱글톤)"""
    
    _instance = None
    _clients: Dict[str, CCXTClient] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.exchanges_repo = ExchangesRepository()
        self.credentials_repo = ExchangeCredentialsRepository()
        self.credential_manager = CredentialManager(CREDENTIALS_PATH)
        self._clients = {}
        self._initialized = True
        
        # 거래소 메타데이터 초기화
        self._init_exchanges()
    
    def _init_exchanges(self):
        """거래소 메타데이터 DB 초기화"""
        try:
            self.exchanges_repo.init_from_config(SUPPORTED_EXCHANGES)
            logger.info("ExchangeFactory", f"{len(SUPPORTED_EXCHANGES)}개 거래소 메타데이터 초기화 완료")
        except Exception as e:
            logger.error("ExchangeFactory", f"거래소 초기화 실패: {str(e)}")
    
    def get_client(self, exchange_id: str, is_testnet: bool = False, 
                  force_new: bool = False) -> Optional[CCXTClient]:
        """
        거래소 클라이언트 조회 또는 생성
        
        Args:
            exchange_id: 거래소 ID
            is_testnet: 테스트넷 여부
            force_new: 새 인스턴스 강제 생성
        
        Returns:
            CCXTClient 인스턴스 또는 None
        """
        cache_key = f"{exchange_id}_{'testnet' if is_testnet else 'mainnet'}"
        
        # 캐시된 클라이언트 반환
        if not force_new and cache_key in self._clients:
            return self._clients[cache_key]
        
        # 자격증명 조회
        creds = self._get_credentials(exchange_id, is_testnet)
        if not creds:
            logger.warning("ExchangeFactory", f"{exchange_id} 자격증명 없음")
            return None
        
        try:
            # 클라이언트 생성
            client = CCXTClient(
                exchange_id=exchange_id,
                api_key=creds.get('api_key', ''),
                secret=creds.get('secret', ''),
                passphrase=creds.get('passphrase', ''),
                is_testnet=is_testnet
            )
            
            # 캐시에 저장
            self._clients[cache_key] = client
            
            return client
            
        except Exception as e:
            logger.error("ExchangeFactory", f"{exchange_id} 클라이언트 생성 실패: {str(e)}")
            return None
    
    def get_client_without_auth(self, exchange_id: str, 
                                is_testnet: bool = False) -> Optional[CCXTClient]:
        """
        인증 없이 클라이언트 생성 (공개 API용)
        
        데이터 수집 등 인증이 필요 없는 작업에 사용
        """
        cache_key = f"{exchange_id}_public_{'testnet' if is_testnet else 'mainnet'}"
        
        if cache_key in self._clients:
            return self._clients[cache_key]
        
        try:
            client = CCXTClient(
                exchange_id=exchange_id,
                api_key='',
                secret='',
                passphrase='',
                is_testnet=is_testnet
            )
            
            self._clients[cache_key] = client
            return client
            
        except Exception as e:
            logger.error("ExchangeFactory", f"{exchange_id} 공개 클라이언트 생성 실패: {str(e)}")
            return None
    
    def _get_credentials(self, exchange_id: str, is_testnet: bool) -> Optional[Dict]:
        """자격증명 조회"""
        # DB에서 조회
        creds = self.credentials_repo.get_credentials(exchange_id, is_testnet)
        if creds and creds.get('api_key'):
            return {
                'api_key': creds['api_key'],
                'secret': creds['secret'],
                'passphrase': creds.get('passphrase', '')
            }
        
        # 레거시: OKX 자격증명 (기존 암호화 파일에서)
        if exchange_id == 'okx' and not is_testnet:
            try:
                okx_creds = self.credential_manager.get_okx_credentials()
                if all(okx_creds.values()):
                    return okx_creds
            except:
                pass
        
        return None
    
    def save_credentials(self, exchange_id: str, api_key: str, secret: str,
                        passphrase: str = None, is_testnet: bool = False) -> bool:
        """자격증명 저장"""
        try:
            self.credentials_repo.upsert_credentials(
                exchange_id=exchange_id,
                api_key=api_key,
                secret=secret,
                passphrase=passphrase,
                is_testnet=is_testnet
            )
            
            # 캐시 무효화
            cache_key = f"{exchange_id}_{'testnet' if is_testnet else 'mainnet'}"
            if cache_key in self._clients:
                del self._clients[cache_key]
            
            logger.info("ExchangeFactory", f"{exchange_id} 자격증명 저장 완료")
            return True
            
        except Exception as e:
            logger.error("ExchangeFactory", f"자격증명 저장 실패: {str(e)}")
            return False
    
    def test_connection(self, exchange_id: str, api_key: str, secret: str,
                       passphrase: str = None, is_testnet: bool = False) -> tuple:
        """
        연결 테스트 (저장하지 않고 테스트만)
        
        Returns:
            (성공 여부, 메시지)
        """
        try:
            client = CCXTClient(
                exchange_id=exchange_id,
                api_key=api_key,
                secret=secret,
                passphrase=passphrase,
                is_testnet=is_testnet
            )
            return client.test_connection()
            
        except Exception as e:
            return False, f"클라이언트 생성 실패: {str(e)}"
    
    def has_credentials(self, exchange_id: str, is_testnet: bool = False) -> bool:
        """자격증명 존재 여부"""
        return self.credentials_repo.has_credentials(exchange_id, is_testnet)
    
    def get_configured_exchanges(self) -> List[str]:
        """자격증명이 설정된 거래소 목록"""
        all_creds = self.credentials_repo.get_all_credentials()
        return list(set([c['exchange_id'] for c in all_creds if c.get('api_key')]))
    
    def get_enabled_exchanges(self) -> List[Dict]:
        """활성화된 거래소 목록"""
        return self.exchanges_repo.get_enabled_exchanges()
    
    def get_testnet_exchanges(self) -> List[Dict]:
        """테스트넷 지원 거래소 목록"""
        return self.exchanges_repo.get_testnet_exchanges()
    
    def clear_cache(self, exchange_id: str = None):
        """캐시 정리"""
        if exchange_id:
            keys_to_delete = [k for k in self._clients.keys() if k.startswith(exchange_id)]
            for key in keys_to_delete:
                del self._clients[key]
        else:
            self._clients.clear()


# 전역 팩토리 인스턴스
_factory = None


def get_exchange_factory() -> ExchangeFactory:
    """전역 팩토리 인스턴스 조회"""
    global _factory
    if _factory is None:
        _factory = ExchangeFactory()
    return _factory


def get_client(exchange_id: str, is_testnet: bool = False) -> Optional[CCXTClient]:
    """거래소 클라이언트 조회 (편의 함수)"""
    return get_exchange_factory().get_client(exchange_id, is_testnet)


def get_public_client(exchange_id: str, is_testnet: bool = False) -> Optional[CCXTClient]:
    """공개 클라이언트 조회 (편의 함수)"""
    return get_exchange_factory().get_client_without_auth(exchange_id, is_testnet)

