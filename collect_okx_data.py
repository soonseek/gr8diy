#!/usr/bin/env python3
"""
OKX 모든 심볼 1년 데이터 수집 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import sqlite3
from datetime import datetime, timedelta
import time

# OKX 무기한 선물 심볼
OKX_SYMBOLS = {
    "BTC": "BTC-USDT-SWAP",
    "ETH": "ETH-USDT-SWAP",
    "SOL": "SOL-USDT-SWAP",
    "XRP": "XRP-USDT-SWAP",
    "DOGE": "DOGE-USDT-SWAP"
}

class OKXDataCollector:
    def __init__(self):
        self.db_path = "database/trading_bot.db"
        self.base_url = "https://www.okx.com/api/v5/market/candles"

    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # candles 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exchange_id, symbol, timeframe, timestamp)
            )
        ''')

        conn.commit()
        conn.close()
        print("데이터베이스 초기화 완료")

    def get_candles(self, symbol, timeframe, after=None, before=None, limit=100):
        """OKX에서 캔들 데이터 가져오기"""
        params = {
            "instId": symbol,
            "bar": timeframe,
            "limit": str(limit)
        }

        if after:
            params["after"] = str(int(after.timestamp() * 1000))
        if before:
            params["before"] = str(int(before.timestamp() * 1000))

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0' and data.get('data'):
                    return data['data']
            else:
                print(f"API 오류: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"요청 실패: {str(e)}")

        return []

    def save_candles(self, symbol, timeframe, candles_data):
        """캔들 데이터 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        saved_count = 0
        for candle in candles_data:
            # OKX 데이터 형식: [timestamp, open, high, low, close, volume, ...]
            timestamp_ms = int(candle[0])
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000)

            open_price = float(candle[1])
            high_price = float(candle[2])
            low_price = float(candle[3])
            close_price = float(candle[4])
            volume = float(candle[5])

            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO candles
                    (exchange_id, symbol, timeframe, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', ("okx", symbol, timeframe, timestamp, open_price, high_price, low_price, close_price, volume))
                saved_count += 1
            except Exception as e:
                print(f"저장 실패: {str(e)}")

        conn.commit()
        conn.close()
        return saved_count

    def collect_symbol_data(self, coin_name, symbol, timeframe, start_date):
        """개별 심볼 데이터 수집"""
        print(f"\n{coin_name} ({symbol}) {timeframe} 데이터 수집 시작...")

        total_saved = 0
        current_date = start_date

        while current_date < datetime.now():
            # 1일씩 데이터 수집
            end_date = min(current_date + timedelta(days=1), datetime.now())

            print(f"  {current_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} 수집 중...")

            candles = self.get_candles(symbol, timeframe, current_date, end_date, 100)

            if candles:
                saved = self.save_candles(symbol, timeframe, candles)
                total_saved += saved
                print(f"    {saved}개 데이터 저장")
            else:
                print(f"    데이터 없음")

            current_date = end_date
            time.sleep(0.2)  # API 레이트 리밋 방지

        print(f"  {coin_name} {timeframe}: 총 {total_saved}개 데이터 저장 완료")
        return total_saved

    def collect_all_data(self, timeframes, start_date):
        """모든 심볼 데이터 수집"""
        print(f"OKX 데이터 수집 시작: {start_date.strftime('%Y-%m-%d')}부터")
        print(f"대상 심볼: {list(OKX_SYMBOLS.keys())}")
        print(f"타임프레임: {timeframes}")

        grand_total = 0

        for coin_name, symbol in OKX_SYMBOLS.items():
            for timeframe in timeframes:
                try:
                    count = self.collect_symbol_data(coin_name, symbol, timeframe, start_date)
                    grand_total += count
                except Exception as e:
                    print(f"  에러 발생: {str(e)}")
                    continue

        print(f"\n✅ 전체 데이터 수집 완료!")
        print(f"총 저장된 데이터 수: {grand_total:,}개")

        # 데이터베이스 통계
        self.show_database_stats()

    def show_database_stats(self):
        """데이터베이스 통계 표시"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 전체 데이터 수
        cursor.execute('SELECT COUNT(*) FROM candles')
        total_count = cursor.fetchone()[0]

        # 심볼별 데이터 수
        cursor.execute('''
            SELECT symbol, timeframe, COUNT(*) as count
            FROM candles
            WHERE exchange_id = 'okx'
            GROUP BY symbol, timeframe
            ORDER BY symbol, timeframe
        ''')
        symbol_stats = cursor.fetchall()

        # 날짜 범위
        cursor.execute('''
            SELECT MIN(timestamp), MAX(timestamp)
            FROM candles
            WHERE exchange_id = 'okx'
        ''')
        date_range = cursor.fetchone()

        conn.close()

        print(f"\n📊 데이터베이스 통계:")
        print(f"총 데이터 수: {total_count:,}개")

        if date_range[0] and date_range[1]:
            print(f"데이터 기간: {date_range[0]} ~ {date_range[1]}")

        print(f"\n심볼별 통계:")
        for symbol, timeframe, count in symbol_stats:
            print(f"  {symbol} {timeframe}: {count:,}개")

def main():
    collector = OKXDataCollector()

    # 데이터베이스 초기화
    collector.init_database()

    # 수집 설정 (먼저 테스트용으로 1분봉만 최근 30일)
    timeframes = ["1m"]
    start_date = datetime.now() - timedelta(days=30)  # 최근 30일

    # 데이터 수집 실행
    collector.collect_all_data(timeframes, start_date)

if __name__ == "__main__":
    main()