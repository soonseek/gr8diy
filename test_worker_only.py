#!/usr/bin/env python3
"""
데이터 수집 워커만 단독 테스트
"""
import sys
from datetime import datetime

# 프로젝트 모듈 경로 추가
sys.path.insert(0, '.')

from workers.data_collector import DataCollectorWorker
from api.exchange_factory import get_public_client
from config.settings import TIMEFRAMES
from utils.time_helper import time_helper

def test_worker_only():
    """워커 단독 테스트"""
    print("="*60)
    print("데이터 수집 워커 단독 테스트")
    print("="*60)

    # 기본 설정
    exchange_id = "okx"
    test_symbols = ["BTC/USDT:USDT"]  # 테스트용 심볼 1개만
    start_date = datetime(2024, 12, 1)
    start_date = time_helper.kst.localize(start_date)

    print(f"거래소: {exchange_id}")
    print(f"테스트 심볼: {test_symbols}")
    print(f"시작 날짜: {start_date}")
    print(f"타임프레임: {TIMEFRAMES}")

    try:
        # 클라이언트 생성
        print("\n1. 클라이언트 생성...")
        client = get_public_client(exchange_id)
        if not client:
            print(f"[ERROR] 클라이언트 생성 실패: {exchange_id}")
            return

        print(f"[SUCCESS] 클라이언트 생성 성공: {type(client)}")

        # 워커 생성
        print("\n2. 워커 생성...")
        worker = DataCollectorWorker(exchange_id, client)
        print("[SUCCESS] 워커 생성 성공")

        # 진행률 콜백 설정
        def on_progress(msg, cur, total):
            print(f"[진행률] {msg} ({cur}/{total})")

        def on_completed():
            print("\n[SUCCESS] 데이터 수집 완료!")

        def on_error(error_msg):
            print(f"\n[ERROR] 데이터 수집 오류: {error_msg}")

        worker.progress_updated.connect(on_progress)
        worker.collection_completed.connect(on_completed)
        worker.error_occurred.connect(on_error)

        print("\n3. 데이터 수집 시작...")
        print("-" * 40)

        # 첫 번째 심볼과 첫 번째 타임프레임만 테스트
        test_symbols = [test_symbols[0]]
        test_timeframes = [TIMEFRAMES[0]]  # 1분봉만 테스트

        print(f"테스트 축소: {test_symbols}, {test_timeframes}")

        # 임시로 타임프레임 변경 (테스트용)
        original_timeframes = TIMEFRAMES.copy()
        TIMEFRAMES.clear()
        TIMEFRAMES.extend(test_timeframes)

        # 데이터 수집 실행
        worker.backfill_data(test_symbols, start_date, exchange_id)

        # 원복
        TIMEFRAMES.clear()
        TIMEFRAMES.extend(original_timeframes)

    except Exception as e:
        import traceback
        print(f"\n[ERROR] 테스트 실패: {e}")
        print("상세 에러:")
        traceback.print_exc()

if __name__ == "__main__":
    test_worker_only()