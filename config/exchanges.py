"""
거래소 메타데이터 설정
CoinGecko Top 100 중 CCXT 선물(Perpetual/Futures) 지원 거래소
"""

# CCXT 거래소 ID와 메타데이터
# 순위는 CoinGecko 기준 (2024년 12월)
SUPPORTED_EXCHANGES = {
    # Tier 1 - Top 20 (우선 지원)
    "binance": {
        "name": "Binance",
        "rank": 1,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://testnet.binancefuture.com",
        "testnet_separate_api": True,  # 테스트넷 전용 API 키 필요
        "maker_fee": 0.0002,  # 0.02%
        "taker_fee": 0.0004,  # 0.04%
        "futures_type": "swap",  # USDT-M Perpetual
        "symbol_format": "{base}/{quote}:USDT",  # BTC/USDT:USDT
        "requires_passphrase": False,
    },
    "bybit": {
        "name": "Bybit",
        "rank": 3,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://testnet.bybit.com",
        "maker_fee": 0.0001,
        "taker_fee": 0.0006,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "okx": {
        "name": "OKX",
        "rank": 4,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://www.okx.com",  # Demo mode
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": True,
    },
    "bitget": {
        "name": "Bitget",
        "rank": 6,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://testnet.bitget.com",
        "maker_fee": 0.0002,
        "taker_fee": 0.0006,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": True,
    },
    "gate": {
        "name": "Gate.io",
        "rank": 7,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.00015,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "kucoin": {
        "name": "KuCoin",
        "rank": 8,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://sandbox.kucoin.com",
        "maker_fee": 0.0002,
        "taker_fee": 0.0006,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": True,
    },
    "htx": {
        "name": "HTX (Huobi)",
        "rank": 9,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "kraken": {
        "name": "Kraken",
        "rank": 10,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "cryptocom": {
        "name": "Crypto.com",
        "rank": 11,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.00015,
        "taker_fee": 0.0003,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "mexc": {
        "name": "MEXC",
        "rank": 12,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0,
        "taker_fee": 0.0002,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "deribit": {
        "name": "Deribit",
        "rank": 15,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://test.deribit.com",
        "maker_fee": 0.0,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "bingx": {
        "name": "BingX",
        "rank": 16,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://testnet.bingx.com",
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "phemex": {
        "name": "Phemex",
        "rank": 17,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://testnet.phemex.com",
        "maker_fee": 0.0001,
        "taker_fee": 0.0006,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "bitmart": {
        "name": "BitMart",
        "rank": 18,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0006,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "whitebit": {
        "name": "WhiteBIT",
        "rank": 19,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0001,
        "taker_fee": 0.00035,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "bitfinex": {
        "name": "Bitfinex",
        "rank": 20,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0001,
        "taker_fee": 0.0002,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    
    # Tier 2 - 21-50
    "coinex": {
        "name": "CoinEx",
        "rank": 21,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "lbank": {
        "name": "LBank",
        "rank": 23,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "woo": {
        "name": "WOO X",
        "rank": 25,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0,
        "taker_fee": 0.0003,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "xt": {
        "name": "XT.COM",
        "rank": 27,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "probit": {
        "name": "ProBit",
        "rank": 30,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "digifinex": {
        "name": "DigiFinex",
        "rank": 32,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "ascendex": {
        "name": "AscendEX",
        "rank": 35,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "bitrue": {
        "name": "Bitrue",
        "rank": 38,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "bitvavo": {
        "name": "Bitvavo",
        "rank": 40,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0003,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "tidex": {
        "name": "Tidex",
        "rank": 42,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.001,
        "taker_fee": 0.001,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "btcex": {
        "name": "BTCEX",
        "rank": 45,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "delta": {
        "name": "Delta Exchange",
        "rank": 48,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://testnet.delta.exchange",
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    
    # Tier 3 - 51-100 (선물 지원하는 거래소만)
    "pionex": {
        "name": "Pionex",
        "rank": 52,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "hyperliquid": {
        "name": "Hyperliquid",
        "rank": 55,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://testnet.hyperliquid.xyz",
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "vertex": {
        "name": "Vertex",
        "rank": 60,
        "has_futures": True,
        "has_testnet": True,
        "testnet_url": "https://testnet.vertexprotocol.com",
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "blofin": {
        "name": "Blofin",
        "rank": 65,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0005,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "hashkey": {
        "name": "HashKey",
        "rank": 70,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "poloniex": {
        "name": "Poloniex",
        "rank": 75,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "hitbtc": {
        "name": "HitBTC",
        "rank": 80,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.0001,
        "taker_fee": 0.0002,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "bitopro": {
        "name": "BitoPro",
        "rank": 85,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.001,
        "taker_fee": 0.002,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "exmo": {
        "name": "EXMO",
        "rank": 90,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.001,
        "taker_fee": 0.001,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
    "latoken": {
        "name": "LATOKEN",
        "rank": 95,
        "has_futures": True,
        "has_testnet": False,
        "testnet_url": None,
        "maker_fee": 0.00049,
        "taker_fee": 0.00049,
        "futures_type": "swap",
        "symbol_format": "{base}/{quote}:USDT",
        "requires_passphrase": False,
    },
}

# 테스트넷 지원 거래소 목록
TESTNET_EXCHANGES = [
    ex_id for ex_id, ex_data in SUPPORTED_EXCHANGES.items() 
    if ex_data.get("has_testnet")
]

# 모든 지원 거래소 ID 목록 (CoinGecko 순위순)
ALL_EXCHANGE_IDS = list(SUPPORTED_EXCHANGES.keys())

# 기본 거래소 (Binance)
DEFAULT_EXCHANGE_ID = "binance"

# 기본 활성화 거래소 (전체)
DEFAULT_ENABLED_EXCHANGES = ALL_EXCHANGE_IDS

# 기본 심볼 목록 (CCXT 통일 형식)
DEFAULT_SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT",
]

# 타임프레임 매핑 (CCXT 표준)
TIMEFRAMES = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}

# 레거시 타임프레임 변환 (OKX 형식 → CCXT 형식)
LEGACY_TIMEFRAME_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1H": "1h",
    "4H": "4h",
    "1D": "1d",
}


def get_exchange_info(exchange_id: str) -> dict:
    """거래소 정보 조회"""
    return SUPPORTED_EXCHANGES.get(exchange_id, {})


def get_exchange_fee(exchange_id: str, fee_type: str = "taker") -> float:
    """거래소 수수료 조회"""
    info = get_exchange_info(exchange_id)
    if fee_type == "maker":
        return info.get("maker_fee", 0.0002)
    return info.get("taker_fee", 0.0005)


def format_symbol(exchange_id: str, base: str, quote: str = "USDT") -> str:
    """거래소별 심볼 형식으로 변환"""
    info = get_exchange_info(exchange_id)
    fmt = info.get("symbol_format", "{base}/{quote}:USDT")
    return fmt.format(base=base, quote=quote)


def parse_symbol(symbol: str) -> tuple:
    """
    CCXT 통일 심볼을 base, quote로 파싱
    예: BTC/USDT:USDT -> (BTC, USDT)
    """
    if ":" in symbol:
        symbol = symbol.split(":")[0]
    if "/" in symbol:
        base, quote = symbol.split("/")
        return base, quote
    return symbol, "USDT"


def get_testnet_exchanges() -> list:
    """테스트넷 지원 거래소 목록"""
    return TESTNET_EXCHANGES


def get_futures_exchanges() -> list:
    """선물 지원 거래소 목록"""
    return [
        ex_id for ex_id, ex_data in SUPPORTED_EXCHANGES.items()
        if ex_data.get("has_futures")
    ]

