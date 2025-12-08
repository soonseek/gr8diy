"""
보조지표 계산기
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from config.settings import INDICATOR_PARAMS


class IndicatorCalculator:
    """기술적 지표 계산"""
    
    @staticmethod
    def calculate_ma(prices: pd.Series, period: int) -> pd.Series:
        """이동평균선 (MA)"""
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def calculate_macd(prices: pd.Series, 
                      fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return {
            "macd": macd.iloc[-1] if len(macd) > 0 else None,
            "signal": signal_line.iloc[-1] if len(signal_line) > 0 else None,
            "histogram": histogram.iloc[-1] if len(histogram) > 0 else None
        }
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if len(rsi) > 0 else None
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                            k_period: int = 14, d_period: int = 3) -> Dict:
        """Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=d_period).mean()
        
        return {
            "k": k.iloc[-1] if len(k) > 0 else None,
            "d": d.iloc[-1] if len(d) > 0 else None
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, 
                                 period: int = 20, std_dev: float = 2) -> Dict:
        """Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            "upper": upper.iloc[-1] if len(upper) > 0 else None,
            "middle": middle.iloc[-1] if len(middle) > 0 else None,
            "lower": lower.iloc[-1] if len(lower) > 0 else None
        }
    
    @staticmethod
    def calculate_all_indicators(candles: List[Dict]) -> Dict:
        """
        모든 지표 계산
        
        candles: [{"open": ..., "high": ..., "low": ..., "close": ..., "volume": ...}, ...]
        """
        if not candles or len(candles) < 200:  # 최소 200개 필요 (MA200)
            return {}
        
        # DataFrame 변환
        df = pd.DataFrame(candles)
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        
        # 이동평균선
        indicators = {}
        for period in INDICATOR_PARAMS['MA']:
            ma = IndicatorCalculator.calculate_ma(df['close'], period)
            indicators[f'ma_{period}'] = ma.iloc[-1] if len(ma) > 0 else None
        
        # MACD
        macd_params = INDICATOR_PARAMS['MACD']
        macd_result = IndicatorCalculator.calculate_macd(
            df['close'],
            macd_params['fast'],
            macd_params['slow'],
            macd_params['signal']
        )
        indicators['macd'] = macd_result['macd']
        indicators['macd_signal'] = macd_result['signal']
        indicators['macd_hist'] = macd_result['histogram']
        
        # RSI
        rsi_period = INDICATOR_PARAMS['RSI']['period']
        indicators['rsi'] = IndicatorCalculator.calculate_rsi(df['close'], rsi_period)
        
        # Stochastic
        stoch_params = INDICATOR_PARAMS['STOCH']
        stoch_result = IndicatorCalculator.calculate_stochastic(
            df['high'], df['low'], df['close'],
            stoch_params['k_period'], stoch_params['d_period']
        )
        indicators['stoch_k'] = stoch_result['k']
        indicators['stoch_d'] = stoch_result['d']
        
        # Bollinger Bands
        bb_params = INDICATOR_PARAMS['BOLLINGER']
        bb_result = IndicatorCalculator.calculate_bollinger_bands(
            df['close'],
            bb_params['period'],
            bb_params['std_dev']
        )
        indicators['bb_upper'] = bb_result['upper']
        indicators['bb_middle'] = bb_result['middle']
        indicators['bb_lower'] = bb_result['lower']
        
        return indicators


