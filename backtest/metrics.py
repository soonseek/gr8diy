"""
백테스트 성과 지표 계산
"""
import math
from typing import List, Dict
from datetime import datetime


class BacktestMetrics:
    """백테스트 성과 지표 계산"""
    
    @staticmethod
    def calculate(trades: List, equity_curve: List[Dict], 
                 initial_capital: float, final_capital: float) -> Dict:
        """
        모든 성과 지표 계산
        
        Args:
            trades: 거래 리스트
            equity_curve: 자산 곡선 [{timestamp, equity, price}, ...]
            initial_capital: 초기 자본
            final_capital: 최종 자본
        
        Returns:
            성과 지표 딕셔너리
        """
        # 기본 지표
        total_return = ((final_capital - initial_capital) / initial_capital) * 100
        
        # 거래 통계
        total_trades = len(trades)
        
        if total_trades == 0:
            return {
                'total_return': 0,
                'cagr': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'win_rate': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_martingale_level': 0,
                'avg_martingale_level': 0,
                'total_fees': 0
            }
        
        # 승패 분류
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]
        
        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
        
        # 평균 수익/손실
        avg_profit = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Profit Factor
        total_profit = sum(t.pnl for t in winning_trades)
        total_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # 총 수수료
        total_fees = sum(t.fees for t in trades)
        
        # 마틴게일 통계
        martingale_levels = [t.martingale_level for t in trades]
        max_martingale_level = max(martingale_levels) if martingale_levels else 0
        avg_martingale_level = sum(martingale_levels) / len(martingale_levels) if martingale_levels else 0
        
        # 최대 낙폭 (MDD)
        max_drawdown = BacktestMetrics.calculate_max_drawdown(equity_curve)
        
        # CAGR (연환산 수익률)
        cagr = BacktestMetrics.calculate_cagr(equity_curve, initial_capital, final_capital)
        
        # 샤프 비율
        sharpe_ratio = BacktestMetrics.calculate_sharpe_ratio(equity_curve)
        
        # 소르티노 비율
        sortino_ratio = BacktestMetrics.calculate_sortino_ratio(equity_curve)
        
        return {
            'total_return': round(total_return, 2),
            'cagr': round(cagr, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'sortino_ratio': round(sortino_ratio, 3),
            'win_rate': round(win_rate, 2),
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 999.99,
            'max_martingale_level': max_martingale_level,
            'avg_martingale_level': round(avg_martingale_level, 2),
            'total_fees': round(total_fees, 2)
        }
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[Dict]) -> float:
        """
        최대 낙폭 계산
        
        Returns:
            최대 낙폭 (%)
        """
        if not equity_curve:
            return 0
        
        peak = equity_curve[0]['equity']
        max_dd = 0
        
        for point in equity_curve:
            equity = point['equity']
            peak = max(peak, equity)
            
            if peak > 0:
                dd = ((peak - equity) / peak) * 100
                max_dd = max(max_dd, dd)
        
        return max_dd
    
    @staticmethod
    def calculate_cagr(equity_curve: List[Dict], initial_capital: float, 
                      final_capital: float) -> float:
        """
        연환산 수익률 (CAGR) 계산
        
        Returns:
            CAGR (%)
        """
        if not equity_curve or len(equity_curve) < 2:
            return 0
        
        try:
            start_time = datetime.fromisoformat(equity_curve[0]['timestamp'])
            end_time = datetime.fromisoformat(equity_curve[-1]['timestamp'])
            
            days = (end_time - start_time).days
            if days <= 0:
                return 0
            
            years = days / 365.0
            
            if initial_capital <= 0 or final_capital < 0:
                return 0
            
            total_return = final_capital / initial_capital
            
            if total_return <= 0:
                return -100
            
            cagr = (math.pow(total_return, 1 / years) - 1) * 100
            return cagr
            
        except Exception:
            return 0
    
    @staticmethod
    def calculate_sharpe_ratio(equity_curve: List[Dict], 
                               risk_free_rate: float = 0.02) -> float:
        """
        샤프 비율 계산
        
        Args:
            equity_curve: 자산 곡선
            risk_free_rate: 무위험 수익률 (연간, 기본 2%)
        
        Returns:
            샤프 비율
        """
        if len(equity_curve) < 2:
            return 0
        
        # 일일 수익률 계산
        returns = []
        for i in range(1, len(equity_curve)):
            prev_equity = equity_curve[i-1]['equity']
            curr_equity = equity_curve[i]['equity']
            
            if prev_equity > 0:
                daily_return = (curr_equity - prev_equity) / prev_equity
                returns.append(daily_return)
        
        if not returns:
            return 0
        
        # 평균 수익률
        avg_return = sum(returns) / len(returns)
        
        # 표준편차
        if len(returns) < 2:
            return 0
        
        variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0
        
        # 연환산 (일일 데이터 기준)
        daily_rf = risk_free_rate / 365
        
        sharpe = (avg_return - daily_rf) / std_dev * math.sqrt(365)
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(equity_curve: List[Dict], 
                                risk_free_rate: float = 0.02) -> float:
        """
        소르티노 비율 계산 (하방 변동성만 고려)
        
        Args:
            equity_curve: 자산 곡선
            risk_free_rate: 무위험 수익률 (연간)
        
        Returns:
            소르티노 비율
        """
        if len(equity_curve) < 2:
            return 0
        
        # 일일 수익률 계산
        returns = []
        for i in range(1, len(equity_curve)):
            prev_equity = equity_curve[i-1]['equity']
            curr_equity = equity_curve[i]['equity']
            
            if prev_equity > 0:
                daily_return = (curr_equity - prev_equity) / prev_equity
                returns.append(daily_return)
        
        if not returns:
            return 0
        
        # 평균 수익률
        avg_return = sum(returns) / len(returns)
        
        # 하방 편차 (음수 수익률만)
        negative_returns = [r for r in returns if r < 0]
        
        if not negative_returns:
            return float('inf') if avg_return > 0 else 0
        
        downside_variance = sum(r ** 2 for r in negative_returns) / len(negative_returns)
        downside_std = math.sqrt(downside_variance)
        
        if downside_std == 0:
            return 0
        
        # 연환산
        daily_rf = risk_free_rate / 365
        
        sortino = (avg_return - daily_rf) / downside_std * math.sqrt(365)
        return sortino
    
    @staticmethod
    def calculate_calmar_ratio(equity_curve: List[Dict], initial_capital: float,
                              final_capital: float) -> float:
        """
        칼마 비율 계산 (CAGR / MDD)
        
        Returns:
            칼마 비율
        """
        cagr = BacktestMetrics.calculate_cagr(equity_curve, initial_capital, final_capital)
        mdd = BacktestMetrics.calculate_max_drawdown(equity_curve)
        
        if mdd == 0:
            return float('inf') if cagr > 0 else 0
        
        return cagr / mdd
    
    @staticmethod
    def calculate_win_streak(trades: List) -> Dict:
        """
        연속 승/패 통계 계산
        
        Returns:
            {max_win_streak, max_loss_streak, current_streak}
        """
        if not trades:
            return {'max_win_streak': 0, 'max_loss_streak': 0, 'current_streak': 0}
        
        max_win = 0
        max_loss = 0
        current = 0
        
        for trade in trades:
            if trade.pnl > 0:
                if current > 0:
                    current += 1
                else:
                    current = 1
                max_win = max(max_win, current)
            elif trade.pnl < 0:
                if current < 0:
                    current -= 1
                else:
                    current = -1
                max_loss = max(max_loss, abs(current))
            else:
                current = 0
        
        return {
            'max_win_streak': max_win,
            'max_loss_streak': max_loss,
            'current_streak': current
        }

