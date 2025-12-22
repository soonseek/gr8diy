"""
Home Page - Content separated by tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QStackedWidget, QListWidget, QListWidgetItem, QLabel, QFrame
from PySide6.QtCore import Qt, QSize
from qfluentwidgets import Pivot, FluentIcon, ListItemDelegate
from pathlib import Path
import markdown
import os
import re


class HomePage(QWidget):
    """Home Page"""

    def __init__(self):
        super().__init__()
        self.update_versions = []  # Version information storage
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Pivot tabs
        pivot_layout = QHBoxLayout()
        self.pivot = Pivot(self)
        pivot_layout.addWidget(self.pivot)
        pivot_layout.addStretch()
        layout.addLayout(pivot_layout)

        # Stack widget
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Tab contents
        self.intro_browser = self._create_browser()
        self.features_browser = self._create_browser()
        self.setup_browser = self._create_browser()
        self.guide_browser = self._create_browser()
        self.community_browser = self._create_browser()

        # Update history widget
        self.updates_widget = QWidget()
        self.updates_layout = QHBoxLayout(self.updates_widget)
        self.updates_layout.setContentsMargins(0, 0, 0, 0)
        self.updates_layout.setSpacing(10)

        # Left content area
        self.updates_browser = self._create_browser()
        self.updates_layout.addWidget(self.updates_browser, 1)  # stretch factor = 1

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #4a5080; max-width: 1px;")
        self.updates_layout.addWidget(separator)

        # Right version list (30%)
        self.version_list_widget = QWidget()
        self.version_list_layout = QVBoxLayout(self.version_list_widget)
        self.version_list_layout.setContentsMargins(5, 0, 0, 0)

        # Version list title
        version_title = QLabel("Version List")
        version_title.setStyleSheet("""
            QLabel {
                color: #00ff9f;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 0;
                border-bottom: 2px solid #00ff9f;
                margin-bottom: 10px;
            }
        """)
        self.version_list_layout.addWidget(version_title)

        # Version list
        self.version_list = QListWidget()
        self.version_list.setFixedWidth(220)
        self.version_list.setFocusPolicy(Qt.NoFocus)  # Disable focus
        self.version_list.setStyleSheet("""
            QListWidget {
                background: #1a1a2e;
                border: 2px solid #4a5080;
                border-radius: 6px;
                padding: 5px;
                color: #e0e0e0;
                font-size: 13px;
                outline: none;
            }
            QListWidget:focus {
                border: 2px solid #4a5080;
                outline: none;
            }
            QListWidget::item {
                padding: 12px 10px;
                margin: 2px 0;
                border-radius: 4px;
                background: transparent;
                border: none;
            }
            QListWidget::item:hover {
                background: rgba(0, 255, 159, 0.1);
            }
            QListWidget::item:selected {
                background: rgba(0, 255, 159, 0.2);
                border: 2px solid #00ff9f;
                color: #00ff9f;
                font-weight: bold;
            }
            QListWidget::item:selected:hover {
                background: rgba(0, 255, 159, 0.3);
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 12px;
                border-radius: 6px;
                outline: none;
            }
            QScrollBar::handle:vertical {
                background: #4a5080;
                border-radius: 6px;
                min-height: 20px;
                outline: none;
            }
            QScrollBar::handle:vertical:hover {
                background: #00ff9f;
                outline: none;
            }
        """)
        self.version_list.itemClicked.connect(self._on_version_item_clicked)
        self.version_list_layout.addWidget(self.version_list)

        self.updates_layout.addWidget(self.version_list_widget, 0)  # stretch factor = 0 (fixed width)
        # Set version widget width to match list width
        self.version_list_widget.setFixedWidth(230)  # list(220) + margin(10)

        self.stack.addWidget(self.intro_browser)
        self.stack.addWidget(self.features_browser)
        self.stack.addWidget(self.setup_browser)
        self.stack.addWidget(self.guide_browser)
        self.stack.addWidget(self.community_browser)
        self.stack.addWidget(self.updates_widget)
        
        self.pivot.addItem("intro", "Project Introduction", lambda: self.stack.setCurrentIndex(0), icon=FluentIcon.INFO)
        self.pivot.addItem("features", "Key Features", lambda: self.stack.setCurrentIndex(1), icon=FluentIcon.ALBUM)
        self.pivot.addItem("setup", "Installation & Setup", lambda: self.stack.setCurrentIndex(2), icon=FluentIcon.DEVELOPER_TOOLS)
        self.pivot.addItem("guide", "Development Guide", lambda: self.stack.setCurrentIndex(3), icon=FluentIcon.DOCUMENT)
        self.pivot.addItem("community", "Community", lambda: self.stack.setCurrentIndex(4), icon=FluentIcon.PEOPLE)
        self.pivot.addItem("updates", "Update History", lambda: self.stack.setCurrentIndex(5), icon=FluentIcon.UPDATE)
        
        self.pivot.setCurrentItem("intro")
        
        self._load_content()
    
    def _create_browser(self) -> QTextBrowser:
        """Create text browser"""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                border: none;
                padding: 10px;
                font-size: 13px;
            }
        """)
        return browser
    
    def _load_content(self):
        """Load content"""
        # Project introduction
        self.intro_browser.setHtml(self._style_html("""
# Gr8 DIY

**Multi-exchange cryptocurrency automated trading desktop application based on PySide6 + QFluentWidgets**

## Key Features

### 🌐 Multi-Exchange Support
- Based on CCXT library - CoinGecko Top 100 exchanges
- Binance, Bybit, OKX, Bitget, Gate.io, KuCoin, HTX, Kraken, etc.
- Independent API key management per exchange

### 📊 Data Collection
- Historical data backfill (up to 200 days)
- Real-time data updates (10-second polling)
- 6 timeframes (1m, 5m, 15m, 1h, 4h, 1d)

### 🤖 Automated Trading Bot
- Martingale DCA strategy
- Leverage adjustment (1-100x)
- Automated take profit/stop loss
- Real-time monitoring

### Tech Stack
- UI: PySide6, QFluentWidgets
- Exchange: CCXT
- DB: SQLite
- AI: OpenAI GPT
        """))
        
        # Key Features
        self.features_browser.setHtml(self._style_html("""
# Key Features

## ⚙️ Settings
### Exchange Integration
- 38+ exchange API key management
- Mainnet/Testnet modes
- Integration test and status check
- Automatic Hedge Mode configuration

### GPT Integration
- OpenAI API key management
- AI analysis features (optional)

## 📊 Data
### Collection
- Exchange-specific data collection
- Historical data backfill
- Real-time updates (10-second polling)
- Active symbol management

### Viewing
- Exchange-specific data viewing
- Symbol/timeframe data verification
- Collection status monitoring

## 🤖 Bot
### Bot Creation
- Exchange selection (only integrated exchanges)
- Symbol-specific direction settings (LONG/SHORT)
- Margin and leverage settings
- Martingale stage/offset settings
- Take profit/stop loss settings

### Monitoring
- Real-time position status
- P&L tracking
- Individual/Bulk liquidation

### History
- Trading statistics (win rate, net profit, etc.)
- Trading history viewing

## 📈 Backtesting (In Development)
- Historical data-based simulation
- Performance metric analysis
- Results export
        """))
        
        # Installation & Setup
        self.setup_browser.setHtml(self._style_html("""
# Installation & Setup

## System Requirements
- Windows 10/11
- Python 3.10 or higher
- 8GB RAM or more recommended

## Installation

### 1. Install Python
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add to PATH" during installation

### 2. Create Virtual Environment
```bash
python -m venv env
```

### 3. Install Dependencies
```bash
.\\env\\Scripts\\pip.exe install -r requirements.txt
```

### 4. Run
```bash
.\\env\\Scripts\\python.exe .\\app\\main.py
```

## Initial Setup

### 1. Exchange API Integration
1. Settings → Exchange Integration
2. Select exchange
3. Enter API Key, Secret (some require Passphrase)
4. Test connection with test button
5. Save

### 2. Data Collection
1. Data → Collection
2. Select exchange
3. Set collection period
4. Select active symbols
5. Start collection

### 3. Bot Execution
1. Bot → Create Bot
2. Select exchange (only integrated exchanges)
3. Select symbol checkboxes
4. Set direction/margin/leverage
5. Configure Martingale settings
6. Set take profit/stop loss
7. 🚀 Run Bot
        """))
        
        # Development Guide
        self.guide_browser.setHtml(self._style_html("""
# Development Guide

## Project Structure
```
free-trader/
├── app/           # Main entry point
├── ui/            # UI components
├── api/           # Exchange APIs
├── workers/       # Background tasks
├── database/      # DB schema and repository
├── config/        # Configuration
├── backtest/      # Backtest engine
└── utils/         # Utilities
```

## Key Classes

### API
- `CCXTClient`: CCXT unified client
- `ExchangeFactory`: Exchange client factory

### Workers
- `DataCollectorWorker`: Data collection
- `TradingBotWorker`: Bot execution
- `BacktestWorker`: Backtest execution

### UI
- `MainWindow`: Main window
- `SettingsPage`: Settings
- `DataPage`: Data
- `BotPage`: Bot
- `BacktestPage`: Backtest

## Adding New Exchange
1. Add metadata to `config/exchanges.py`
2. Works automatically if CCXT supports it

## Theme Customization
Modify `Gr8Theme` class in `ui/theme.py`:
```python
NEON_GREEN = "#00ff9f"  # Desired color
NEON_BLUE = "#00d4ff"
```
        """))
        
        # Community
        self.community_browser.setHtml(self._style_html("""
# Community

## 📺 YouTube
**Channel: Sofia Papa**
- Automated trading bot development tutorials
- DIY project development process
- Live coding sessions

## 💬 Discord
**[Join Gr8 DIY Discord](https://discord.gg/KBvavs9F47)**
- Real-time communication
- Q&A
- Bug reports
- Feature suggestions

## 🐙 GitHub
**[Gr8 DIY GitHub Repository](https://github.com/soonseek/gr8diy)**
- Source code
- Issue tracking
- Pull Requests

## How to Contribute
- 🐛 Found a bug: Discord or GitHub Issue
- 💡 Feature suggestion: Discuss on Discord
- 🔧 Code contribution: Pull Requests welcome
- 📖 Documentation improvement: README edit suggestions

---

**Made with ❤️ by YouTube <Sofia Papa> and subscribers**
        """))
        
        # Update history
        self._load_update_versions()

    def _style_html(self, content: str) -> str:
        """Convert markdown to styled HTML"""
        try:
            html = markdown.markdown(
                content, 
                extensions=['fenced_code', 'tables', 'toc']
            )
        except:
            html = f"<pre>{content}</pre>"
        
        return f"""
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                color: #e0e0e0; 
                line-height: 1.6;
            }}
            h1 {{ color: #00ff9f; font-size: 24px; margin: 20px 0 12px 0; border-bottom: 2px solid #00ff9f; padding-bottom: 8px; }}
            h2 {{ color: #00d4aa; font-size: 18px; margin: 16px 0 10px 0; }}
            h3 {{ color: #00d4aa; font-size: 15px; margin: 12px 0 8px 0; }}
            p {{ margin: 8px 0; }}
            ul, ol {{ margin: 10px 0; padding-left: 30px; }}
            li {{ margin: 5px 0; line-height: 1.5; }}
            code {{ 
                background: #1a1a2e; 
                padding: 3px 6px; 
                border-radius: 3px; 
                font-size: 12px; 
                color: #00ff9f;
                font-family: 'Consolas', 'Monaco', monospace;
            }}
            pre {{ 
                background: #1a1a2e; 
                padding: 15px; 
                border-radius: 6px; 
                overflow-x: auto; 
                border: 1px solid #4a5080;
                margin: 12px 0;
            }}
            pre code {{
                background: transparent;
                padding: 0;
                color: #e0e0e0;
            }}
            a {{ color: #00d4ff; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            table {{ border-collapse: collapse; margin: 12px 0; width: 100%; }}
            th, td {{ border: 1px solid #4a5080; padding: 8px 12px; text-align: left; }}
            th {{ background: #1a1a2e; color: #00ff9f; font-weight: bold; }}
            blockquote {{
                border-left: 4px solid #00ff9f;
                margin: 12px 0;
                padding: 8px 15px;
                background: rgba(0, 255, 159, 0.05);
            }}
            hr {{ border: none; border-top: 1px solid #4a5080; margin: 20px 0; }}
        </style>
        {html}
        """

    def _load_update_versions(self):
        """Load update version list"""
        # Updates folder path
        updates_dir = Path(__file__).parent.parent / "updates"

        # Initialize version information
        self.update_versions = []
        self.version_list.clear()

        if updates_dir.exists():
            # Find v*_*.md files (e.g., v1.1_2025-12-12.md)
            pattern = re.compile(r'^v(\d+\.\d+)_(\d{4}-\d{2}-\d{2})\.md$')

            for file in sorted(updates_dir.glob("v*.md"), reverse=True):
                match = pattern.match(file.name)
                if match:
                    version = match.group(1)
                    date = match.group(2)
                    display_text = f"v{version} ({date})"

                    self.update_versions.append({
                        'version': version,
                        'date': date,
                        'file': file,
                        'display': display_text
                    })

                    # Add list item
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, len(self.update_versions) - 1)  # Store index
                    self.version_list.addItem(item)

        # Select first version (latest) as default
        if self.update_versions:
            self.version_list.setCurrentRow(0)
            self._load_selected_update(0)
        else:
            # Load existing UPDATES.md file if available
            updates_path = Path(__file__).parent.parent / "UPDATES.md"
            if updates_path.exists():
                try:
                    with open(updates_path, 'r', encoding='utf-8') as f:
                        updates_content = f.read()
                    self.updates_browser.setHtml(self._style_html(updates_content))
                except:
                    self.updates_browser.setHtml(self._style_html("# Update History\n\nLoad failed"))
            else:
                self.updates_browser.setHtml(self._style_html("# Update History\n\nUpdate files not found."))

    def _on_version_item_clicked(self, item):
        """Load update content when version list item is clicked"""
        index = item.data(Qt.UserRole)
        if index is not None and 0 <= index < len(self.update_versions):
            self._load_selected_update(index)

    def _load_selected_update(self, index):
        """Load update content for selected version"""
        if 0 <= index < len(self.update_versions):
            version_info = self.update_versions[index]

            try:
                with open(version_info['file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                self.updates_browser.setHtml(self._style_html(content))
            except Exception as e:
                self.updates_browser.setHtml(self._style_html(
                    f"# Update History\n\n"
                    f"File load failed: {version_info['display']}\n\n"
                    f"Error: {str(e)}"
                ))
