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

# Python 정보 디버그 출력
print(f"DEBUG: Python executable: {sys.executable}")
print(f"DEBUG: Python version: {sys.version}")
print(f"DEBUG: Project root: {project_root}")

# Qt 플러그인 경로 설정 (QApplication 생성 전에 설정해야 함!)
def _setup_qt_plugin_path():
    """Qt 플러그인 경로를 Windows 환경에 맞게 설정"""
    import importlib.util

    # Windows 플랫폼 명시적으로 설정
    os.environ["QT_QPA_PLATFORM"] = "windows"

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
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(pyside6_str)
                os.add_dll_directory(str(platforms_path))
            except Exception:
                pass

    return True

def exception_hook(exctype, value, tb):
    """전역 예외 핸들러"""
    if exctype == KeyboardInterrupt:
        sys.__excepthook__(exctype, value, tb)
        return

    # UnicodeDecodeError는 QFluentWidgets 메시지에서 자주 발생하므로 안전하게 처리
    if exctype == UnicodeDecodeError:
        print(f"\n[WARNING] UnicodeDecodeError: {value}")
        print("[WARNING] This is usually harmless and can be ignored")
        return

    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    try:
        # 안전한 인코딩으로 에러 메시지 출력
        safe_msg = error_msg.encode('ascii', 'ignore').decode('ascii')
        print(f"\n[ERROR] Unhandled exception: {exctype.__name__}: {value}")
        print(f"[ERROR] Traceback:\n{safe_msg}")
    except:
        print(f"\n[ERROR] Unhandled exception: {exctype.__name__}: {value}")

    # 로거가 이미 초기화된 경우에만 로깅
    try:
        from utils.logger import logger
        logger.error("System", f"Unhandled exception: {exctype.__name__}", value)
    except:
        pass

def main():
    """메인 실행 함수"""
    # 콘솔 인코딩 설정 (UTF-8)
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    print("Gr8 DIY 시작")

    # 전역 예외 핸들러 설치
    sys.excepthook = exception_hook

    # Qt 플러그인 경로 설정 (QApplication 생성 전에 설정해야 함!)
    if not _setup_qt_plugin_path():
        print("[ERROR] Failed to setup Qt plugin paths")
        return

    # High DPI 설정
    # High DPI 지원 - QApplication 생성 전에 설정해야 함!
    from PySide6.QtCore import Qt, QCoreApplication
    from PySide6.QtWidgets import QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # QApplication 생성
    app = QApplication(sys.argv)

    # Qt 플러그인 경로 추가 (SQL 드라이버 등을 위해)
    import importlib.util
    spec = importlib.util.find_spec("PySide6")
    if spec and spec.origin:
        pyside6_path = Path(spec.origin).parent
    else:
        pyside6_path = project_root / "env" / "Lib" / "site-packages" / "PySide6"

    plugin_path = pyside6_path / "plugins"
    platforms_path = plugin_path / "platforms"

    # 라이브러리 경로와 환경 변수 모두 설정
    QCoreApplication.addLibraryPath(str(plugin_path))
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platforms_path)
    os.environ["QT_PLUGIN_PATH"] = str(plugin_path)

    print(f"DEBUG: Plugin path added: {plugin_path}")
    print(f"DEBUG: Platforms path: {platforms_path}")
    print(f"DEBUG: Plugin path exists: {plugin_path.exists()}")
    print(f"DEBUG: Platforms path exists: {platforms_path.exists()}")

    # Windows DLL 경로 추가
    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(str(pyside6_path))
            os.add_dll_directory(str(plugin_path))
            os.add_dll_directory(str(platforms_path))
            print("DEBUG: DLL directories added")
        except Exception as e:
            print(f"DEBUG: DLL directory error: {e}")

    # QApplication 이벤트 루프 초기화 (중요!)
    app.processEvents()

    # 테마 설정을 위해 qfluentwidgets를 이제 import (QApplication 생성 이후)
    print("DEBUG: Importing qfluentwidgets...")
    try:
        import PySide6
        from PySide6 import QtCore
        from qfluentwidgets import setTheme, Theme
        # Fluent 다크 테마 설정 (Gr8 DIY 커스텀 테마는 MainWindow에서 적용)
        setTheme(Theme.DARK)
        print("DEBUG: qfluentwidgets theme set successfully")
    except Exception as e:
        print(f"DEBUG: qfluentwidgets error: {e}")

    # QApplication 생성 후 Qt 관련 모듈들 import
    print("DEBUG: Importing logger...")
    try:
        from utils.logger import logger
        print("DEBUG: Logger imported successfully")
    except Exception as e:
        print(f"DEBUG: Logger error: {e}")
        logger = None

    print("DEBUG: Importing database schema...")
    try:
        from database.schema import DatabaseSchema
        print("DEBUG: Database schema imported successfully")
    except Exception as e:
        print(f"DEBUG: Database schema error: {e}")

    print("DEBUG: Importing main window...")
    MainWindow = None
    try:
        from ui.main_window import MainWindow
        print("DEBUG: Main window imported successfully")
    except Exception as e:
        print(f"DEBUG: Main window error: {e}")
        traceback.print_exc()
        print(f"[ERROR] Failed to import MainWindow: {e}")
        return

    # 데이터베이스 초기화
    print("DEBUG: Initializing database...")
    try:
        if logger:
            logger.info("Main", "데이터베이스 초기화 중...")
        db_path = project_root / "database" / "trading_bot.db"
        if not DatabaseSchema.init_database(str(db_path)):
            if logger:
                logger.error("Main", "데이터베이스 초기화 실패")
            print("[ERROR] Database initialization failed")
            sys.exit(1)
        print("DEBUG: Database initialized successfully")
    except Exception as e:
        print(f"DEBUG: Database initialization error: {e}")
        traceback.print_exc()

    # 메인 윈도우 생성
    print("DEBUG: Creating main window...")
    try:
        if logger:
            logger.info("Main", "메인 윈도우 생성 중...")
        window = MainWindow()
        print("DEBUG: MainWindow instance created")

        window.show()
        print("DEBUG: window.show() called")

        if logger:
            logger.info("Main", "애플리케이션 시작 완료")
        print("DEBUG: All imports and setup completed successfully")
    except Exception as e:
        print(f"DEBUG: Main window creation error: {e}")
        traceback.print_exc()

        print(f"[ERROR] Failed to create main window: {e}")
        return

    # 메인 루프 실행
    print("DEBUG: Starting application main loop...")
    try:
        print("DEBUG: Entering app.exec()")
        sys.exit(app.exec())
    except Exception as e:
        print(f"DEBUG: Main loop error: {e}")
        traceback.print_exc()
        print(f"[ERROR] Application main loop failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()