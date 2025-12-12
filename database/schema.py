"""
데이터베이스 스키마 정의
CCXT 멀티 거래소 지원 버전
"""
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from utils.logger import logger


class DatabaseSchema:
    """데이터베이스 스키마 관리"""
    
    # 현재 스키마 버전
    SCHEMA_VERSION = 2
    
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
            # 거래소 관련 (새로 추가)
            DatabaseSchema._table_exchanges(),
            DatabaseSchema._table_exchange_credentials(),
            
            # 데이터 관련
            DatabaseSchema._table_candles(),
            DatabaseSchema._table_indicators(),
            DatabaseSchema._table_active_symbols(),
            
            # 봇 관련
            DatabaseSchema._table_bot_configs(),
            DatabaseSchema._table_orders(),
            DatabaseSchema._table_positions(),
            DatabaseSchema._table_bot_logs(),
            DatabaseSchema._table_trades_history(),
            
            # 시스템 관련
            DatabaseSchema._table_system_logs(),
            DatabaseSchema._table_app_settings(),
            
            # 백테스트 관련 (새로 추가)
            DatabaseSchema._table_backtest_results(),
        ]
        
        for table_sqls in tables:
            # 여러 SQL 문을 분리 실행
            for sql in table_sqls:
                query = QSqlQuery()
                if not query.exec(sql):
                    # "not an error"는 무시 (Qt의 알려진 이슈)
                    error_text = query.lastError().text()
                    if "not an error" not in error_text.lower():
                        logger.error("DB", f"테이블 생성 실패: {error_text}")
                        logger.error("DB", f"SQL: {sql}")
                else:
                    logger.debug("DB", "테이블 생성 성공")
    
    # ========== 거래소 관련 테이블 ==========
    
    @staticmethod
    def _table_exchanges() -> list:
        """거래소 마스터 테이블"""
        return [
            """CREATE TABLE IF NOT EXISTS exchanges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                has_futures INTEGER DEFAULT 0,
                has_testnet INTEGER DEFAULT 0,
                maker_fee REAL DEFAULT 0.0002,
                taker_fee REAL DEFAULT 0.0005,
                is_enabled INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            "CREATE INDEX IF NOT EXISTS idx_exchanges_id ON exchanges(exchange_id)"
        ]
    
    @staticmethod
    def _table_exchange_credentials() -> list:
        """거래소별 API 자격증명"""
        return [
            """CREATE TABLE IF NOT EXISTS exchange_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
                api_key TEXT,
                secret TEXT,
                passphrase TEXT,
                is_testnet INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exchange_id, is_testnet)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_creds_exchange ON exchange_credentials(exchange_id)"
        ]
    
    # ========== 데이터 관련 테이블 ==========
    
    @staticmethod
    def _table_candles() -> list:
        """캔들 데이터 (거래소별)"""
        return [
            """CREATE TABLE IF NOT EXISTS candles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exchange_id, symbol, timeframe, timestamp)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_candles_exchange_symbol_tf ON candles(exchange_id, symbol, timeframe)",
            "CREATE INDEX IF NOT EXISTS idx_candles_timestamp ON candles(timestamp DESC)"
        ]
    
    @staticmethod
    def _table_indicators() -> list:
        """보조지표 (거래소별)"""
        return [
            """CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
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
                UNIQUE(exchange_id, symbol, timeframe, timestamp)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_indicators_exchange_symbol_tf ON indicators(exchange_id, symbol, timeframe, timestamp DESC)"
        ]
    
    @staticmethod
    def _table_active_symbols() -> list:
        """활성 심볼 (거래소별)"""
        return [
            """CREATE TABLE IF NOT EXISTS active_symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exchange_id, symbol)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_active_symbols_exchange ON active_symbols(exchange_id)"
        ]
    
    # ========== 봇 관련 테이블 ==========
    
    @staticmethod
    def _table_bot_configs() -> list:
        """봇 설정 (거래소별)"""
        return [
            """CREATE TABLE IF NOT EXISTS bot_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
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
                is_testnet INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exchange_id, symbol, is_testnet)
            )"""
        ]
    
    @staticmethod
    def _table_orders() -> list:
        """주문 내역"""
        return [
            """CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
                order_id TEXT NOT NULL,
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
                is_testnet INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exchange_id, order_id)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_orders_exchange_symbol ON orders(exchange_id, symbol)",
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)"
        ]
    
    @staticmethod
    def _table_positions() -> list:
        """포지션 내역"""
        return [
            """CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
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
                is_testnet INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME
            )""",
            "CREATE INDEX IF NOT EXISTS idx_positions_exchange_symbol ON positions(exchange_id, symbol)",
            "CREATE INDEX IF NOT EXISTS idx_positions_is_closed ON positions(is_closed)"
        ]
    
    @staticmethod
    def _table_bot_logs() -> list:
        """봇 로그"""
        return [
            """CREATE TABLE IF NOT EXISTS bot_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                level TEXT NOT NULL,
                exchange_id TEXT,
                symbol TEXT,
                bot_id INTEGER,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                payload TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            "CREATE INDEX IF NOT EXISTS idx_bot_logs_exchange_symbol ON bot_logs(exchange_id, symbol)",
            "CREATE INDEX IF NOT EXISTS idx_bot_logs_timestamp ON bot_logs(timestamp DESC)"
        ]
    
    @staticmethod
    def _table_trades_history() -> list:
        """거래 내역 (익절/손절 완료된 포지션)"""
        return [
            """CREATE TABLE IF NOT EXISTS trades_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
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
                is_testnet INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            "CREATE INDEX IF NOT EXISTS idx_trades_history_exchange_symbol ON trades_history(exchange_id, symbol)",
            "CREATE INDEX IF NOT EXISTS idx_trades_history_exit_time ON trades_history(exit_time DESC)"
        ]
    
    # ========== 시스템 관련 테이블 ==========
    
    @staticmethod
    def _table_system_logs() -> list:
        """시스템 로그"""
        return [
            """CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                level TEXT NOT NULL,
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                stacktrace TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level)",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp DESC)"
        ]
    
    @staticmethod
    def _table_app_settings() -> list:
        """앱 설정"""
        return [
            """CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        ]
    
    # ========== 백테스트 관련 테이블 ==========
    
    @staticmethod
    def _table_backtest_results() -> list:
        """백테스트 결과"""
        return [
            """CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                
                -- 전략 설정 (JSON)
                strategy_config TEXT NOT NULL,
                
                -- 성과 지표
                initial_capital REAL NOT NULL,
                final_capital REAL NOT NULL,
                total_return REAL,
                cagr REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                sortino_ratio REAL,
                win_rate REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                avg_profit REAL,
                avg_loss REAL,
                profit_factor REAL,
                max_martingale_level INTEGER,
                avg_martingale_level REAL,
                total_fees REAL,
                
                -- 거래 내역 (JSON 배열)
                trades_json TEXT,
                
                -- 자산 곡선 (JSON 배열)
                equity_curve_json TEXT,
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            "CREATE INDEX IF NOT EXISTS idx_backtest_exchange_symbol ON backtest_results(exchange_id, symbol)",
            "CREATE INDEX IF NOT EXISTS idx_backtest_created ON backtest_results(created_at DESC)"
        ]
