"""
OKX Trading Bot - 메인 진입점
"""
import sys
import traceback
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qfluentwidgets import setTheme, Theme

from ui.main_window import MainWindow
from database.schema import DatabaseSchema
from config.settings import DB_PATH
from utils.logger import logger


def exception_hook(exc_type, exc_value, exc_traceback):
    """전역 예외 핸들러"""
    # 로거가 아직 초기화되지 않았을 수도 있으므로 체크
    if exc_type == KeyboardInterrupt:
        # Ctrl+C는 정상 종료
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = f"{exc_type.__name__}: {exc_value}"
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # 로거로 전송
    logger.error("System", error_msg, tb_str)
    
    # 콘솔에도 출력 (디버깅용)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    """앱 실행 함수"""
    print("=" * 60)
    print("OKX Trading Bot 시작")
    print("=" * 60)
    
    # 전역 예외 핸들러 설치
    sys.excepthook = exception_hook
    
    # High DPI 지원 (PySide6/Qt6에서는 기본 활성화되므로 제거)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # 테마 설정
    setTheme(Theme.AUTO)
    
    # 데이터베이스 초기화
    logger.info("Main", "데이터베이스 초기화 중...")
    if not DatabaseSchema.init_database(str(DB_PATH)):
        logger.error("Main", "데이터베이스 초기화 실패")
        sys.exit(1)
    
    # 메인 윈도우 생성
    logger.info("Main", "메인 윈도우 생성 중...")
    window = MainWindow()
    window.show()
    
    logger.info("Main", "애플리케이션 시작 완료")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

