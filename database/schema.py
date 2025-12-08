"""
데이터베이스 스키마 정의
"""
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from utils.logger import logger


class DatabaseSchema:
    """데이터베이스 스키마 관리"""
    
    @staticmethod
    def init_database(db_path: str) -> bool:
        """데이터베이스 초기화"""
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(db_path)
        
        if not db.open():
            logger.error("DB", f"데이터베이스 연결 실패: {db.lastError().text()}")
            return False
        
        logger.info("DB", f"데이터베이스 연결 성공: {db_path}")
        
        # 테이블 생성
        DatabaseSchema._create_tables()
        
        return True
    
    @staticmethod
    def _create_tables():
        """모든 테이블 생성"""
        tables = [
            DatabaseSchema._table_candles(),
            DatabaseSchema._table_indicators(),
            DatabaseSchema._table_bot_configs(),
            DatabaseSchema._table_orders(),
            DatabaseSchema._table_positions(),
            DatabaseSchema._table_bot_logs(),
            DatabaseSchema._table_system_logs(),
            DatabaseSchema._table_active_symbols(),
            DatabaseSchema._table_app_settings(),
            DatabaseSchema._table_trades_history(),
        ]
        
        for table_sql in tables:
            query = QSqlQuery()
            if not query.exec(table_sql):
                logger.error("DB", f"테이블 생성 실패: {query.lastError().text()}")
                logger.error("DB", f"SQL: {table_sql}")
            else:
                logger.debug("DB", "테이블 생성 성공")
    
    @staticmethod
    def _table_candles() -> str:
        return """
        CREATE TABLE IF NOT EXISTS candles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timeframe, timestamp)
        );
        CREATE INDEX IF NOT EXISTS idx_candles_symbol_tf_ts 
        ON candles(symbol, timeframe, timestamp DESC);
        """
    
    @staticmethod
    def _table_indicators() -> str:
        return """
        CREATE TABLE IF NOT EXISTS indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            ma_20 REAL,
            ma_50 REAL,
            ma_100 REAL,
            ma_200 REAL,
            macd REAL,
            macd_signal REAL,
            macd_hist REAL,
            rsi REAL,
            stoch_k REAL,
            stoch_d REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timeframe, timestamp)
        );
        CREATE INDEX IF NOT EXISTS idx_indicators_symbol_tf_ts 
        ON indicators(symbol, timeframe, timestamp DESC);
        """
    
    @staticmethod
    def _table_bot_configs() -> str:
        return """
        CREATE TABLE IF NOT EXISTS bot_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            direction TEXT NOT NULL,
            interval TEXT NOT NULL,
            max_margin REAL NOT NULL,
            margin_mode TEXT NOT NULL,
            leverage INTEGER NOT NULL,
            martingale_enabled INTEGER DEFAULT 0,
            martingale_steps INTEGER DEFAULT 0,
            martingale_offset_pct REAL DEFAULT 0,
            martingale_size_ratios TEXT,
            tp_offset_pct REAL NOT NULL,
            sl_offset_pct REAL,
            is_active INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol)
        );
        """
    
    @staticmethod
    def _table_orders() -> str:
        return """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            type TEXT NOT NULL,
            price REAL,
            size REAL NOT NULL,
            filled_size REAL DEFAULT 0,
            status TEXT NOT NULL,
            bot_id INTEGER,
            position_id INTEGER,
            related_order_type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        """
    
    @staticmethod
    def _table_positions() -> str:
        return """
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            size REAL NOT NULL,
            avg_price REAL NOT NULL,
            leverage INTEGER NOT NULL,
            liquidation_price REAL,
            unrealized_pnl REAL DEFAULT 0,
            realized_pnl REAL DEFAULT 0,
            total_fees REAL DEFAULT 0,
            bot_id INTEGER,
            is_closed INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            closed_at DATETIME
        );
        CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
        CREATE INDEX IF NOT EXISTS idx_positions_is_closed ON positions(is_closed);
        """
    
    @staticmethod
    def _table_bot_logs() -> str:
        return """
        CREATE TABLE IF NOT EXISTS bot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            level TEXT NOT NULL,
            symbol TEXT,
            bot_id INTEGER,
            category TEXT NOT NULL,
            message TEXT NOT NULL,
            payload TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_bot_logs_symbol ON bot_logs(symbol);
        CREATE INDEX IF NOT EXISTS idx_bot_logs_timestamp ON bot_logs(timestamp DESC);
        """
    
    @staticmethod
    def _table_system_logs() -> str:
        return """
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            level TEXT NOT NULL,
            module TEXT NOT NULL,
            message TEXT NOT NULL,
            stacktrace TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
        CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp DESC);
        """
    
    @staticmethod
    def _table_active_symbols() -> str:
        return """
        CREATE TABLE IF NOT EXISTS active_symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL UNIQUE,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    @staticmethod
    def _table_app_settings() -> str:
        return """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    @staticmethod
    def _table_trades_history() -> str:
        """거래 내역 (익절/손절 완료된 포지션)"""
        return """
        CREATE TABLE IF NOT EXISTS trades_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL NOT NULL,
            size REAL NOT NULL,
            leverage INTEGER NOT NULL,
            pnl REAL NOT NULL,
            fees REAL NOT NULL,
            entry_time DATETIME NOT NULL,
            exit_time DATETIME NOT NULL,
            exit_reason TEXT,
            bot_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_trades_history_symbol ON trades_history(symbol);
        CREATE INDEX IF NOT EXISTS idx_trades_history_exit_time ON trades_history(exit_time DESC);
        """


