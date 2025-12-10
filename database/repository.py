"""
데이터베이스 레포지토리 - CRUD 작업
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from PySide6.QtSql import QSqlQuery, QSqlDatabase
from utils.logger import logger
from utils.time_helper import time_helper


class BaseRepository:
    """기본 레포지토리 클래스"""
    
    def __init__(self):
        self.db = QSqlDatabase.database()
    
    def execute_query(self, sql: str, params: tuple = ()) -> QSqlQuery:
        """쿼리 실행"""
        query = QSqlQuery(self.db)
        
        if params:
            # 파라미터가 있으면 prepare + bind
            if not query.prepare(sql):
                logger.error("DB", f"쿼리 준비 실패: {query.lastError().text()}")
                logger.error("DB", f"SQL: {sql}")
                return query
            
            # positional binding
            for i, param in enumerate(params):
                query.bindValue(i, param)
            
            # prepared 쿼리 실행
            success = query.exec()
        else:
            # 파라미터 없으면 직접 실행
            success = query.exec(sql)
        
        if not success:
            error_text = query.lastError().text()
            # "not an error" 무시 (Qt의 알려진 이슈)
            if "not an error" not in error_text.lower():
                logger.error("DB", f"쿼리 실행 실패: {error_text}")
                logger.error("DB", f"SQL: {sql}")
                if params:
                    logger.error("DB", f"Params: {params}")
        
        return query
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict]:
        """단일 레코드 조회"""
        query = self.execute_query(sql, params)
        if query.next():
            record = query.record()
            return {record.fieldName(i): query.value(i) 
                   for i in range(record.count())}
        return None
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict]:
        """다중 레코드 조회"""
        query = self.execute_query(sql, params)
        results = []
        while query.next():
            record = query.record()
            results.append({record.fieldName(i): query.value(i) 
                          for i in range(record.count())})
        return results


class SystemLogsRepository(BaseRepository):
    """시스템 로그 레포지토리"""
    
    def insert(self, timestamp: str, level: str, module: str, 
               message: str, stacktrace: str = ""):
        """로그 삽입"""
        sql = """
        INSERT INTO system_logs (timestamp, level, module, message, stacktrace)
        VALUES (?, ?, ?, ?, ?)
        """
        self.execute_query(sql, (timestamp, level, module, message, stacktrace))
    
    def get_recent(self, limit: int = 1000, level_filter: str = None) -> List[Dict]:
        """최근 로그 조회"""
        if level_filter and level_filter != "ALL":
            sql = """
            SELECT * FROM system_logs 
            WHERE level = ?
            ORDER BY timestamp DESC LIMIT ?
            """
            return self.fetch_all(sql, (level_filter, limit))
        else:
            sql = """
            SELECT * FROM system_logs 
            ORDER BY timestamp DESC LIMIT ?
            """
            return self.fetch_all(sql, (limit,))
    
    def get_errors(self, limit: int = 1000) -> List[Dict]:
        """에러 로그만 조회"""
        sql = """
        SELECT * FROM system_logs 
        WHERE level IN ('ERROR', 'CRITICAL')
        ORDER BY timestamp DESC LIMIT ?
        """
        return self.fetch_all(sql, (limit,))
    
    def delete_old(self, days: int):
        """오래된 로그 삭제"""
        cutoff = time_helper.days_ago_kst(days)
        cutoff_str = time_helper.format_kst(cutoff)
        sql = "DELETE FROM system_logs WHERE timestamp < ?"
        self.execute_query(sql, (cutoff_str,))


class CandlesRepository(BaseRepository):
    """캔들 데이터 레포지토리"""
    
    def insert_candle(self, symbol: str, timeframe: str, timestamp: str,
                     open_price: float, high: float, low: float, 
                     close: float, volume: float):
        """캔들 삽입 (중복 시 무시)"""
        sql = """
        INSERT OR IGNORE INTO candles 
        (symbol, timeframe, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(sql, (symbol, timeframe, timestamp, 
                                open_price, high, low, close, volume))
    
    def insert_candles_batch(self, candles: List[Dict]):
        """캔들 일괄 삽입"""
        sql = """
        INSERT OR IGNORE INTO candles 
        (symbol, timeframe, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        for candle in candles:
            self.execute_query(sql, (
                candle['symbol'],
                candle['timeframe'],
                candle['timestamp'],
                candle['open'],
                candle['high'],
                candle['low'],
                candle['close'],
                candle['volume']
            ))
    
    def get_latest_timestamp(self, symbol: str, timeframe: str) -> Optional[str]:
        """최신 캔들 타임스탬프 조회"""
        sql = "SELECT timestamp FROM candles WHERE symbol = ? AND timeframe = ? ORDER BY timestamp DESC LIMIT 1"
        result = self.fetch_one(sql, (symbol, timeframe))
        return result['timestamp'] if result else None
    
    def get_candles(self, symbol: str, timeframe: str, 
                   limit: int = 500) -> List[Dict]:
        """캔들 조회"""
        sql = "SELECT * FROM candles WHERE symbol = ? AND timeframe = ? ORDER BY timestamp DESC LIMIT ?"
        return self.fetch_all(sql, (symbol, timeframe, limit))
    
    def delete_old(self, days: int):
        """오래된 캔들 삭제"""
        cutoff = time_helper.days_ago_kst(days)
        cutoff_str = time_helper.format_kst(cutoff)
        sql = "DELETE FROM candles WHERE timestamp < ?"
        self.execute_query(sql, (cutoff_str,))


class IndicatorsRepository(BaseRepository):
    """보조지표 레포지토리"""
    
    def upsert_indicators(self, symbol: str, timeframe: str, 
                         timestamp: str, indicators: Dict):
        """보조지표 삽입/업데이트"""
        sql = """
        INSERT OR REPLACE INTO indicators
        (symbol, timeframe, timestamp, ma_20, ma_50, ma_100, ma_200,
         macd, macd_signal, macd_hist, rsi, stoch_k, stoch_d,
         bb_upper, bb_middle, bb_lower)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(sql, (
            symbol, timeframe, timestamp,
            indicators.get('ma_20'), indicators.get('ma_50'),
            indicators.get('ma_100'), indicators.get('ma_200'),
            indicators.get('macd'), indicators.get('macd_signal'),
            indicators.get('macd_hist'), indicators.get('rsi'),
            indicators.get('stoch_k'), indicators.get('stoch_d'),
            indicators.get('bb_upper'), indicators.get('bb_middle'),
            indicators.get('bb_lower')
        ))
    
    def get_latest(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """최신 지표 조회"""
        sql = """
        SELECT * FROM indicators
        WHERE symbol = ? AND timeframe = ?
        ORDER BY timestamp DESC LIMIT 1
        """
        return self.fetch_one(sql, (symbol, timeframe))
    
    def delete_old(self, days: int):
        """오래된 지표 삭제"""
        cutoff = time_helper.days_ago_kst(days)
        cutoff_str = time_helper.format_kst(cutoff)
        sql = "DELETE FROM indicators WHERE timestamp < ?"
        self.execute_query(sql, (cutoff_str,))


class ActiveSymbolsRepository(BaseRepository):
    """활성 심볼 레포지토리"""
    
    def init_default_symbols(self, symbols: List[str]):
        """기본 심볼 초기화"""
        for symbol in symbols:
            sql = "INSERT OR IGNORE INTO active_symbols (symbol) VALUES (?)"
            self.execute_query(sql, (symbol,))
    
    def get_active_symbols(self) -> List[str]:
        """활성 심볼 목록 조회"""
        sql = "SELECT symbol FROM active_symbols WHERE is_active = 1"
        results = self.fetch_all(sql)
        return [r['symbol'] for r in results]
    
    def set_symbol_active(self, symbol: str, is_active: bool):
        """심볼 활성화 상태 변경"""
        sql = "UPDATE active_symbols SET is_active = ? WHERE symbol = ?"
        self.execute_query(sql, (1 if is_active else 0, symbol))


class BotConfigsRepository(BaseRepository):
    """봇 설정 레포지토리"""
    
    def upsert_config(self, config: Dict):
        """봇 설정 삽입/업데이트"""
        sql = """
        INSERT OR REPLACE INTO bot_configs
        (symbol, direction, interval, max_margin, margin_mode, leverage,
         martingale_enabled, martingale_steps, martingale_offset_pct,
         martingale_size_ratios, tp_offset_pct, sl_offset_pct, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        import json
        self.execute_query(sql, (
            config['symbol'], config['direction'], config['interval'],
            config['max_margin'], config['margin_mode'], config['leverage'],
            config.get('martingale_enabled', 0),
            config.get('martingale_steps', 0),
            config.get('martingale_offset_pct', 0),
            json.dumps(config.get('martingale_size_ratios', [])),
            config['tp_offset_pct'],
            config.get('sl_offset_pct'),
            config.get('is_active', 0)
        ))
    
    def get_config(self, symbol: str) -> Optional[Dict]:
        """봇 설정 조회"""
        sql = "SELECT * FROM bot_configs WHERE symbol = ?"
        return self.fetch_one(sql, (symbol,))
    
    def get_active_configs(self) -> List[Dict]:
        """활성화된 봇 설정 조회"""
        sql = "SELECT * FROM bot_configs WHERE is_active = 1"
        return self.fetch_all(sql)
    
    def set_active(self, symbol: str, is_active: bool):
        """봇 활성화 상태 변경"""
        sql = "UPDATE bot_configs SET is_active = ? WHERE symbol = ?"
        self.execute_query(sql, (1 if is_active else 0, symbol))


class AppSettingsRepository(BaseRepository):
    """앱 설정 레포지토리"""
    
    def get(self, key: str, default: str = "") -> str:
        """설정 조회"""
        sql = "SELECT value FROM app_settings WHERE key = ?"
        result = self.fetch_one(sql, (key,))
        return result['value'] if result else default
    
    def set(self, key: str, value: str):
        """설정 저장"""
        sql = """
        INSERT OR REPLACE INTO app_settings (key, value, updated_at)
        VALUES (?, ?, datetime('now'))
        """
        self.execute_query(sql, (key, value))


class BotLogsRepository(BaseRepository):
    """봇 로그 레포지토리"""
    
    def insert(self, timestamp: str, level: str, symbol: str, 
              bot_id: int, category: str, message: str, payload: str = ""):
        """봇 로그 삽입"""
        sql = """
        INSERT INTO bot_logs 
        (timestamp, level, symbol, bot_id, category, message, payload)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(sql, (timestamp, level, symbol, bot_id, 
                                category, message, payload))
    
    def get_logs(self, symbol: str = None, category: str = None,
                limit: int = 1000) -> List[Dict]:
        """봇 로그 조회"""
        conditions = []
        params = []
        
        if symbol:
            conditions.append("symbol = ?")
            params.append(symbol)
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
        SELECT * FROM bot_logs
        WHERE {where_clause}
        ORDER BY timestamp DESC LIMIT ?
        """
        params.append(limit)
        return self.fetch_all(sql, tuple(params))


class OrdersRepository(BaseRepository):
    """주문 레포지토리"""
    
    def insert_order(self, order: Dict):
        """주문 삽입"""
        sql = """
        INSERT INTO orders
        (order_id, symbol, side, type, price, size, filled_size, 
         status, bot_id, position_id, related_order_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(sql, (
            order['order_id'], order['symbol'], order['side'],
            order['type'], order.get('price'), order['size'],
            order.get('filled_size', 0), order['status'],
            order.get('bot_id'), order.get('position_id'),
            order.get('related_order_type')
        ))
    
    def update_order_status(self, order_id: str, status: str, 
                          filled_size: float = None):
        """주문 상태 업데이트"""
        if filled_size is not None:
            sql = """
            UPDATE orders SET status = ?, filled_size = ?, 
            updated_at = datetime('now')
            WHERE order_id = ?
            """
            self.execute_query(sql, (status, filled_size, order_id))
        else:
            sql = """
            UPDATE orders SET status = ?, updated_at = datetime('now')
            WHERE order_id = ?
            """
            self.execute_query(sql, (status, order_id))
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """주문 조회"""
        sql = "SELECT * FROM orders WHERE order_id = ?"
        return self.fetch_one(sql, (order_id,))


class PositionsRepository(BaseRepository):
    """포지션 레포지토리"""
    
    def insert_position(self, position: Dict) -> int:
        """포지션 삽입"""
        sql = """
        INSERT INTO positions
        (symbol, side, size, avg_price, leverage, liquidation_price,
         unrealized_pnl, realized_pnl, total_fees, bot_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        query = self.execute_query(sql, (
            position['symbol'], position['side'], position['size'],
            position['avg_price'], position['leverage'],
            position.get('liquidation_price'), position.get('unrealized_pnl', 0),
            position.get('realized_pnl', 0), position.get('total_fees', 0),
            position.get('bot_id')
        ))
        return query.lastInsertId()
    
    def update_position(self, position_id: int, updates: Dict):
        """포지션 업데이트"""
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        sql = f"""
        UPDATE positions SET {set_clause}, updated_at = datetime('now')
        WHERE id = ?
        """
        params = list(updates.values()) + [position_id]
        self.execute_query(sql, tuple(params))
    
    def get_open_position(self, symbol: str) -> Optional[Dict]:
        """열린 포지션 조회"""
        sql = """
        SELECT * FROM positions 
        WHERE symbol = ? AND is_closed = 0
        ORDER BY created_at DESC LIMIT 1
        """
        return self.fetch_one(sql, (symbol,))
    
    def close_position(self, position_id: int, realized_pnl: float):
        """포지션 종료"""
        sql = """
        UPDATE positions 
        SET is_closed = 1, realized_pnl = ?, closed_at = datetime('now')
        WHERE id = ?
        """
        self.execute_query(sql, (realized_pnl, position_id))


class TradesHistoryRepository(BaseRepository):
    """거래 내역 레포지토리"""
    
    def insert_trade(self, trade: Dict):
        """거래 내역 삽입"""
        sql = """
        INSERT INTO trades_history
        (symbol, side, entry_price, exit_price, size, leverage,
         pnl, fees, entry_time, exit_time, exit_reason, bot_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(sql, (
            trade['symbol'], trade['side'], trade['entry_price'],
            trade['exit_price'], trade['size'], trade['leverage'],
            trade['pnl'], trade['fees'], trade['entry_time'],
            trade['exit_time'], trade.get('exit_reason'), trade.get('bot_id')
        ))
    
    def get_trades(self, symbol: str = None, start_date: str = None,
                  end_date: str = None) -> List[Dict]:
        """거래 내역 조회"""
        conditions = []
        params = []
        
        if symbol:
            conditions.append("symbol = ?")
            params.append(symbol)
        
        if start_date:
            conditions.append("exit_time >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("exit_time <= ?")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
        SELECT * FROM trades_history
        WHERE {where_clause}
        ORDER BY exit_time DESC
        """
        return self.fetch_all(sql, tuple(params))
    
    def get_statistics(self, symbol: str = None, start_date: str = None,
                      end_date: str = None) -> Dict:
        """거래 통계 조회"""
        trades = self.get_trades(symbol, start_date, end_date)
        
        if not trades:
            return {
                "total_trades": 0,
                "total_profit": 0,
                "total_loss": 0,
                "net_pnl": 0,
                "win_rate": 0,
                "max_consecutive_losses": 0,
                "max_drawdown": 0
            }
        
        total_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        total_loss = sum(t['pnl'] for t in trades if t['pnl'] < 0)
        win_count = sum(1 for t in trades if t['pnl'] > 0)
        
        # 최대 연속 손실
        max_consecutive_losses = 0
        current_losses = 0
        for trade in trades:
            if trade['pnl'] < 0:
                current_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
            else:
                current_losses = 0
        
        # 최대 드로다운 (간단 계산)
        cumulative = 0
        peak = 0
        max_dd = 0
        for trade in reversed(trades):
            cumulative += trade['pnl']
            peak = max(peak, cumulative)
            dd = peak - cumulative
            max_dd = max(max_dd, dd)
        
        return {
            "total_trades": len(trades),
            "total_profit": total_profit,
            "total_loss": total_loss,
            "net_pnl": total_profit + total_loss,
            "win_rate": (win_count / len(trades) * 100) if trades else 0,
            "max_consecutive_losses": max_consecutive_losses,
            "max_drawdown": max_dd
        }


