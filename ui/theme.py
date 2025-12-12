"""
Gr8 DIY - 커스텀 테마 시스템
"""

class Gr8Theme:
    """Gr8 DIY 커스텀 테마 색상 팔레트"""
    
    # === 배경색 ===
    BG_DARK = "#0a0e27"
    BG_SECONDARY = "#1a1f3a"
    BG_TERTIARY = "#252b4a"
    BG_INPUT = "#1e2338"
    
    # === 네온 포인트 컬러 ===
    NEON_GREEN = "#00ff9f"
    NEON_BLUE = "#00d4ff"
    NEON_PURPLE = "#b744ff"
    
    # === 그라디언트 ===
    GRADIENT_PRIMARY = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ff9f, stop:1 #00d4ff)"
    GRADIENT_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ffb3, stop:1 #00e0ff)"
    GRADIENT_PRESSED = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00cc7f, stop:1 #00a8cc)"
    
    # === 텍스트 색상 ===
    TEXT_PRIMARY = "#e8e8e8"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_DISABLED = "#606060"
    TEXT_ON_ACCENT = "#0a0e27"
    
    # === 보더/구분선 (밝게!) ===
    BORDER_DEFAULT = "#6a7090"
    BORDER_FOCUS = "#00ff9f"
    BORDER_HOVER = "#00d4ff"
    
    # === 상태 색상 ===
    SUCCESS = "#00ff9f"
    WARNING = "#ffaa00"
    ERROR = "#ff4444"
    INFO = "#00d4ff"


def get_custom_stylesheet():
    """Gr8 DIY 커스텀 스타일시트 반환"""
    
    return f"""
    /* ===== 전역 설정 ===== */
    * {{
        font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
        font-size: 13px;
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
    
    /* ===== 카드/패널 ===== */
    CardWidget {{
        background-color: {Gr8Theme.BG_SECONDARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 12px;
    }}
    
    QFrame {{
        background: transparent;
        border: none;
    }}
    
    /* ===== 버튼 (포인트 컬러!) ===== */
    PushButton, QPushButton {{
        background-color: {Gr8Theme.NEON_GREEN};
        color: {Gr8Theme.TEXT_ON_ACCENT};
        border: 2px solid {Gr8Theme.NEON_GREEN};
        border-radius: 5px;
        padding: 6px 14px;
        font-weight: bold;
        font-size: 13px;
    }}
    
    PushButton:hover, QPushButton:hover {{
        background-color: {Gr8Theme.NEON_BLUE};
        border-color: {Gr8Theme.NEON_BLUE};
    }}
    
    PushButton:pressed, QPushButton:pressed {{
        background-color: #00aa6f;
        border-color: #00aa6f;
    }}
    
    PushButton:disabled, QPushButton:disabled {{
        background-color: {Gr8Theme.BG_TERTIARY};
        border-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.TEXT_DISABLED};
    }}
    
    /* ===== 입력 필드 ===== */
    LineEdit, QLineEdit, QTextEdit {{
        background-color: {Gr8Theme.BG_INPUT};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 5px;
        padding: 6px 10px;
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
        border-radius: 5px;
        padding: 6px 10px;
    }}
    
    PasswordLineEdit:focus {{
        border: 2px solid {Gr8Theme.BORDER_FOCUS};
    }}
    
    /* ===== 콤보박스/드롭다운 ===== */
    ComboBox, ComboBox > QComboBox {{
        background-color: {Gr8Theme.BG_INPUT} !important;
        color: {Gr8Theme.TEXT_PRIMARY} !important;
        border: 3px solid {Gr8Theme.NEON_GREEN} !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        padding-right: 38px !important;
        min-height: 32px !important;
        font-size: 13px !important;
    }}
    
    ComboBox:hover, ComboBox > QComboBox:hover {{
        border: 3px solid {Gr8Theme.NEON_BLUE} !important;
        background-color: {Gr8Theme.BG_SECONDARY} !important;
    }}
    
    QComboBox {{
        background-color: {Gr8Theme.BG_INPUT} !important;
        color: {Gr8Theme.TEXT_PRIMARY} !important;
        border: 3px solid {Gr8Theme.NEON_GREEN} !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        padding-right: 38px !important;
        min-height: 32px !important;
        font-size: 13px !important;
    }}
    
    QComboBox:hover {{
        border: 3px solid {Gr8Theme.NEON_BLUE} !important;
        background-color: {Gr8Theme.BG_SECONDARY} !important;
    }}
    
    ComboBox::drop-down, ComboBox > QComboBox::drop-down, QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: right center;
        border: none;
        border-left: 2px solid {Gr8Theme.BG_DARK};
        width: 32px;
        background-color: {Gr8Theme.NEON_GREEN} !important;
        border-radius: 0 4px 4px 0;
    }}
    
    ComboBox::down-arrow, ComboBox > QComboBox::down-arrow, QComboBox::down-arrow {{
        image: none;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 8px solid {Gr8Theme.TEXT_ON_ACCENT};
    }}
    
    /* ===== DateEdit ===== */
    QDateEdit {{
        background-color: {Gr8Theme.BG_INPUT};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 5px;
        padding: 4px 8px;
        font-size: 13px;
    }}
    
    QDateEdit:hover {{
        border-color: {Gr8Theme.NEON_BLUE};
    }}
    
    QDateEdit:focus {{
        border-color: {Gr8Theme.NEON_GREEN};
    }}
    
    QDateEdit::drop-down {{
        border: none;
        width: 24px;
        background-color: {Gr8Theme.NEON_GREEN};
        border-radius: 0 3px 3px 0;
    }}
    
    QDateEdit::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {Gr8Theme.TEXT_ON_ACCENT};
    }}
    
    /* ===== 스핀박스 ===== */
    SpinBox, QSpinBox, DoubleSpinBox, QDoubleSpinBox {{
        background-color: {Gr8Theme.BG_INPUT};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 5px;
        padding: 5px 10px;
        padding-right: 25px;
        font-size: 13px;
    }}
    
    SpinBox:focus, QSpinBox:focus, DoubleSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {Gr8Theme.NEON_GREEN};
    }}
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: right;
        background-color: {Gr8Theme.NEON_GREEN};
        border-radius: 2px;
        width: 20px;
        margin: 2px;
    }}
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: right;
        background-color: {Gr8Theme.NEON_BLUE};
        border-radius: 2px;
        width: 20px;
        margin: 2px;
    }}
    
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid {Gr8Theme.TEXT_ON_ACCENT};
    }}
    
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {Gr8Theme.TEXT_ON_ACCENT};
    }}
    
    /* ===== 체크박스 ===== */
    CheckBox, QCheckBox {{
        color: {Gr8Theme.TEXT_PRIMARY};
        spacing: 6px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 3px;
        background-color: {Gr8Theme.BG_INPUT};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {Gr8Theme.NEON_BLUE};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {Gr8Theme.NEON_GREEN};
        border-color: {Gr8Theme.NEON_GREEN};
    }}
    
    /* ===== 스위치 버튼 ===== */
    SwitchButton {{
        background-color: {Gr8Theme.BG_TERTIARY};
        border: none;
    }}
    
    SwitchButton:checked {{
        background-color: {Gr8Theme.NEON_GREEN};
    }}
    
    /* ===== 테이블 ===== */
    QTableWidget {{
        background-color: {Gr8Theme.BG_SECONDARY};
        alternate-background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.TEXT_PRIMARY};
        gridline-color: {Gr8Theme.BORDER_DEFAULT};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 5px;
        selection-background-color: {Gr8Theme.NEON_BLUE};
        selection-color: {Gr8Theme.TEXT_ON_ACCENT};
    }}
    
    QTableWidget::item {{
        padding: 4px 8px;
        border-bottom: 1px solid {Gr8Theme.BORDER_DEFAULT};
    }}
    
    QTableWidget::item:hover {{
        background-color: {Gr8Theme.BG_TERTIARY};
    }}
    
    QTableWidget QTableCornerButton::section {{
        background-color: {Gr8Theme.BG_TERTIARY};
        border: none;
    }}
    
    QHeaderView::section {{
        background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.TEXT_PRIMARY};
        padding: 6px 8px;
        border: none;
        border-bottom: 2px solid {Gr8Theme.NEON_GREEN};
        font-weight: bold;
        font-size: 12px;
    }}
    
    /* ===== 스크롤바 ===== */
    QScrollBar:vertical {{
        background-color: {Gr8Theme.BG_SECONDARY};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {Gr8Theme.BORDER_DEFAULT};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {Gr8Theme.NEON_BLUE};
    }}
    
    QScrollBar:horizontal {{
        background-color: {Gr8Theme.BG_SECONDARY};
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {Gr8Theme.BORDER_DEFAULT};
        border-radius: 6px;
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {Gr8Theme.NEON_BLUE};
    }}
    
    QScrollBar::add-line, QScrollBar::sub-line {{
        border: none;
        background: none;
    }}
    
    /* ===== 타이틀 라벨 ===== */
    TitleLabel {{
        color: {Gr8Theme.TEXT_PRIMARY};
        font-size: 22px;
        font-weight: bold;
        padding: 5px 0;
    }}
    
    SubtitleLabel {{
        color: {Gr8Theme.NEON_GREEN};
        font-size: 16px;
        font-weight: bold;
        padding: 8px 0 4px 0;
    }}
    
    BodyLabel {{
        color: {Gr8Theme.TEXT_SECONDARY};
        font-size: 13px;
    }}
    
    /* ===== Progress Bar ===== */
    QProgressBar {{
        background-color: {Gr8Theme.BG_INPUT};
        border: 2px solid {Gr8Theme.BORDER_DEFAULT};
        border-radius: 5px;
        height: 20px;
        text-align: center;
        color: {Gr8Theme.TEXT_PRIMARY};
    }}
    
    QProgressBar::chunk {{
        background-color: {Gr8Theme.NEON_GREEN};
        border-radius: 3px;
    }}
    
    /* ===== 탭 (Pivot) ===== */
    Pivot {{
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px solid {Gr8Theme.BORDER_DEFAULT} !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    Pivot QPushButton, Pivot > QPushButton {{
        color: {Gr8Theme.TEXT_SECONDARY} !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 4px solid transparent !important;
        padding: 14px 28px !important;
        margin: 0 !important;
        margin-bottom: -2px !important;
        font-size: 14px !important;
        min-width: 100px !important;
        border-radius: 0 !important;
        text-align: center !important;
    }}
    
    Pivot QPushButton:hover, Pivot > QPushButton:hover {{
        color: {Gr8Theme.TEXT_PRIMARY} !important;
        background-color: rgba(0, 212, 255, 0.1) !important;
        border-bottom: 4px solid {Gr8Theme.NEON_BLUE} !important;
    }}
    
    Pivot QPushButton:checked, Pivot > QPushButton:checked {{
        color: {Gr8Theme.NEON_GREEN} !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 4px solid {Gr8Theme.NEON_GREEN} !important;
        font-weight: bold !important;
    }}
    
    /* ===== 툴팁 ===== */
    QToolTip {{
        background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.TEXT_PRIMARY};
        border: 2px solid {Gr8Theme.NEON_GREEN};
        border-radius: 5px;
        padding: 6px 10px;
    }}
    
    /* ===== InfoBar (알림) ===== */
    InfoBar {{
        background-color: {Gr8Theme.BG_SECONDARY};
        border-left: 4px solid {Gr8Theme.NEON_GREEN};
        border-radius: 5px;
        padding: 12px;
    }}
    
    /* ===== 네비게이션 ===== */
    NavigationInterface {{
        background-color: {Gr8Theme.BG_SECONDARY};
        border-right: 2px solid {Gr8Theme.BORDER_DEFAULT};
    }}
    
    NavigationInterface::item {{
        color: {Gr8Theme.TEXT_SECONDARY};
        padding: 10px 14px;
        margin: 3px 6px;
        border-radius: 5px;
    }}
    
    NavigationInterface::item:hover {{
        background-color: {Gr8Theme.BG_TERTIARY};
        color: {Gr8Theme.NEON_BLUE};
    }}
    
    NavigationInterface::item:selected {{
        background-color: {Gr8Theme.NEON_GREEN};
        color: {Gr8Theme.TEXT_ON_ACCENT};
        font-weight: bold;
    }}
    
    /* ===== 스플리터 ===== */
    QSplitter::handle {{
        background-color: {Gr8Theme.BORDER_DEFAULT};
        width: 3px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {Gr8Theme.NEON_BLUE};
    }}
    """


def apply_theme_to_widget(widget):
    """위젯에 커스텀 테마 적용"""
    widget.setStyleSheet(get_custom_stylesheet())
