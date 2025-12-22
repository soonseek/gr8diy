#!/usr/bin/env python3
"""
데이터 수집 버튼 테스트 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from ui.data_page_simple import DataPageSimple

def test_button_click():
    """데이터 수집 버튼 클릭 테스트"""
    app = QApplication(sys.argv)

    # 데이터 페이지 생성
    data_page = DataPageSimple()

    print("테스트 시작: 데이터 수집 버튼 클릭")

    # 버튼 상태 확인
    print(f"버튼 활성화 상태: {data_page.collect_button.isEnabled()}")
    print(f"버튼 텍스트: '{data_page.collect_button.text()}'")

    # 심볼 선택 상태 확인
    selected_symbols = data_page.selected_symbols
    print(f"선택된 심볼 수: {len(selected_symbols)}")
    print(f"선택된 심볼: {list(selected_symbols)[:5]}...")  # 처음 5개만 표시

    # 강제로 버튼 클릭 시뮬레이션
    print("\n버튼 클릭 시뮬레이션...")
    data_page.start_data_collection()

    print("테스트 완료")

if __name__ == "__main__":
    test_button_click()