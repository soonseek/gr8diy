"""
Gr8 DIY - 커스텀 테마 시스템
다크모드 + 네온 그린-블루 그라디언트
"""

class Gr8Theme:
    """Gr8 DIY 커스텀 테마 색상 팔레트"""
    
    # === 배경색 ===
    BG_DARK = "#0a0e27"           # 메인 배경 (진한 네이비)
    BG_SECONDARY = "#1a1f3a"      # 카드/패널 배경
    BG_TERTIARY = "#252b4a"       # 호버 배경
    BG_INPUT = "#1e2338"          # 입력 필드 배경
    
    # === 네온 포인트 컬러 ===
    NEON_GREEN = "#00ff9f"        # 형광 그린 (주 포인트)
    NEON_BLUE = "#00d4ff"         # 사이버 블루 (보조 포인트)
    NEON_PURPLE = "#b744ff"       # 네온 퍼플 (악센트)
    
    # === 그라디언트 ===
    GRADIENT_PRIMARY = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ff9f, stop:1 #00d4ff)"
    GRADIENT_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ffb3, stop:1 #00e0ff)"
    GRADIENT_PRESSED = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00cc7f, stop:1 #00a8cc)"
    
    # === 텍스트 색상 ===
    TEXT_PRIMARY = "#e8e8e8"      # 메인 텍스트
    TEXT_SECONDARY = "#a0a0a0"    # 보조 텍스트
    TEXT_DISABLED = "#606060"     # 비활성 텍스트
    TEXT_ON_ACCENT = "#0a0e27"    # 강조색 위 텍스트 (어두운 배경)
    
    # === 보더/구분선 ===
    BORDER_DEFAULT = "#2a3050"    # 기본 보더
    BORDER_FOCUS = "#00ff9f"      # 포커스 보더 (네온 그린)
    BORDER_HOVER = "#00d4ff"      # 호버 보더 (사이버 블루)
    
    # === 상태 색상 ===
    SUCCESS = "#00ff9f"           # 성공 (그린)
    WARNING = "#ffaa00"           # 경고 (오렌지)
    ERROR = "#ff4444"             # 에러 (레드)
    INFO = "#00d4ff"              # 정보 (블루)
    
    # === 그림자 ===
    SHADOW_LIGHT = "rgba(0, 255, 159, 0.2)"   # 그린 글로우
    SHADOW_MEDIUM = "rgba(0, 212, 255, 0.3)"  # 블루 글로우
    SHADOW_DARK = "rgba(0, 0, 0, 0.5)"        # 일반 그림자


def get_custom_stylesheet():
    """Gr8 DIY 커스텀 스타일시트 반환"""
    
    return f"""
    /* ===== 전역 설정 ===== */
    * {{
        font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
        font-size: 14px;
    }}
    
    /* ===== 메인 윈도우 ===== */
    QMainWindow {{
        background-color: {Gr8Theme.BG_DARK};
        color: {Gr8Theme.TEXT_PRIMARY};
    }}
    
    /* ===== 기본 위젯 ===== */
    QWidget {{
        background-color: transparent;
        color: {Gr8Theme.TEXT_PRIMARY};
    }}
    
    /* ===== 카드/패널 (CardWidget) ===== */
    CardWidget, QFrame {{
        background-color: {Gr8Theme.BG_SECONDARY};
        border: 1px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 12px;
    }}
    
    /* ===== 버튼 ===== */
    PushButton, QPushButton {{
        background: {Gr8Theme.GRADIENT_PRIMARY};
        color: {Gr8Theme.TEXT_ON_ACCENT};
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        font-size: 14px;
        min-height: 36px;
    }}
    
    PushButton:hover, QPushButton:hover {{
        background: {Gr8Theme.GRADIENT_HOVER};
    }}
    
    PushButton:pressed, QPushButton:pressed {{
        background: {Gr8Theme.GRADIENT_PRESSED};
        padding: 11px 23px 9px 25px;
    }}
    
    PushButton:disabled, QPushButton:disabled {{
        background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.TEXT_DISABLED};
    }}
    
    /* ===== 보조 버튼 (아웃라인) ===== */
    QPushButton[secondary="true"] {{
        background-color: transparent;
        color: {Gr8Theme.NEON_GREEN};
        border: 2px solid {Gr8Theme.NEON_GREEN};
    }}
    
    QPushButton[secondary="true"]:hover {{
        background-color: {Gr8Theme.NEON_GREEN};
        color: {Gr8Theme.TEXT_ON_ACCENT};
    }}
    
    /* ===== 입력 필드 ===== */
    LineEdit, QLineEdit, QTextEdit {{
        background-color: {Gr8Theme.BG_INPUT};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 10px 16px;
        selection-background-color: {Gr8Theme.NEON_BLUE};
        selection-color: {Gr8Theme.TEXT_ON_ACCENT};
    }}
    
    LineEdit:focus, QLineEdit:focus, QTextEdit:focus {{
        border: 2px solid {Gr8Theme.BORDER_FOCUS};
    }}
    
    LineEdit:hover, QLineEdit:hover, QTextEdit:hover {{
        border-color: {Gr8Theme.BORDER_HOVER};
    }}
    
    /* ===== 비밀번호 입력 ===== */
    PasswordLineEdit {{
        background-color: {Gr8Theme.BG_INPUT};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 10px 16px;
    }}
    
    PasswordLineEdit:focus {{
        border: 2px solid {Gr8Theme.BORDER_FOCUS};
    }}
    
    /* ===== 콤보박스 ===== */
    ComboBox, QComboBox {{
        background-color: {Gr8Theme.BG_INPUT};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 8px 16px;
        min-height: 40px;
    }}
    
    /* ===== DateEdit (DatePicker) ===== */
    QDateEdit {{
        background-color: {Gr8Theme.BG_INPUT};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 8px 16px;
        min-height: 40px;
    }}
    
    QDateEdit:hover {{
        border-color: {Gr8Theme.BORDER_HOVER};
    }}
    
    QDateEdit:focus {{
        border-color: {Gr8Theme.BORDER_FOCUS};
    }}
    
    QDateEdit::drop-down {{
        border: none;
        width: 30px;
    }}
    
    QDateEdit::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {Gr8Theme.NEON_GREEN};
        margin-right: 8px;
    }}
    
    ComboBox:hover, QComboBox:hover {{
        border-color: {Gr8Theme.BORDER_HOVER};
    }}
    
    ComboBox:focus, QComboBox:focus {{
        border-color: {Gr8Theme.BORDER_FOCUS};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {Gr8Theme.NEON_GREEN};
        margin-right: 8px;
    }}
    
    /* ===== 스핀박스 ===== */
    SpinBox, QSpinBox, DoubleSpinBox, QDoubleSpinBox {{
        background-color: {Gr8Theme.BG_INPUT};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 36px;
    }}
    
    SpinBox:focus, QSpinBox:focus, DoubleSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {Gr8Theme.BORDER_FOCUS};
    }}
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background-color: {Gr8Theme.NEON_GREEN};
        border-radius: 4px;
        margin: 2px;
    }}
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: {Gr8Theme.NEON_BLUE};
        border-radius: 4px;
        margin: 2px;
    }}
    
    /* ===== 체크박스 ===== */
    CheckBox, QCheckBox {{
        color: {Gr8Theme.TEXT_PRIMARY};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 4px;
        background-color: {Gr8Theme.BG_INPUT};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {Gr8Theme.BORDER_HOVER};
    }}
    
    QCheckBox::indicator:checked {{
        background: {Gr8Theme.GRADIENT_PRIMARY};
        border-color: {Gr8Theme.NEON_GREEN};
    }}
    
    /* ===== 스위치 버튼 ===== */
    SwitchButton {{
        background-color: {Gr8Theme.BG_TERTIARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
    }}
    
    SwitchButton:checked {{
        background: {Gr8Theme.GRADIENT_PRIMARY};
        border-color: {Gr8Theme.NEON_GREEN};
    }}
    
    /* ===== 테이블 ===== */
    QTableWidget {{
        background-color: {Gr8Theme.BG_SECONDARY};
        alternate-background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.TEXT_PRIMARY};
        gridline-color: {Gr8Theme.BORDER_DEFAULT};
        border: 1px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        selection-background-color: {Gr8Theme.NEON_BLUE};
        selection-color: {Gr8Theme.TEXT_ON_ACCENT};
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {Gr8Theme.BORDER_DEFAULT};
    }}
    
    QTableWidget::item:hover {{
        background-color: {Gr8Theme.BG_TERTIARY};
    }}
    
    QHeaderView::section {{
        background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.TEXT_PRIMARY};
        padding: 14px 10px;
        min-height: 45px;
        border: none;
        border-bottom: 2px solid {Gr8Theme.NEON_GREEN};
        font-weight: bold;
        font-size: 13px;
    }}
    
    QHeaderView {{
        min-height: 45px;
    }}
    
    /* ===== 스크롤바 ===== */
    QScrollBar:vertical {{
        background-color: {Gr8Theme.BG_SECONDARY};
        width: 10px;
        border-radius: 5px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {Gr8Theme.BG_TERTIARY};
        border: 1px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 5px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {Gr8Theme.BORDER_HOVER};
        border-color: {Gr8Theme.NEON_BLUE};
    }}
    
    QScrollBar:horizontal {{
        background-color: {Gr8Theme.BG_SECONDARY};
        height: 10px;
        border-radius: 5px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {Gr8Theme.BG_TERTIARY};
        border: 1px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 5px;
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {Gr8Theme.BORDER_HOVER};
        border-color: {Gr8Theme.NEON_BLUE};
    }}
    
    QScrollBar::add-line, QScrollBar::sub-line {{
        border: none;
        background: none;
    }}
    
    /* ===== 타이틀 라벨 ===== */
    TitleLabel {{
        color: {Gr8Theme.TEXT_PRIMARY};
        font-size: 24px;
        font-weight: bold;
        padding: 8px 0;
    }}
    
    SubtitleLabel {{
        color: {Gr8Theme.NEON_GREEN};
        font-size: 18px;
        font-weight: bold;
        padding: 6px 0;
    }}
    
    BodyLabel {{
        color: {Gr8Theme.TEXT_SECONDARY};
        font-size: 14px;
    }}
    
    /* ===== Progress Bar ===== */
    QProgressBar {{
        background-color: {Gr8Theme.BG_INPUT};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        height: 24px;
        text-align: center;
        color: {Gr8Theme.TEXT_PRIMARY};
    }}
    
    QProgressBar::chunk {{
        background: {Gr8Theme.GRADIENT_PRIMARY};
        border-radius: 6px;
    }}
    
    /* ===== 탭 (Pivot) ===== */
    Pivot {{
        background-color: {Gr8Theme.BG_SECONDARY};
        border-bottom: 3px solid {Gr8Theme.BORDER_DEFAULT};
        padding: 5px 0;
    }}
    
    Pivot > QPushButton {{
        color: {Gr8Theme.TEXT_SECONDARY};
        background-color: {Gr8Theme.BG_DARK};
        border: 1px solid {Gr8Theme.BORDER_DEFAULT};
        border-bottom: 3px solid {Gr8Theme.BORDER_DEFAULT};
        padding: 12px 20px;
        margin: 2px 4px;
        margin-bottom: -3px;
        font-size: 14px;
        min-width: 100px;
        border-radius: 8px 8px 0 0;
    }}
    
    Pivot > QPushButton:hover {{
        color: {Gr8Theme.NEON_BLUE};
        background-color: {Gr8Theme.BG_TERTIARY};
        border-color: {Gr8Theme.NEON_BLUE};
    }}
    
    Pivot > QPushButton:checked {{
        color: {Gr8Theme.NEON_GREEN};
        background-color: {Gr8Theme.BG_SECONDARY};
        border: 1px solid {Gr8Theme.NEON_GREEN};
        border-bottom: 3px solid {Gr8Theme.NEON_GREEN};
        font-weight: bold;
    }}
    
    /* ===== 툴팁 ===== */
    QToolTip {{
        background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 1px solid {Gr8Theme.NEON_GREEN};
        border-radius: 6px;
        padding: 8px 12px;
    }}
    
    /* ===== InfoBar (알림) ===== */
    InfoBar {{
        background-color: {Gr8Theme.BG_SECONDARY};
        border-left: 4px solid {Gr8Theme.NEON_GREEN};
        border-radius: 8px;
        padding: 16px;
    }}
    
    /* ===== 네비게이션 ===== */
    NavigationInterface {{
        background-color: {Gr8Theme.BG_SECONDARY};
        border-right: 1px solid {Gr8Theme.BORDER_DEFAULT};
        min-width: 75px;
    }}
    
    NavigationInterface::item {{
        color: {Gr8Theme.TEXT_SECONDARY};
        padding: 12px 16px;
        margin: 4px 8px;
        border-radius: 8px;
    }}
    
    NavigationInterface::item:hover {{
        background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.NEON_BLUE};
    }}
    
    NavigationInterface::item:selected {{
        background: {Gr8Theme.GRADIENT_PRIMARY};
        color: {Gr8Theme.TEXT_ON_ACCENT};
        font-weight: bold;
    }}
    
    /* ===== 스플리터 ===== */
    QSplitter::handle {{
        background-color: {Gr8Theme.BORDER_DEFAULT};
        width: 2px;
        margin: 0;
    }}
    
    QSplitter::handle:hover {{
        background-color: {Gr8Theme.NEON_BLUE};
    }}
    
    QSplitter::handle:pressed {{
        background-color: {Gr8Theme.NEON_GREEN};
    }}
    """


def apply_theme_to_widget(widget):
    """위젯에 커스텀 테마 적용"""
    widget.setStyleSheet(get_custom_stylesheet())

