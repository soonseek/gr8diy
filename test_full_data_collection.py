#!/usr/bin/env python3
"""
전체 데이터 수집 프로세스 테스트 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from PySide6.QtCore import QCoreApplication
from workers.data_collector import DataCollectorWorker

def test_full_data_collection():
    """전체 데이터 수집 프로세스 테스트"""
    app = QCoreApplication(sys.argv)

    print("="*60)
    print("[TEST] 전체 데이터 수집 프로세스 테스트 시작")
    print("="*60)

    # 워커 생성
    worker = DataCollectorWorker(exchange_id="okx")

    # 시그널 연결
    def on_progress(message, current, total):
        print(f"[PROGRESS] 진행률: ({current}/{total}) {message}")

    def on_error(error_message):
        print(f"[ERROR] 에러 발생: {error_message}")

    def on_completed():
        print("[SUCCESS] 데이터 수집 완료!")
        app.quit()  # 애플리케이션 종료

    worker.progress_updated.connect(on_progress)
    worker.error_occurred.connect(on_error)
    worker.collection_completed.connect(on_completed)

    # 테스트용 심볼 및 날짜 설정
    symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT"]  # OKX 무기한 선물 형식
    start_date = datetime.now() - timedelta(days=3)  # 최근 3일만 테스트

    print(f"[CONFIG] 테스트 설정:")
    print(f"   - 거래소: OKX")
    print(f"   - 심볼: {symbols}")
    print(f"   - 시작일: {start_date}")
    print(f"   - 타임프레임: ['1m', '5m', '15m', '1h', '4h', '1d']")
    print()

    # 데이터 수집 시작
    print("[START] 데이터 수집 시작...")
    worker.backfill_data(symbols, start_date)

    # 애플리케이션 실행
    print("[RUNNING] 애플리케이션 실행 중...")
    app.exec()

    print("[COMPLETE] 테스트 완료")

if __name__ == "__main__":
    test_full_data_collection()