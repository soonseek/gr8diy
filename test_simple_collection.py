#!/usr/bin/env python3
"""
간단한 데이터 수집 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import sqlite3
from datetime import datetime, timedelta

def test_simple_collection():
    """간단한 데이터 수집 테스트"""

    # DB 초기화
    conn = sqlite3.connect('database/trading_bot.db')
    cursor = conn.cursor()

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

    # API 테스트
    url = "https://www.okx.com/api/v5/market/candles"
    params = {
        "instId": "BTC-USDT-SWAP",
        "bar": "1m",
        "limit": "5"
    }

    print("OKX API 테스트...")
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('code') == '0' and data.get('data'):
            candles = data['data']
            print(f"✅ API 응답 성공: {len(candles)}개 데이터")

            # 데이터 저장 테스트
            saved_count = 0
            for candle in candles:
                timestamp_ms = int(candle[0])
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000)

                cursor.execute('''
                    INSERT OR REPLACE INTO candles
                    (exchange_id, symbol, timeframe, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', ("okx", "BTC-USDT-SWAP", "1m", timestamp,
                      float(candle[1]), float(candle[2]), float(candle[3]),
                      float(candle[4]), float(candle[5])))
                saved_count += 1

            conn.commit()
            print(f"✅ {saved_count}개 데이터 저장 성공")

            # 저장 확인
            cursor.execute('SELECT COUNT(*) FROM candles WHERE exchange_id = "okx"')
            count = cursor.fetchone()[0]
            print(f"✅ DB 저장 확인: {count}개 데이터")

            # 최신 데이터 확인
            cursor.execute('''
                SELECT timestamp, close, volume
                FROM candles
                WHERE exchange_id = "okx"
                ORDER BY timestamp DESC
                LIMIT 3
            ''')
            recent = cursor.fetchall()
            print("최신 데이터:")
            for ts, close, vol in recent:
                print(f"  {ts}: Close={close}, Volume={vol}")

        else:
            print(f"❌ API 데이터 없음: {data}")
    else:
        print(f"❌ API 오류: {response.status_code} - {response.text}")

    conn.close()

if __name__ == "__main__":
    test_simple_collection()