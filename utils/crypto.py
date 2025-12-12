"""
암호화 유틸리티 (API 키 등 민감 정보 저장용)
"""
import base64
import json
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


class CredentialManager:
    """자격증명 암호화 관리"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self._key = self._get_or_create_key()
        self._cipher = Fernet(self._key)
    
    def _get_or_create_key(self) -> bytes:
        """암호화 키 생성 또는 로드"""
        key_path = self.storage_path.parent / ".key"
        
        if key_path.exists():
            with open(key_path, "rb") as f:
                return f.read()
        else:
            # 시스템 정보 기반으로 키 생성 (간단한 방법)
            # 실제 프로덕션에서는 더 안전한 방법 사용 권장
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            # 시스템 고유 정보 사용
            password = (os.environ.get("COMPUTERNAME", "default") + 
                       os.environ.get("USERNAME", "user")).encode()
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            with open(key_path, "wb") as f:
                f.write(key)
            
            # 키 파일 숨김 처리 (Windows)
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(key_path), 2)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
            
            return key
    
    def save_credentials(self, credentials: dict):
        """자격증명 암호화 저장"""
        json_data = json.dumps(credentials)
        encrypted = self._cipher.encrypt(json_data.encode())
        
        with open(self.storage_path, "wb") as f:
            f.write(encrypted)
    
    def load_credentials(self) -> dict:
        """자격증명 복호화 로드"""
        if not self.storage_path.exists():
            return {}
        
        try:
            with open(self.storage_path, "rb") as f:
                encrypted = f.read()
            
            decrypted = self._cipher.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            print(f"자격증명 로드 실패: {e}")
            return {}
    
    def get_okx_credentials(self) -> dict:
        """OKX 자격증명 조회"""
        creds = self.load_credentials()
        return {
            "api_key": creds.get("okx_api_key", ""),
            "secret": creds.get("okx_secret", ""),
            "passphrase": creds.get("okx_passphrase", "")
        }
    
    def get_gpt_credentials(self) -> dict:
        """GPT 자격증명 조회"""
        creds = self.load_credentials()
        return {
            "api_key": creds.get("gpt_api_key", "")
        }
    
    def update_okx_credentials(self, api_key: str, secret: str, passphrase: str):
        """OKX 자격증명 업데이트"""
        creds = self.load_credentials()
        creds["okx_api_key"] = api_key
        creds["okx_secret"] = secret
        creds["okx_passphrase"] = passphrase
        self.save_credentials(creds)
    
    def update_gpt_credentials(self, api_key: str):
        """GPT 자격증명 업데이트"""
        creds = self.load_credentials()
        creds["gpt_api_key"] = api_key
        self.save_credentials(creds)
    
    # ========== 멀티 거래소 지원 ==========
    
    def get_exchange_credentials(self, exchange_id: str, is_testnet: bool = False) -> dict:
        """
        거래소별 자격증명 조회
        
        Args:
            exchange_id: 거래소 ID (binance, bybit, okx 등)
            is_testnet: 테스트넷 여부
        
        Returns:
            {api_key, secret, passphrase}
        """
        creds = self.load_credentials()
        prefix = f"{exchange_id}_testnet" if is_testnet else exchange_id
        
        return {
            "api_key": creds.get(f"{prefix}_api_key", ""),
            "secret": creds.get(f"{prefix}_secret", ""),
            "passphrase": creds.get(f"{prefix}_passphrase", "")
        }
    
    def save_exchange_credentials(self, exchange_id: str, api_key: str, 
                                  secret: str, passphrase: str = "",
                                  is_testnet: bool = False):
        """
        거래소별 자격증명 저장
        
        Args:
            exchange_id: 거래소 ID
            api_key: API 키
            secret: 시크릿
            passphrase: 패스프레이즈 (선택)
            is_testnet: 테스트넷 여부
        """
        creds = self.load_credentials()
        prefix = f"{exchange_id}_testnet" if is_testnet else exchange_id
        
        creds[f"{prefix}_api_key"] = api_key
        creds[f"{prefix}_secret"] = secret
        creds[f"{prefix}_passphrase"] = passphrase
        
        self.save_credentials(creds)
    
    def delete_exchange_credentials(self, exchange_id: str, is_testnet: bool = False):
        """
        거래소별 자격증명 삭제
        
        Args:
            exchange_id: 거래소 ID
            is_testnet: 테스트넷 여부
        """
        creds = self.load_credentials()
        prefix = f"{exchange_id}_testnet" if is_testnet else exchange_id
        
        keys_to_delete = [
            f"{prefix}_api_key",
            f"{prefix}_secret", 
            f"{prefix}_passphrase"
        ]
        
        for key in keys_to_delete:
            if key in creds:
                del creds[key]
        
        self.save_credentials(creds)
    
    def has_exchange_credentials(self, exchange_id: str, is_testnet: bool = False) -> bool:
        """거래소 자격증명 존재 여부"""
        creds = self.get_exchange_credentials(exchange_id, is_testnet)
        return bool(creds.get('api_key') and creds.get('secret'))
    
    def save_gpt_credentials(self, api_key: str):
        """GPT 자격증명 저장 (별칭)"""
        self.update_gpt_credentials(api_key)


