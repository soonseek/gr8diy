"""
애플리케이션 전역 설정
"""
import os
import sys
from pathlib import Path


def get_app_dir():
    """애플리케이션 디렉토리 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 실행 중 (exe)
        # 실행 파일이 있는 폴더
        return Path(sys.executable).parent
    else:
        # 개발 환경 (Python 스크립트)
        return Path(__file__).parent.parent.absolute()


# 프로젝트 루트 경로
PROJECT_ROOT = get_app_dir()

# 데이터 디렉토리
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# 데이터베이스 경로
DB_PATH = DATA_DIR / "trading_bot.db"

# 암호화된 자격증명 저장 경로
CREDENTIALS_PATH = DATA_DIR / "credentials.enc"

# 로그 설정
LOG_RETENTION_DAYS = 200
DATA_RETENTION_DAYS = 200

# 타임존
TIMEZONE = "Asia/Seoul"

# OKX 설정
OKX_BASE_URL = "https://www.okx.com"
OKX_API_BASE = "https://www.okx.com"
OKX_WS_PUBLIC = "wss://ws.okx.com:8443/ws/v5/public"
OKX_WS_PRIVATE = "wss://ws.okx.com:8443/ws/v5/private"
OKX_WS_BUSINESS = "wss://ws.okx.com:8443/ws/v5/business"

# Rate Limit 설정 (OKX 공식보다 여유있게)
OKX_RATE_LIMIT_PER_SECOND = 10  # 초당 최대 요청 수
OKX_RATE_LIMIT_COOLDOWN = 60  # 429 발생 시 대기 시간(초)

# 기본 심볼 목록
DEFAULT_SYMBOLS = [
    "BTC-USDT-SWAP",
    "ETH-USDT-SWAP",
    "SOL-USDT-SWAP",
    "XRP-USDT-SWAP",
    "DOGE-USDT-SWAP"
]

# 타임프레임
TIMEFRAMES = ["1m", "5m", "15m", "1H", "4H", "1D"]

# 보조지표 기본 파라미터
INDICATOR_PARAMS = {
    "MA": [20, 50, 100, 200],
    "MACD": {"fast": 12, "slow": 26, "signal": 9},
    "RSI": {"period": 14},
    "STOCH": {"k_period": 14, "d_period": 3, "smooth": 3},
    "BOLLINGER": {"period": 20, "std_dev": 2}
}

# 봇 설정
BOT_INTERVALS = ["1m", "5m", "15m"]
MAX_LEVERAGE = 20
MIN_LEVERAGE = 1
MAX_MARTINGALE_STEPS = 10

# 마틴게일 기본 사이즈 비율
DEFAULT_MARTINGALE_RATIOS = [1, 1, 2, 4, 8, 16, 32, 64, 128, 256]

# UI 설정
WINDOW_TITLE = "OKX Trading Bot"
LOG_VIEW_MAX_LINES = 1000

# GPT 설정
GPT_DEFAULT_MODEL = "gpt-4"
GPT_TIMEOUT = 30


