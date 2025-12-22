#!/usr/bin/env python3
"""
데이터 수집 테스트 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from workers.data_collector_worker import DataCollectorWorker
from PySide6.QtCore import QCoreApplication, QObject
from PySide6.QtWidgets import QApplication
import time

class TestController(QObject):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.app = None

    def test_collection(self):
        """데이터 수집 테스트"""
        print("=== 데이터 수집 테스트 시작 ===")

        # QApplication 생성 (필요)
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        # 워커 생성
        self.worker = DataCollectorWorker()

        # 심볼 및 기간 설정
        symbols = ["BTC-USDT-SWAP"]  # 테스트용 하나의 심볼만
        start_date = datetime.now() - timedelta(days=7)  # 최근 7일
        exchange_id = "okx"

        print(f"테스트 설정:")
        print(f"  - 거래소: {exchange_id}")
        print(f"  - 심볼: {symbols}")
        print(f"  - 기간: {start_date.strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}")

        # 시그널 연결
        self.worker.progress_updated.connect(self.on_progress)
        self.worker.collection_completed.connect(self.on_completed)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.log_message.connect(self.on_log)

        # 수집 시작
        print("\n데이터 수집 시작...")
        self.worker.backfill_data(symbols, start_date, exchange_id)

        # 완료까지 대기
        self.app.processEvents()
        time.sleep(1)  # 간단한 대기

        print("=== 테스트 완료 ===")

    def on_progress(self, message, current, total):
        progress = int((current / total) * 100) if total > 0 else 0
        print(f"[진행률 {progress:3d}%] {message}")

    def on_completed(self):
        print("[완료] 데이터 수집이 완료되었습니다.")

    def on_error(self, error_msg):
        print(f"[에러] {error_msg}")

    def on_log(self, message):
        print(f"[로그] {message}")

if __name__ == "__main__":
    controller = TestController()
    controller.test_collection()