"""
Exchange Selector Widget
Searchable dropdown + consistent interface
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCompleter, QListView
)
from PySide6.QtCore import Qt, Signal, QStringListModel
from qfluentwidgets import (
    ComboBox, SearchLineEdit, BodyLabel, CardWidget
)

from config.exchanges import (
    SUPPORTED_EXCHANGES, ALL_EXCHANGE_IDS, DEFAULT_EXCHANGE_ID,
    TESTNET_EXCHANGES
)


class ExchangeSelector(QWidget):
    """Searchable exchange selector widget"""

    # Exchange change signal
    exchange_changed = Signal(str)  # exchange_id

    def __init__(self, show_label: bool = True, label_text: str = "Exchange:",
                 show_testnet_only: bool = False, default_exchange: str = None):
        """
        Args:
            show_label: Whether to show label
            label_text: Label text
            show_testnet_only: Show only testnet supported exchanges
            default_exchange: Default selected exchange (None for DEFAULT_EXCHANGE_ID)
        """
        super().__init__()
        
        self.show_testnet_only = show_testnet_only
        self._current_exchange_id = default_exchange or DEFAULT_EXCHANGE_ID
        
        self._init_ui(show_label, label_text)
        self._setup_exchanges()
        
        # Select default exchange
        self._select_exchange(self._current_exchange_id)

    def _init_ui(self, show_label: bool, label_text: str):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        if show_label:
            label = BodyLabel(label_text)
            label.setFixedWidth(80)
            layout.addWidget(label)
        
        # Search + combo box container
        combo_container = QVBoxLayout()
        combo_container.setSpacing(5)

        # Search input
        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("Search exchanges...")
        self.search_edit.setFixedHeight(36)
        self.search_edit.textChanged.connect(self._on_search_changed)
        combo_container.addWidget(self.search_edit)

        # Combo box
        self.combo = ComboBox()
        self.combo.setFixedHeight(36)
        self.combo.setMinimumWidth(300)
        self.combo.setMaximumWidth(400)
        self.combo.currentIndexChanged.connect(self._on_combo_changed)

        # Exchange selection dropdown style (theme-based + width limit)
        from ui.theme import get_custom_stylesheet
        base_style = get_custom_stylesheet()

        # Apply base theme style
        self.combo.setStyleSheet(base_style)

        # Additional style for exchange selection (width limit)
        additional_style = """
            QComboBox {
                max-width: 380px;
                min-width: 280px;
            }
            QComboBox QAbstractItemView {
                max-width: 380px !important;
                min-width: 280px !important;
                /* Height adjustment for long exchange names */
                min-height: 200px;
                max-height: 300px;
            }
            QComboBox QAbstractItemView::item {
                /* Allow word wrap for long text */
                word-wrap: break-word;
                white-space: pre-wrap;
            }
        """

        # 스타일 병합
        current_style = self.combo.styleSheet()
        self.combo.setStyleSheet(current_style + additional_style)

        combo_container.addWidget(self.combo)
        
        layout.addLayout(combo_container)
        layout.addStretch()
    
    def _setup_exchanges(self):
        """거래소 목록 설정"""
        self.combo.clear()
        
        # 표시할 거래소 목록
        if self.show_testnet_only:
            exchange_ids = TESTNET_EXCHANGES
        else:
            exchange_ids = ALL_EXCHANGE_IDS
        
        # 순위순으로 정렬 (이미 SUPPORTED_EXCHANGES에서 순위순)
        self._exchange_list = []
        
        for ex_id in exchange_ids:
            ex_info = SUPPORTED_EXCHANGES.get(ex_id, {})
            name = ex_info.get('name', ex_id)
            rank = ex_info.get('rank', 999)
            
            display_text = f"{name} (#{rank})"
            self.combo.addItem(display_text, ex_id)
            self._exchange_list.append({
                'id': ex_id,
                'name': name,
                'display': display_text,
                'rank': rank
            })
        
        # 자동완성 설정
        names = [ex['display'] for ex in self._exchange_list]
        completer = QCompleter(names, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.search_edit.setCompleter(completer)
    
    def _on_search_changed(self, text: str):
        """검색어 변경"""
        text = text.lower().strip()
        
        if not text:
            # 검색어 없으면 전체 표시
            self._filter_combo("")
            return
        
        # 검색어로 필터링
        self._filter_combo(text)
    
    def _filter_combo(self, search_text: str):
        """콤보박스 필터링"""
        current_id = self._current_exchange_id
        
        self.combo.blockSignals(True)
        self.combo.clear()
        
        for ex in self._exchange_list:
            if not search_text or search_text in ex['name'].lower() or search_text in ex['id'].lower():
                self.combo.addItem(ex['display'], ex['id'])
        
        # 기존 선택 복원
        for i in range(self.combo.count()):
            if self.combo.itemData(i) == current_id:
                self.combo.setCurrentIndex(i)
                break
        
        self.combo.blockSignals(False)
    
    def _on_combo_changed(self, index: int):
        """콤보박스 선택 변경"""
        if index < 0 or index >= self.combo.count():
            return
        
        # 콤보박스 텍스트로 exchange_list에서 ID 찾기
        display_text = self.combo.currentText()
        
        for ex in self._exchange_list:
            if ex['display'] == display_text:
                exchange_id = ex['id']
                if exchange_id != self._current_exchange_id:
                    self._current_exchange_id = exchange_id
                    self.exchange_changed.emit(exchange_id)
                    print(f"[DEBUG-ExchangeSelector] 거래소 변경됨: {exchange_id}")
                break
    
    def _select_exchange(self, exchange_id: str):
        """특정 거래소 선택"""
        for i in range(self.combo.count()):
            if self.combo.itemData(i) == exchange_id:
                self.combo.setCurrentIndex(i)
                self._current_exchange_id = exchange_id
                return True
        return False
    
    def get_exchange_id(self) -> str:
        """현재 선택된 거래소 ID"""
        return self._current_exchange_id
    
    def get_exchange_info(self) -> dict:
        """현재 선택된 거래소 정보"""
        return SUPPORTED_EXCHANGES.get(self._current_exchange_id, {})
    
    def get_exchange_name(self) -> str:
        """현재 선택된 거래소 이름"""
        info = self.get_exchange_info()
        return info.get('name', self._current_exchange_id)
    
    def set_exchange(self, exchange_id: str):
        """거래소 설정"""
        self._select_exchange(exchange_id)
    
    def clear_search(self):
        """검색어 초기화"""
        self.search_edit.clear()
        self._filter_combo("")


class ExchangeSelectorCard(CardWidget):
    """거래소 선택 카드 위젯"""
    
    exchange_changed = Signal(str)
    
    def __init__(self, title: str = "거래소 선택", 
                 description: str = None,
                 show_testnet_only: bool = False,
                 default_exchange: str = None):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        from qfluentwidgets import SubtitleLabel
        
        title_label = SubtitleLabel(title)
        layout.addWidget(title_label)
        
        if description:
            desc_label = BodyLabel(description)
            desc_label.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(desc_label)
        
        self.selector = ExchangeSelector(
            show_label=False,
            show_testnet_only=show_testnet_only,
            default_exchange=default_exchange
        )
        self.selector.exchange_changed.connect(self.exchange_changed.emit)
        layout.addWidget(self.selector)
    
    def get_exchange_id(self) -> str:
        return self.selector.get_exchange_id()
    
    def get_exchange_info(self) -> dict:
        return self.selector.get_exchange_info()
    
    def set_exchange(self, exchange_id: str):
        self.selector.set_exchange(exchange_id)

