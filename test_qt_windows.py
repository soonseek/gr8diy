# -*- coding: utf-8 -*-
"""
Windows용 Qt 테스트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Windows 플랫폼 명시적으로 설정
os.environ["QT_QPA_PLATFORM"] = "windows"

# Qt 플러그인 경로 설정
def setup_qt():
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
        print(f"Platform exists: {platforms_path.exists()}")

        # Windows에서 필요한 DLL 경로 추가
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(str(pyside6_path))
                os.add_dll_directory(str(platforms_path))
                print("DLL directories added")
            except Exception as e:
                print(f"DLL directory error: {e}")

try:
    print("TEST: 환경 설정")
    setup_qt()
    print(f"QT_QPA_PLATFORM: {os.environ.get('QT_QPA_PLATFORM', 'Not set')}")

    print("TEST: PySide6 임포트 시작")
    from PySide6.QtWidgets import QApplication, QLabel
    from PySide6.QtCore import Qt
    print("TEST: PySide6 임포트 완료")

    def main():
        print("TEST: QApplication 생성 시작")
        app = QApplication(sys.argv)
        print("TEST: QApplication 생성 완료")
        print(f"Application instance: {QApplication.instance()}")

        print("TEST: 레이블 생성")
        label = QLabel("안녕하세요! Gr8 DIY 테스트")
        label.setWindowTitle("Gr8 DIY Qt 테스트")
        label.resize(400, 300)
        label.setAlignment(Qt.AlignCenter)

        print("TEST: 위젯 표시")
        label.show()
        print("TEST: 위젯 표시 완료 - 창이 보여야 합니다!")

        print("TEST: 3초 후 자동 종료")
        # 3초 후 자동 종료 타이머
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.singleShot(3000, app.quit)

        print("TEST: 앱 실행 시작")
        exit_code = app.exec()
        print(f"TEST: 앱 종료, 종료 코드: {exit_code}")
        return exit_code

    if __name__ == "__main__":
        exit_code = main()
        sys.exit(exit_code)

except Exception as e:
    import traceback
    print(f"TEST: 예외 발생: {e}")
    traceback.print_exc()