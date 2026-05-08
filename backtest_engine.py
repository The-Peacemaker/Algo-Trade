#!/usr/bin/env python3
"""
Backtest Engine with Advanced Analytics
=========================================
Professional backtesting with:

- Equity curve generation
- Sharpe ratio calculation
- Maximum drawdown
- Trade-level analytics
- Win/Loss distribution
- Monthly/Daily breakdowns
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math


@dataclass
class BacktestTrade:
    """Backtest trade record"""
    symbol: str
    entry_price: float
    exit_price: float
    quantity: int
    direction: str
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_percent: float
    holding_period: int  # minutes
    
    # Entry conditions
    entry_signal: str = ""
    confidence: float = 0
    
    # Exit conditions
    exit_reason: str = ""  # target, stop_loss, time, signal


@dataclass
class BacktestResults:
    """Comprehensive backtest results"""
    # Capital
    starting_capital: float
    ending_capital: float
    total_return: float
    total_return_percent: float
    
    # Trade Stats
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Profit Metrics
    gross_profit: float
    gross_loss: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    avg_trade: float
    
    # Risk Metrics
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    
    # Trade Distribution
    avg_holding_time: int
    longest_trade: int
    shortest_trade: int
    
    # Time Analytics
    trades_by_hour: Dict = field(default_factory=dict)
    trades_by_day: Dict = field(default_factory=dict)
    monthly_returns: Dict = field(default_factory=dict)
    
    # Equity Curve
    equity_curve: List[Dict] = field(default_factory=list)


class BacktestEngine:
    """
    Professional Backtest Engine
    
    Comprehensive backtesting with:
    - Trade simulation
    - Equity curve
    - Risk analytics
    - Performance metrics
    """
    
    def __init__(
        self,
        starting_capital: float = 5000,
        commission: float = 0,
        slippage: float = 0
    ):
        self.starting_capital = starting_capital
        self.commission = commission
        self.slippage = slippage
        
        # State
        self.current_capital = starting_capital
        self.trades: List[BacktestTrade] = []
        self.equity_curve = [{"date": datetime.now(), "capital": starting_capital}]
        
        # Daily tracking
        self.daily_trades: Dict[str, List] = {}
        self.daily_pnl: Dict[str, float] = {}
        
        # Performance
        self.wins = []
        self.losses = []
    
    def run_trade(
        self,
        symbol: str,
        entry_price: float,
        exit_price: float,
        quantity: int,
        direction: str,
        entry_time: datetime,
        exit_time: datetime,
        exit_reason: str = "target",
        entry_signal: str = "",
        confidence: float = 0
    ) -> BacktestTrade:
        """Execute a backtest trade"""
        
        # Calculate P&L
        if direction == "LONG":
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity
        
        # Apply costs
        entry_cost = entry_price * quantity
        exit_cost = exit_price * quantity
        total_commission = (entry_cost + exit_cost) * self.commission
        
        # Slippage (simplified)
        slip = (entry_cost + exit_cost) * self.slippage
        
        net_pnl = pnl - total_commission - slip
        pnl_percent = (net_pnl / entry_cost) * 100
        
        # Holding time
        holding_minutes = int((exit_time - entry_time).total_seconds() / 60)
        
        trade = BacktestTrade(
            symbol=symbol,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            direction=direction,
            entry_time=entry_time,
            exit_time=exit_time,
            pnl=net_pnl,
            pnl_percent=pnl_percent,
            holding_period=holding_minutes,
            entry_signal=entry_signal,
            confidence=confidence,
            exit_reason=exit_reason
        )
        
        # Update capital
        self.current_capital += net_pnl
        
        # Store trade
        self.trades.append(trade)
        
        # Track for analytics
        if net_pnl > 0:
            self.wins.append(net_pnl)
        else:
            self.losses.append(net_pnl)
        
        # Daily tracking
        day = entry_time.strftime("%Y-%m-%d")
        if day not in self.daily_trades:
            self.daily_trades[day] = []
            self.daily_pnl[day] = 0
        self.daily_trades[day].append(trade)
        self.daily_pnl[day] += net_pnl
        
        # Update equity curve
        self.equity_curve.append({
            "date": exit_time,
            "capital": self.current_capital,
            "pnl": net_pnl
        })
        
        return trade
    
    def calculate_results(self) -> BacktestResults:
        """Calculate comprehensive backtest results"""
        
        if not self.trades:
            return BacktestResults(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Basic stats
        total_trades = len(self.trades)
        winning = len(self.wins)
        losing = len(self.losses)
        win_rate = (winning / total_trades * 100) if total_trades > 0 else 0
        
        # Returns
        total_return = self.current_capital - self.starting_capital
        return_pct = (total_return / self.starting_capital * 100)
        
        # Profit metrics
        gross_profit = sum(self.wins)
        gross_loss = abs(sum(self.losses)) if self.losses else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        avg_win = gross_profit / winning if winning > 0 else 0
        avg_loss = gross_loss / losing if losing > 0 else 0
        avg_trade = total_return / total_trades if total_trades > 0 else 0
        
        # Risk metrics - calculate drawdown
        peak = self.starting_capital
        max_dd = 0
        max_dd_pct = 0
        
        for point in self.equity_curve:
            if point["capital"] > peak:
                peak = point["capital"]
            dd = peak - point["capital"]
            dd_pct = (dd / peak * 100) if peak > 0 else 0
            
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct
        
        # Sharpe (simplified)
        returns = [t["pnl"] / self.starting_capital for t in self.equity_curve[1:]]
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = math.sqrt(
            sum((r - avg_return) ** 2 for r in returns) / len(returns)
        ) if returns else 1
        
        sharpe = (avg_return / std_return * math.sqrt(252)) if std_return > 0 else 0
        
        # Sortino (downside deviation)
        downside = [r for r in returns if r < 0]
        downside_std = math.sqrt(
            sum(r ** 2 for r in downside) / len(downside)
        ) if downside else 1
        sortino = (avg_return / downside_std * math.sqrt(252)) if downside_std > 0 else 0
        
        # Time analytics
        holding_times = [t.holding_period for t in self.trades]
        avg_hold = sum(holding_times) / len(holding_times) if holding_times else 0
        
        # Hour distribution
        hour_dist = {}
        for t in self.trades:
            h = t.entry_time.hour
            hour_dist[h] = hour_dist.get(h, 0) + 1
        
        # Day distribution
        day_dist = {}
        for t in self.trades:
            d = t.entry_time.strftime("%A")
            day_dist[d] = day_dist.get(d, 0) + 1
        
        # Monthly returns
        monthly = {}
        for t in self.trades:
            m = t.entry_time.strftime("%Y-%m")
            if m not in monthly:
                monthly[m] = 0
            monthly[m] += t.pnl
        
        return BacktestResults(
            starting_capital=self.starting_capital,
            ending_capital=round(self.current_capital, 2),
            total_return=round(total_return, 2),
            total_return_percent=round(return_pct, 2),
            total_trades=total_trades,
            winning_trades=winning,
            losing_trades=losing,
            win_rate=round(win_rate, 1),
            gross_profit=round(gross_profit, 2),
            gross_loss=round(gross_loss, 2),
            profit_factor=round(profit_factor, 2),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            avg_trade=round(avg_trade, 2),
            max_drawdown=round(max_dd, 2),
            max_drawdown_percent=round(max_dd_pct, 2),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            avg_holding_time=int(avg_hold),
            longest_trade=max(holding_times) if holding_times else 0,
            shortest_trade=min(holding_times) if holding_times else 0,
            trades_by_hour=hour_dist,
            trades_by_day=day_dist,
            monthly_returns=monthly,
            equity_curve=self.equity_curve
        )
    
    def print_report(self):
        """Print formatted backtest report"""
        results = self.calculate_results()
        
        print("=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)
        
        print(f"\n📊 CAPITAL PERFORMANCE")
        print(f"  Starting:      ₹{results.starting_capital:,.0f}")
        print(f"  Ending:        ₹{results.ending_capital:,.0f}")
        print(f"  Total Return: ₹{results.total_return:+,.0f} ({results.total_return_percent:+.1f}%)")
        
        print(f"\n📈 TRADE STATISTICS")
        print(f"  Total Trades:    {results.total_trades}")
        print(f"  Winning:         {results.winning_trades}")
        print(f"  Losing:          {results.losing_trades}")
        print(f"  Win Rate:        {results.win_rate}%")
        
        print(f"\n💰 PROFIT METRICS")
        print(f"  Gross Profit:    ₹{results.gross_profit:+,.0f}")
        print(f"  Gross Loss:     ₹{results.gross_loss:,.0f}")
        print(f"  Profit Factor:   {results.profit_factor:.2f}")
        print(f"  Avg Win:         ₹{results.avg_win:+,.0f}")
        print(f"  Avg Loss:       ₹{results.avg_loss:,.0f}")
        
        print(f"\n⚠️ RISK METRICS")
        print(f"  Max Drawdown:    ₹{results.max_drawdown:,.0f} ({results.max_drawdown_percent:.1f}%)")
        print(f"  Sharpe Ratio:   {results.sharpe_ratio:.2f}")
        print(f"  Sortino Ratio:  {results.sortino_ratio:.2f}")
        
        print(f"\n⏱️ TIME METRICS")
        print(f"  Avg Hold Time:   {results.avg_holding_time} min")
        print(f"  Longest:        {results.longest_trade} min")
        print(f"  Shortest:       {results.shortest_trade} min")
        
        if results.trades_by_hour:
            print(f"\n🕐 BEST HOURS")
            top_hours = sorted(
                results.trades_by_hour.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            for h, c in top_hours:
                print(f"  {h}:00 - {c} trades")
        
        print("=" * 70)
        
        return results


# ============ TEST ===========
def test_backtest():
    """Test backtest engine"""
    
    print("=" * 60)
    print("BACKTEST ENGINE TEST")
    print("=" * 60)
    
    engine = BacktestEngine(starting_capital=5000)
    
    # Simulate 20 trades
    import random
    from datetime import datetime, timedelta
    
    base_price = 2500
    for i in range(20):
        price = base_price + random.uniform(-50, 50)
        
        # Random win/loss
        is_win = random.random() > 0.5
        if is_win:
            exit_price = price * 1.02
        else:
            exit_price = price * 0.98
        
        trade = engine.run_trade(
            symbol="RELIANCE",
            entry_price=price,
            exit_price=exit_price,
            quantity=random.randint(1, 5),
            direction="LONG",
            entry_time=datetime.now() - timedelta(days=20-i),
            exit_time=datetime.now() - timedelta(days=20-i) + timedelta(minutes=30),
            exit_reason="target" if is_win else "stop_loss",
            confidence=random.randint(60, 90)
        )
    
    # Report
    engine.print_report()
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_backtest()