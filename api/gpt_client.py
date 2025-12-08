"""
GPT API 클라이언트
"""
from typing import Optional, List, Dict
import openai
from config.settings import GPT_DEFAULT_MODEL, GPT_TIMEOUT
from utils.logger import logger


class GPTClient:
    """OpenAI GPT API 클라이언트"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
    
    def set_api_key(self, api_key: str):
        """API 키 설정"""
        self.api_key = api_key
        openai.api_key = api_key
    
    def test_connection(self) -> tuple[bool, str]:
        """연결 테스트"""
        if not self.api_key:
            return False, "API 키가 설정되지 않았습니다"
        
        try:
            # 모델 목록 조회로 간단 테스트
            response = openai.models.list()
            
            if response:
                logger.info("GPT", "GPT API 연동 성공")
                return True, "GPT API 연동 성공"
            else:
                return False, "API 응답이 없습니다"
                
        except openai.AuthenticationError:
            return False, "API 키 인증 실패"
        except openai.APIConnectionError:
            return False, "네트워크 연결 실패"
        except Exception as e:
            return False, f"연결 테스트 실패: {str(e)}"
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       model: str = None,
                       temperature: float = 0.7,
                       max_tokens: int = 500) -> Optional[str]:
        """
        채팅 완성 API 호출
        
        messages: [{"role": "user", "content": "..."}] 형식
        """
        if not self.api_key:
            logger.error("GPT", "API 키가 설정되지 않았습니다")
            return None
        
        try:
            response = openai.chat.completions.create(
                model=model or GPT_DEFAULT_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=GPT_TIMEOUT
            )
            
            if response.choices:
                content = response.choices[0].message.content
                logger.info("GPT", "채팅 완성 성공")
                return content
            
            return None
            
        except Exception as e:
            logger.error("GPT", f"채팅 완성 실패: {str(e)}")
            return None
    
    def analyze_market(self, symbol: str, indicators: Dict) -> Optional[str]:
        """
        시장 분석 (추후 확장용)
        
        현재는 기본 구조만 제공
        """
        prompt = f"""
        다음 기술적 지표를 바탕으로 {symbol}의 시장 상황을 분석해주세요:
        
        - MA20: {indicators.get('ma_20')}
        - MA50: {indicators.get('ma_50')}
        - RSI: {indicators.get('rsi')}
        - MACD: {indicators.get('macd')}
        
        간단한 분석과 추천을 제공해주세요.
        """
        
        messages = [
            {"role": "system", "content": "당신은 암호화폐 시장 분석 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages, max_tokens=300)


