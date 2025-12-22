# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Gr8 DIY** is a Python-based cryptocurrency automated trading desktop application built with PySide6 and QFluentWidgets. It features multi-exchange support via CCXT, automated trading bots with Martingale DCA strategies, real-time data collection, and backtesting capabilities with a custom cyberpunk-themed UI.

### Key Features
- **Multi-Exchange Support**: 38+ exchanges including Binance, Bybit, OKX, Bitget, KuCoin, HTX, Kraken
- **Automated Trading**: Martingale DCA strategy with TP/SL management and leverage support
- **Data Collection**: Historical data backfill (200 days) and real-time updates (10s polling)
- **Modern UI**: PySide6 + QFluentWidgets with custom Gr8 DIY cyberpunk theme (neon green/blue)
- **Real-time Monitoring**: Position tracking, bot status, and trade history
- **Backtesting**: Strategy backtesting engine (in development)

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv env

# Activate (Windows)
.\env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Primary method
python app/main.py

# Alternative with batch script
.\scripts\3_run_app.bat

# From virtual environment (Windows)
.\env\Scripts\python.exe .\app\main.py
```

### Building for Distribution
```bash
# Main build script
.\build.bat

# Build creates standalone executable in dist/Gr8 DIY/
```

### Testing
```bash
# Run individual test files
python test_basic_qt.py          # Qt framework testing
python test_okx_api.py           # OKX API connectivity
python test_collection.py        # Data collection testing
python test_full_data_collection.py  # Complete data pipeline
python test_minimal_window.py    # Minimal UI testing
```

## Architecture Overview

### Layered Architecture
```
├── Presentation Layer (UI: PySide6 + QFluentWidgets)
├── Application Layer (Workers: data_collector, trading_bot)
├── Domain Layer (Indicators, Business Logic, Strategies)
└── Infrastructure Layer (API Clients, Database, Utils)
```

### Key Components

**Entry Point**: `app/main.py` - Qt initialization with high DPI setup and custom theme loading

**Multi-Exchange API Integration**:
- `api/ccxt_client.py` - Unified CCXT client
- `api/exchange_factory.py` - Factory pattern for exchange creation
- `config/exchanges.py` - 38+ exchange configurations

**UI Architecture**:
- Navigation-based layout with side navigation bar
- Custom cyberpunk theme (neon green/blue) in `ui/theme.py`
- Signal-slot pattern for thread-safe UI updates
- Pages: Home, Settings, Data, Bot, Backtest, History

**Database**: SQLite with 11 tables for multi-exchange support
- Schema: `database/schema.py`
- Repository: `database/repository.py`
- Tables include exchanges, candles, indicators, bot_configs, orders, positions, etc.

**Background Workers**:
- `workers/data_collector.py` - Multi-exchange data collection (10s polling)
- Historical backfill up to 200 days
- Real-time data updates via WebSocket where available

## Design Principles

1. **Multi-Exchange First**: All components designed for multi-exchange support via CCXT
2. **Thread Safety**: UI and background workers separated via Qt signals
3. **KST Timezone**: All timestamps in Korean Standard Time
4. **Security**: API credentials encrypted using PBKDF2 + Fernet
5. **Rate Limiting**: Respect all exchange API rate limits
6. **Data Retention**: Automatic cleanup of data older than 200 days

## Key Technical Details

### Dependencies
- **PySide6 6.4.2** - Qt framework (specific version for compatibility)
- **PySide6-Fluent-Widgets 1.5.1** - Modern UI components
- **CCXT 4.0+** - Multi-exchange API library
- **cryptography** - API credential encryption
- **pandas/numpy** - Data processing
- **websockets** - Real-time data streams

### Exchange Support
38+ exchanges supported including Binance, Bybit, OKX, Bitget, KuCoin, HTX, Kraken. Each exchange can be configured independently with API keys, testnet mode, and specific symbols.

### Trading Bot Strategy
Martingale DCA (Dollar Cost Averaging) with:
- Symbol-specific long/short direction
- Leverage adjustment (1-100x)
- Auto take profit/stop loss
- Position monitoring and auto-restart

### Data Flow
1. Historical data collection via CCXT REST APIs
2. Real-time updates via WebSocket or polling
3. Technical indicator calculation (MA, MACD, RSI, Stochastic, Bollinger Bands)
4. Database storage with exchange-specific identification
5. Automatic data maintenance and cleanup

### Database Schema (Multi-Exchange)

```sql
-- Exchange Management
exchanges                -- Exchange metadata and capabilities
exchange_credentials     -- Encrypted API keys per exchange

-- Data Storage (all include exchange_id)
candles                 -- OHLCV data with exchange segregation
indicators              -- Technical indicators per exchange/symbol
active_symbols          -- Currently tracked symbols per exchange

-- Trading System
bot_configs             -- Bot settings per exchange/symbol/direction
orders                  -- Order history with exchange tracking
positions               -- Open positions per exchange
bot_logs                -- Bot execution logs
trades_history          -- Completed trades
backtest_results        -- Backtesting performance data
```

## Development Guidelines

### Code Style
- PEP 8 compliance
- Korean language UI with English code comments
- Comprehensive error handling with user-friendly messages
- Type hints where applicable

### Security
- Never commit API keys or credentials
- Use encrypted storage for sensitive data
- All credentials encrypted at rest using `utils/crypto.py`

### Testing
- Test API connectivity before implementing features
- Validate database operations thoroughly
- Test UI components with different DPI settings
- Verify multi-threading scenarios

### Common Patterns
- **Repository Pattern**: Use `database/repository.py` for all database operations
- **Factory Pattern**: Use `api/exchange_factory.py` for creating exchange clients
- **Signal-Slot**: Use Qt signals for thread-safe communication
- **Configuration**: Centralize settings in `config/settings.py`

## Important File Locations

- **Main App**: `app/main.py`
- **Database Schema**: `database/schema.py`
- **Exchange Configs**: `config/exchanges.py`
- **Custom Theme**: `ui/theme.py`
- **Data Collector**: `workers/data_collector.py`
- **API Client**: `api/ccxt_client.py`
- **Settings**: `config/settings.py`

## Build Configuration

PyInstaller build script includes:
- Qt platform plugins for Windows compatibility
- Hidden imports for all dependencies
- Exclusion of conflicting Qt versions
- Data bundling for standalone executable

The build creates a portable executable in `dist/Gr8 DIY/` that doesn't require Python installation.

