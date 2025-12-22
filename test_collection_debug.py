#!/usr/bin/env python3
"""
데이터 수집 기능 간단 테스트
"""
import sys
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# 프로젝트 모듈 경로 추가
sys.path.insert(0, '.')
sys.path.insert(0, './ui')

from ui.data_page import DataPage
from utils.time_helper import time_helper

def test_data_collection():
    """데이터 수집 테스트"""
    app = QApplication(sys.argv)

    # 데이터 페이지 생성
    page = DataPage()
    page.show()

    print("="*60)
    print("데이터 수집 테스트 시작")
    print("="*60)

    # 2초 후에 자동으로 수집 시작
    def auto_start_collection():
        print("\n[TEST] 2초 후 자동 수집 시작...")

        # 기본 설정 확인
        print(f"[TEST] 현재 거래소 ID: {page.exchange_id}")
        print(f"[TEST] 활성화된 심볼: {page.symbols_repo.get_active_symbols(page.exchange_id)}")

        # 수집 시작 버튼 클릭 시뮬레이션
        try:
            page._start_collection()
            print("[TEST] 수집 시작 메서드 호출 완료")
        except Exception as e:
            print(f"[TEST ERROR] 수집 시작 실패: {e}")
            import traceback
            traceback.print_exc()

    # 5초 후에 애플리케이션 종료
    def auto_exit():
        print("\n[TEST] 5초 후 애플리케이션 종료...")
        app.quit()

    # 타이머 설정
    QTimer.singleShot(2000, auto_start_collection)  # 2초 후 수집 시작
    QTimer.singleShot(7000, auto_exit)  # 7초 후 종료

    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    test_data_collection()