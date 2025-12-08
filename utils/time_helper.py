"""
시간/타임존 유틸리티
"""
from datetime import datetime, timedelta
import pytz
from config.settings import TIMEZONE


class TimeHelper:
    """KST 기준 시간 처리 헬퍼"""
    
    def __init__(self):
        self.kst = pytz.timezone(TIMEZONE)
        self.utc = pytz.UTC
    
    def now_kst(self) -> datetime:
        """현재 KST 시간"""
        return datetime.now(self.kst)
    
    def now_utc(self) -> datetime:
        """현재 UTC 시간"""
        return datetime.now(self.utc)
    
    def to_kst(self, dt: datetime) -> datetime:
        """UTC를 KST로 변환"""
        if dt.tzinfo is None:
            dt = self.utc.localize(dt)
        return dt.astimezone(self.kst)
    
    def to_utc(self, dt: datetime) -> datetime:
        """KST를 UTC로 변환"""
        if dt.tzinfo is None:
            dt = self.kst.localize(dt)
        return dt.astimezone(self.utc)
    
    def timestamp_to_kst(self, timestamp: int) -> datetime:
        """Unix timestamp(ms)를 KST datetime으로 변환"""
        dt_utc = datetime.fromtimestamp(timestamp / 1000, tz=self.utc)
        return self.to_kst(dt_utc)
    
    def kst_to_timestamp(self, dt: datetime) -> int:
        """KST datetime을 Unix timestamp(ms)로 변환"""
        if dt.tzinfo is None:
            dt = self.kst.localize(dt)
        return int(dt.timestamp() * 1000)
    
    def format_kst(self, dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """KST datetime을 문자열로 포맷"""
        return dt.strftime(fmt)
    
    def days_ago_kst(self, days: int) -> datetime:
        """현재로부터 N일 전 KST 시간"""
        return self.now_kst() - timedelta(days=days)
    
    def is_within_retention(self, dt: datetime, retention_days: int) -> bool:
        """지정된 보존 기간 내의 데이터인지 확인"""
        cutoff = self.now_kst() - timedelta(days=retention_days)
        if dt.tzinfo is None:
            dt = self.kst.localize(dt)
        return dt > cutoff


# 전역 헬퍼 인스턴스
time_helper = TimeHelper()


