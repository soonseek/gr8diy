# -*- coding: utf-8 -*-
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
    
    # ?�경 변???�정
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platforms_path)
    os.environ["QT_PLUGIN_PATH"] = str(plugins_path)
    
    # Windows?�서 DLL 검??경로??추�?
    if sys.platform == "win32":
        # PATH??PySide6 경로 추�?
        pyside6_str = str(pyside6_path)
        current_path = os.environ.get("PATH", "")
        if pyside6_str not in current_path:
            os.environ["PATH"] = pyside6_str + os.pathsep + current_path
        
        # DLL ?�렉?�리 추�? (Python 3.8+)
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
    """?�역 ?�외 ?�들??""
    # 로거가 ?�직 초기?�되지 ?�았???�도 ?�으므�?체크
    if exc_type == KeyboardInterrupt:
        # Ctrl+C???�상 종료
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = f"{exc_type.__name__}: {exc_value}"
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # 로거�??�송 (logger가 import??경우?�만)
    try:
        from utils.logger import logger
        logger.error("System", error_msg, tb_str)
    except:
        pass
    
    # 콘솔?�도 출력 (?�버깅용)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    """???�행 ?�수"""
    print("=" * 60)
    print("Gr8 DIY ?�작")
    print("=" * 60)
    
    # ?�역 ?�외 ?�들???�치
    sys.excepthook = exception_hook
    
    # High DPI ?�정
    # High DPI 지??- QApplication ?�성 ?�에 ?�정?�야 ??
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
        # QApplication ?�성
    app = QApplication(sys.argv)
    print(f"[DEBUG] Step 3: QApplication ?�성 ?�료 - instance: {app}")
    print(f"[DEBUG] Step 3-1: QApplication.instance() = {QApplication.instance()}")
    
    # Qt ?�러그인 경로 추�? (SQL ?�라?�버 ?�을 ?�해)
    from PySide6.QtCore import QCoreApplication
    plugin_path = project_root / "env" / "Lib" / "site-packages" / "PySide6" / "plugins"
    QCoreApplication.addLibraryPath(str(plugin_path))
    print(f"[DEBUG] Step 3-1.5: Qt plugin path added: {plugin_path}")
    
    # QApplication ?�벤??루프 초기??(중요!)
    app.processEvents()
    print("[DEBUG] Step 3-2: QApplication.processEvents() ?�료")
    
    # ?�마 ?�정???�해 qfluentwidgets�??�제 import (QApplication ?�성 ?�후)
    print("[DEBUG] Step 4: qfluentwidgets import ?�작")
    import PySide6
    from PySide6 import QtCore
    from qfluentwidgets import setTheme, Theme, __version__ as qfw_version
    print(f"[DEBUG] PySide6 version: {PySide6.__version__}, QtCore path: {QtCore.__file__}")
    print(f"[DEBUG] qfluentwidgets version: {qfw_version}")
    # Fluent ?�크 ?�마 ?�정 (Gr8 DIY 커스?� ?�마??MainWindow?�서 ?�용)
    setTheme(Theme.DARK)
    print("[DEBUG] Step 4-1: ?�크 ?�마 ?�정 ?�료")
    
    # QApplication ?�성 ??Qt 관??모듈??import
    print("[DEBUG] Step 5: logger import ?�작")
    from utils.logger import logger
    print("[DEBUG] Step 6: logger import ?�료")
    
    print("[DEBUG] Step 7: DatabaseSchema import ?�작")
    from database.schema import DatabaseSchema
    print("[DEBUG] Step 8: DatabaseSchema import ?�료")
    
    print("[DEBUG] Step 9: MainWindow import ?�작")
    from ui.main_window import MainWindow
    print("[DEBUG] Step 10: MainWindow import ?�료")
    
    # ?�이?�베?�스 초기??    logger.info("Main", "?�이?�베?�스 초기??�?..")
    if not DatabaseSchema.init_database(str(DB_PATH)):
        logger.error("Main", "?�이?�베?�스 초기???�패")
        sys.exit(1)
    
    # 메인 ?�도???�성
    logger.info("Main", "메인 ?�도???�성 �?..")
    print("[DEBUG] Step 11: MainWindow() ?�스?�스 ?�성 ?�작")
    window = MainWindow()
    print("[DEBUG] Step 12: MainWindow() ?�스?�스 ?�성 ?�료")
    window.show()
    print("[DEBUG] Step 13: window.show() ?�료")
    
    logger.info("Main", "?�플리�??�션 ?�작 ?�료")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

