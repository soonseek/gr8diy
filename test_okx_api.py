#!/usr/bin/env python3
"""
OKX API 직접 테스트
"""
import requests
from datetime import datetime, timedelta

def test_okx_api():
    """OKX API 직접 테스트"""

    # 기본 파라미터
    url = "https://www.okx.com/api/v5/market/candles"

    # 현재 시간
    now = datetime.now()

    # 여러 가지 파라미터 조합 테스트
    test_cases = [
        # 1. 심볼만 (가장 간단)
        {
            "instId": "BTC-USDT-SWAP",
            "bar": "1m",
            "limit": "10"
        },
        # 2. 타임스탬프 추가 (밀리초)
        {
            "instId": "BTC-USDT-SWAP",
            "bar": "1m",
            "limit": "10",
            "after": str(int(now.timestamp() * 1000))
        }
    ]

    for i, params in enumerate(test_cases):
        print(f"\n=== 테스트 케이스 {i+1} ===")
        print(f"파라미터: {params}")

        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"상태 코드: {response.status_code}")
            print(f"URL: {response.url}")

            if response.status_code == 200:
                data = response.json()
                print(f"응답: {data}")
                if 'data' in data and data['data']:
                    print(f"✅ 성공: {len(data['data'])}개 데이터 수집")
                else:
                    print("❌ 응답에 데이터가 없음")
            else:
                print(f"❌ 에러: {response.text}")

        except Exception as e:
            print(f"❌ 예외: {str(e)}")

if __name__ == "__main__":
    test_okx_api()