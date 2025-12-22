# -*- coding: utf-8 -*-
"""
최소한의 MainWindow 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    print("TEST: PySide6 임포트 시작")
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
    from PySide6.QtCore import Qt
    print("TEST: PySide6 임포트 완료")

    print("TEST: qfluentwidgets 임포트 시작")
    from qfluentwidgets import FluentIcon
    print("TEST: qfluentwidgets 임포트 완료")

    class MinimalMainWindow(QMainWindow):
        def __init__(self):
            print("TEST: MinimalMainWindow.__init__ 시작")
            super().__init__()
            print("TEST: super().__init__() 완료")

            self.setWindowTitle("테스트 윈도우")
            print("TEST: setWindowTitle 완료")

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            print("TEST: central_widget 설정 완료")

            label = QLabel("테스트 레이블")
            label.setAlignment(Qt.AlignCenter)
            central_widget_layout = QVBoxLayout(central_widget)
            central_widget_layout.addWidget(label)
            print("TEST: UI 설정 완료")

            print("TEST: MinimalMainWindow.__init__ 완료")

    def main():
        print("TEST: QApplication 생성 시작")
        app = QApplication(sys.argv)
        print("TEST: QApplication 생성 완료")

        print("TEST: MainWindow 생성 시작")
        window = MinimalMainWindow()
        print("TEST: MainWindow 생성 완료")

        print("TEST: window.show() 시작")
        window.show()
        print("TEST: window.show() 완료")

        print("TEST: app.exec() 시작")
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()

except Exception as e:
    import traceback
    print(f"TEST: 예외 발생: {e}")
    traceback.print_exc()