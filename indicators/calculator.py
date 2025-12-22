"""
보조지표 계산기
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import talib
from config.settings import INDICATOR_PARAMS
from utils.logger import logger


class IndicatorCalculator:
    """기술적 지표 계산"""

    def __init__(self):
        self.params = INDICATOR_PARAMS

    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, any]:
        """모든 보조지표 계산"""
        indicators = {}

        try:
            # 가격 데이터 추출
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']

            # 이동평균선 (MA)
            indicators['MA'] = self.calculate_ma(close)

            # MACD
            indicators['MACD'] = self.calculate_macd(close)

            # RSI
            indicators['RSI'] = self.calculate_rsi(close)

            # Stochastic
            indicators['STOCH'] = self.calculate_stochastic(high, low, close)

            # Bollinger Bands
            indicators['BOLLINGER'] = self.calculate_bollinger_bands(close)

            # 추가 지표들
            indicators['EMA'] = self.calculate_ema(close)
            indicators['ATR'] = self.calculate_atr(high, low, close)
            indicators['OBV'] = self.calculate_obv(close, volume)
            indicators['WILLIAMS_R'] = self.calculate_williams_r(high, low, close)
            indicators['CCI'] = self.calculate_cci(high, low, close)
            indicators['MFI'] = self.calculate_mfi(high, low, close, volume)

            logger.debug("IndicatorCalculator", f"보조지표 계산 완료: {len(indicators)}개")

        except Exception as e:
            logger.error("IndicatorCalculator", f"보조지표 계산 실패: {str(e)}")

        return indicators

    def calculate_ma(self, close: pd.Series, periods: List[int] = None) -> Dict[str, float]:
        """이동평균선 (MA)"""
        if periods is None:
            periods = self.params["MA"]

        result = {}
        for period in periods:
            try:
                ma_values = talib.SMA(close.values, timeperiod=period)
                result[f'MA_{period}'] = float(ma_values[-1]) if not np.isnan(ma_values[-1]) else None
            except Exception as e:
                logger.warning("IndicatorCalculator", f"MA_{period} 계산 실패: {str(e)}")
                result[f'MA_{period}'] = None

        return result

    def calculate_ema(self, close: pd.Series, periods: List[int] = None) -> Dict[str, float]:
        """지수 이동평균선 (EMA)"""
        if periods is None:
            periods = [12, 26, 50]  # 기본값

        result = {}
        for period in periods:
            try:
                ema_values = talib.EMA(close.values, timeperiod=period)
                result[f'EMA_{period}'] = float(ema_values[-1]) if not np.isnan(ema_values[-1]) else None
            except Exception as e:
                logger.warning("IndicatorCalculator", f"EMA_{period} 계산 실패: {str(e)}")
                result[f'EMA_{period}'] = None

        return result

    def calculate_macd(self, close: pd.Series, params: Dict = None) -> Dict[str, float]:
        """MACD"""
        if params is None:
            params = self.params["MACD"]

        try:
            fast = params["fast"]
            slow = params["slow"]
            signal = params["signal"]

            macd, signal_line, histogram = talib.MACD(close.values, fastperiod=fast, slowperiod=slow, signalperiod=signal)

            return {
                "MACD": float(macd[-1]) if not np.isnan(macd[-1]) else None,
                "MACD_Signal": float(signal_line[-1]) if not np.isnan(signal_line[-1]) else None,
                "MACD_Histogram": float(histogram[-1]) if not np.isnan(histogram[-1]) else None
            }
        except Exception as e:
            logger.warning("IndicatorCalculator", f"MACD 계산 실패: {str(e)}")
            return {"MACD": None, "MACD_Signal": None, "MACD_Histogram": None}

    def calculate_rsi(self, close: pd.Series, period: int = None) -> Optional[float]:
        """RSI (Relative Strength Index)"""
        if period is None:
            period = self.params["RSI"]["period"]

        try:
            rsi_values = talib.RSI(close.values, timeperiod=period)
            return float(rsi_values[-1]) if not np.isnan(rsi_values[-1]) else None
        except Exception as e:
            logger.warning("IndicatorCalculator", f"RSI 계산 실패: {str(e)}")
            return None

    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, params: Dict = None) -> Dict[str, float]:
        """Stochastic Oscillator"""
        if params is None:
            params = self.params["STOCH"]

        try:
            k_period = params["k_period"]
            d_period = params["d_period"]

            slowk, slowd = talib.STOCH(high.values, low.values, close.values,
                                      fastk_period=k_period, slowk_period=params.get("smooth", 3),
                                      slowd_period=d_period)

            return {
                "STOCH_K": float(slowk[-1]) if not np.isnan(slowk[-1]) else None,
                "STOCH_D": float(slowd[-1]) if not np.isnan(slowd[-1]) else None
            }
        except Exception as e:
            logger.warning("IndicatorCalculator", f"Stochastic 계산 실패: {str(e)}")
            return {"STOCH_K": None, "STOCH_D": None}

    def calculate_bollinger_bands(self, close: pd.Series, params: Dict = None) -> Dict[str, float]:
        """볼린저 밴드"""
        if params is None:
            params = self.params["BOLLINGER"]

        try:
            period = params["period"]
            std_dev = params["std_dev"]

            upper, middle, lower = talib.BBANDS(close.values, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)

            return {
                "BB_Upper": float(upper[-1]) if not np.isnan(upper[-1]) else None,
                "BB_Middle": float(middle[-1]) if not np.isnan(middle[-1]) else None,
                "BB_Lower": float(lower[-1]) if not np.isnan(lower[-1]) else None
            }
        except Exception as e:
            logger.warning("IndicatorCalculator", f"볼린저 밴드 계산 실패: {str(e)}")
            return {"BB_Upper": None, "BB_Middle": None, "BB_Lower": None}

    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Optional[float]:
        """ATR (Average True Range)"""
        try:
            atr_values = talib.ATR(high.values, low.values, close.values, timeperiod=period)
            return float(atr_values[-1]) if not np.isnan(atr_values[-1]) else None
        except Exception as e:
            logger.warning("IndicatorCalculator", f"ATR 계산 실패: {str(e)}")
            return None

    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> Optional[float]:
        """OBV (On Balance Volume)"""
        try:
            obv_values = talib.OBV(close.values, volume.values)
            return float(obv_values[-1]) if not np.isnan(obv_values[-1]) else None
        except Exception as e:
            logger.warning("IndicatorCalculator", f"OBV 계산 실패: {str(e)}")
            return None

    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Optional[float]:
        """Williams %R"""
        try:
            wr_values = talib.WILLR(high.values, low.values, close.values, timeperiod=period)
            return float(wr_values[-1]) if not np.isnan(wr_values[-1]) else None
        except Exception as e:
            logger.warning("IndicatorCalculator", f"Williams %R 계산 실패: {str(e)}")
            return None

    def calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> Optional[float]:
        """CCI (Commodity Channel Index)"""
        try:
            cci_values = talib.CCI(high.values, low.values, close.values, timeperiod=period)
            return float(cci_values[-1]) if not np.isnan(cci_values[-1]) else None
        except Exception as e:
            logger.warning("IndicatorCalculator", f"CCI 계산 실패: {str(e)}")
            return None

    def calculate_mfi(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14) -> Optional[float]:
        """MFI (Money Flow Index)"""
        try:
            mfi_values = talib.MFI(high.values, low.values, close.values, volume.values, timeperiod=period)
            return float(mfi_values[-1]) if not np.isnan(mfi_values[-1]) else None
        except Exception as e:
            logger.warning("IndicatorCalculator", f"MFI 계산 실패: {str(e)}")
            return None