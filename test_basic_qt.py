# -*- coding: utf-8 -*-
"""
가장 기본적인 Qt 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Qt 플러그인 경로 설정
def setup_qt():
    import os
    import importlib.util

    # PySide6 설치 경로 찾기
    spec = importlib.util.find_spec("PySide6")
    if spec and spec.origin:
        pyside6_path = Path(spec.origin).parent
    else:
        pyside6_path = project_root / "env" / "Lib" / "site-packages" / "PySide6"

    plugins_path = pyside6_path / "plugins"
    platforms_path = plugins_path / "platforms"

    if platforms_path.exists():
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platforms_path)
        os.environ["QT_PLUGIN_PATH"] = str(plugins_path)
        print(f"Qt plugin path set: {platforms_path}")

try:
    print("TEST: Qt 플러그인 설정")
    setup_qt()

    print("TEST: PySide6 임포트 시작")
    from PySide6.QtWidgets import QApplication, QLabel, QWidget
    from PySide6.QtCore import Qt
    print("TEST: PySide6 임포트 완료")

    def main():
        print("TEST: QApplication 생성 시작")
        app = QApplication(sys.argv)
        print("TEST: QApplication 생성 완료")

        print("TEST: 간단한 위젯 생성")
        widget = QWidget()
        widget.setWindowTitle("간단한 테스트")
        widget.resize(300, 200)

        label = QLabel("안녕하세요!", widget)
        label.setAlignment(Qt.AlignCenter)
        widget.show()
        print("TEST: 위젯 표시 완료")

        print("TEST: 앱 실행 - 창이 보여야 합니다!")
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()

except Exception as e:
    import traceback
    print(f"TEST: 예외 발생: {e}")
    traceback.print_exc()