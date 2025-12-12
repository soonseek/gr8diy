"""
OKX Trading Bot - 메인 진입점
"""
import sys
import os
import traceback
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Qt 플러그인 경로 설정 (QApplication 생성 전에 설정해야 함!)
def _setup_qt_plugin_path():
    """Qt 플러그인 경로를 Windows 환경에 맞게 설정"""
    import importlib.util
    
    # PySide6 설치 경로 찾기
    spec = importlib.util.find_spec("PySide6")
    if spec and spec.origin:
        pyside6_path = Path(spec.origin).parent
    else:
        pyside6_path = project_root / "env" / "Lib" / "site-packages" / "PySide6"
    
    plugins_path = pyside6_path / "plugins"
    platforms_path = plugins_path / "platforms"
    
    if not platforms_path.exists():
        print(f"[ERROR] Qt plugins path not found: {platforms_path}")
        return False
    
    # 환경 변수 설정
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platforms_path)
    os.environ["QT_PLUGIN_PATH"] = str(plugins_path)
    
    # Windows에서 DLL 검색 경로에 추가
    if sys.platform == "win32":
        # PATH에 PySide6 경로 추가
        pyside6_str = str(pyside6_path)
        current_path = os.environ.get("PATH", "")
        if pyside6_str not in current_path:
            os.environ["PATH"] = pyside6_str + os.pathsep + current_path
        
        # DLL 디렉토리 추가 (Python 3.8+)
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(pyside6_str)
                os.add_dll_directory(str(platforms_path))
            except Exception:
                pass
    
    print(f"[DEBUG] Qt plugin path set: {platforms_path}")
    return True

_setup_qt_plugin_path()

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from config.settings import DB_PATH


def exception_hook(exc_type, exc_value, exc_traceback):
    """전역 예외 핸들러"""
    # 로거가 아직 초기화되지 않았을 수도 있으므로 체크
    if exc_type == KeyboardInterrupt:
        # Ctrl+C는 정상 종료
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = f"{exc_type.__name__}: {exc_value}"
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # 로거로 전송 (logger가 import된 경우에만)
    try:
        from utils.logger import logger
        logger.error("System", error_msg, tb_str)
    except:
        pass
    
    # 콘솔에도 출력 (디버깅용)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    """앱 실행 함수"""
    print("=" * 60)
    print("Gr8 DIY 시작")
    print("=" * 60)
    
    # 전역 예외 핸들러 설치
    sys.excepthook = exception_hook
    
    print("[DEBUG] Step 1: High DPI 설정 (QApplication 생성 전)")
    # High DPI 지원 - QApplication 생성 전에 설정해야 함!
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    print("[DEBUG] Step 2: QApplication 생성 시작")
    # QApplication 생성
    app = QApplication(sys.argv)
    print(f"[DEBUG] Step 3: QApplication 생성 완료 - instance: {app}")
    print(f"[DEBUG] Step 3-1: QApplication.instance() = {QApplication.instance()}")
    
    # Qt 플러그인 경로 추가 (SQL 드라이버 등을 위해)
    from PySide6.QtCore import QCoreApplication
    plugin_path = project_root / "env" / "Lib" / "site-packages" / "PySide6" / "plugins"
    QCoreApplication.addLibraryPath(str(plugin_path))
    print(f"[DEBUG] Step 3-1.5: Qt plugin path added: {plugin_path}")
    
    # QApplication 이벤트 루프 초기화 (중요!)
    app.processEvents()
    print("[DEBUG] Step 3-2: QApplication.processEvents() 완료")
    
    # 테마 설정을 위해 qfluentwidgets를 이제 import (QApplication 생성 이후)
    print("[DEBUG] Step 4: qfluentwidgets import 시작")
    import PySide6
    from PySide6 import QtCore
    from qfluentwidgets import setTheme, Theme, __version__ as qfw_version
    print(f"[DEBUG] PySide6 version: {PySide6.__version__}, QtCore path: {QtCore.__file__}")
    print(f"[DEBUG] qfluentwidgets version: {qfw_version}")
    # Fluent 다크 테마 설정 (Gr8 DIY 커스텀 테마는 MainWindow에서 적용)
    setTheme(Theme.DARK)
    print("[DEBUG] Step 4-1: 다크 테마 설정 완료")
    
    # QApplication 생성 후 Qt 관련 모듈들 import
    print("[DEBUG] Step 5: logger import 시작")
    from utils.logger import logger
    print("[DEBUG] Step 6: logger import 완료")
    
    print("[DEBUG] Step 7: DatabaseSchema import 시작")
    from database.schema import DatabaseSchema
    print("[DEBUG] Step 8: DatabaseSchema import 완료")
    
    print("[DEBUG] Step 9: MainWindow import 시작")
    from ui.main_window import MainWindow
    print("[DEBUG] Step 10: MainWindow import 완료")
    
    # 데이터베이스 초기화
    logger.info("Main", "데이터베이스 초기화 중...")
    if not DatabaseSchema.init_database(str(DB_PATH)):
        logger.error("Main", "데이터베이스 초기화 실패")
        sys.exit(1)
    
    # 메인 윈도우 생성
    logger.info("Main", "메인 윈도우 생성 중...")
    print("[DEBUG] Step 11: MainWindow() 인스턴스 생성 시작")
    window = MainWindow()
    print("[DEBUG] Step 12: MainWindow() 인스턴스 생성 완료")
    window.show()
    print("[DEBUG] Step 13: window.show() 완료")
    
    logger.info("Main", "애플리케이션 시작 완료")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

