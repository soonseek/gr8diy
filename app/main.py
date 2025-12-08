"""
OKX Trading Bot - 메인 진입점
"""
import sys
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


def main():
    """앱 실행 함수"""
    print("=" * 60)
    print("OKX Trading Bot 시작")
    print("=" * 60)
    
    # High DPI 지원
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
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

