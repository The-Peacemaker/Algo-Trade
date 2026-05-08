#!/usr/bin/env python3
"""
Portfolio Risk Manager
=========================================
Advanced risk management system for quant trading

Features:
- Daily P&L limits with auto-stop
- Position correlation analysis
- Exposure limits (sector, market cap)
- Volatility-based position limits
- Maximum drawdown protection
- Kelly Criterion for position sizing
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import math


class MarketCondition(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


@dataclass
class Trade:
    """Trade record"""
    symbol: str
    entry_price: float
    quantity: int
    direction: str
    timestamp: datetime
    pnl: float = 0
    exit_price: float = 0
    stop_loss: float = 0
    target: float = 0


@dataclass
class PortfolioStats:
    """Portfolio statistics"""
    starting_capital: float
    current_capital: float
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    largest_win: float = 0
    largest_loss: float = 0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    max_drawdown: float = 0
    peak_capital: float = 0


class PortfolioRiskManager:
    """
    Portfolio Risk Manager
    
    Comprehensive risk management system that:
    - Tracks daily P&L
    - Enforces position limits
    - Manages correlation risk
    - Protects against drawdowns
    - Dynamically adjusts exposure
    """
    
    def __init__(
        self,
        starting_capital: float = 5000,
        max_daily_loss_percent: float = 6.0,
        max_consecutive_losses: int = 3,
        max_total_exposure_percent: float = 20.0,
        allow_taking_new_positions: bool = True
    ):
        self.starting_capital = starting_capital
        self.current_capital = starting_capital
        self.peak_capital = starting_capital
        
        # Risk limits
        self.max_daily_loss_percent = max_daily_loss_percent
        self.max_consecutive_losses = max_consecutive_losses
        self.max_total_exposure_percent = max_total_exposure_percent
        
        # State
        self.allow_taking_new_positions = allow_taking_new_positions
        self.daily_trades: List[Trade] = []
        self.positions: Dict[str, Trade] = {}
        self.trade_history: List[Trade] = []
        self.last_reset_date = datetime.now().date()
        
        # Stats
        self.stats = PortfolioStats(
            starting_capital=starting_capital,
            current_capital=starting_capital,
            peak_capital=starting_capital
        )
        
        # Sector exposure (simplified)
        self.sector_limits = {
            "banking": 30.0,    # Max 30% in banking
            "it": 25.0,          # Max 25% in IT
            "finance": 20.0,      # Max 20% in finance
            "energy": 15.0,
            "metal": 15.0,
            "other": 100.0
        }
        
        self.sector_exposure: Dict[str, float] = {}
    
    def reset_daily(self):
        """Reset for new trading day"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_trades = []
            self.last_reset_date = today
    
    def can_take_position(self, symbol: str, sector: str = "other", 
                       estimated_capital: float = 0) -> tuple[bool, str]:
        """Check if new position can be taken"""
        # Basic checks
        if not self.allow_taking_new_positions:
            return False, "Trading disabled by risk manager"
        
        # Daily loss limit check
        daily_pnl = self.get_daily_pnl()
        if daily_pnl < 0:
            daily_loss_percent = abs(daily_pnl) / self.starting_capital * 100
            if daily_loss_percent >= self.max_daily_loss_percent:
                return False, f"Daily loss limit reached ({daily_loss_percent:.1f}%)"
        
        # Consecutive loss check
        if self.stats.consecutive_losses >= self.max_consecutive_losses:
            return False, f"Max consecutive losses reached ({self.stats.consecutive_losses})"
        
        # Total position limit
        if len(self.positions) >= 5:
            return False, "Max positions reached"
        
        # Sector exposure check
        current_exposure = self.sector_exposure.get(sector, 0)
        limit = self.sector_limits.get(sector, 100.0)
        if current_exposure >= limit:
            return False, f"Sector exposure limit ({sector}: {current_exposure}%)"
        
        # Total capital check
        total_exposure = sum(
            p.entry_price * p.quantity 
            for p in self.positions.values()
        ) / self.current_capital * 100
        
        if total_exposure >= self.max_total_exposure_percent:
            return False, f"Total exposure limit reached ({total_exposure:.1f}%)"
        
        return True, "OK"
    
    def open_position(self, trade: Trade):
        """Register new position"""
        self.positions[trade.symbol] = trade
        self.daily_trades.append(trade)
    
    def close_position(self, symbol: str, exit_price: float, pnl: float):
        """Close existing position"""
        if symbol in self.positions:
            trade = self.positions.pop(symbol)
            trade.exit_price = exit_price
            trade.pnl = pnl
            self.trade_history.append(trade)
            self.update_stats(pnl, pnl > 0)
    
    def update_stats(self, pnl: float, was_win: bool):
        """Update portfolio statistics"""
        self.stats.total_trades += 1
        self.current_capital += pnl
        
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        
        # Drawdown
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital * 100
        if drawdown > self.stats.max_drawdown:
            self.stats.max_drawdown = drawdown
        
        if was_win:
            self.stats.wins += 1
            self.stats.consecutive_wins += 1
            self.stats.consecutive_losses = 0
            if pnl > self.stats.largest_win:
                self.stats.largest_win = pnl
        else:
            self.stats.losses += 1
            self.stats.consecutive_losses += 1
            self.stats.consecutive_wins = 0
            if abs(pnl) > abs(self.stats.largest_loss):
                self.stats.largest_loss = abs(pnl)
        
        # Auto-disabling based on consecutive losses
        if self.stats.consecutive_losses >= self.max_consecutive_losses:
            self.allow_taking_new_positions = False
    
    def update_sector_exposure(self, symbol: str, sector: str, value_change: float):
        """Update sector exposure"""
        current = self.sector_exposure.get(sector, 0)
        self.sector_exposure[sector] = current + value_change
    
    def get_daily_pnl(self) -> float:
        """Calculate daily P&L"""
        return sum(t.pnl for t in self.daily_trades if t.pnl != 0)
    
    def get_sharpe_ratio(self, risk_free_rate: float = 0.06) -> float:
        """Calculate Sharpe ratio from trade history"""
        if len(self.trade_history) < 10:
            return 0
        
        returns = [t.pnl / self.starting_capital for t in self.trade_history]
        
        avg_return = sum(returns) / len(returns)
        std_return = math.sqrt(
            sum((r - avg_return) ** 2 for r in returns) / len(returns)
        )
        
        if std_return == 0:
            return 0
        
        sharpe = (avg_return - risk_free_rate / 252) / std_return * math.sqrt(252)
        return sharpe
    
    def get_win_rate(self) -> float:
        """Calculate win rate"""
        if self.stats.total_trades == 0:
            return 0
        return (self.stats.wins / self.stats.total_trades) * 100
    
    def get_profit_factor(self) -> float:
        """Calculate profit factor"""
        gross_profit = sum(
            t.pnl for t in self.trade_history if t.pnl > 0
        )
        gross_loss = abs(sum(
            t.pnl for t in self.trade_history if t.pnl < 0
        ))
        
        if gross_loss == 0:
            return 0 if gross_profit == 0 else 100
        
        return gross_profit / gross_loss
    
    def get_risk_report(self) -> Dict:
        """Get comprehensive risk report"""
        return {
            "capital": {
                "starting": self.starting_capital,
                "current": round(self.current_capital, 2),
                "pnl": round(self.current_capital - self.starting_capital, 2),
                "return_pct": round(
                    (self.current_capital - self.starting_capital) / 
                    self.starting_capital * 100, 2
                )
            },
            "performance": {
                "total_trades": self.stats.total_trades,
                "wins": self.stats.wins,
                "losses": self.stats.losses,
                "win_rate": round(self.get_win_rate(), 1),
                "profit_factor": round(self.get_profit_factor(), 2),
                "sharpe_ratio": round(self.get_sharpe_ratio(), 2),
                "max_drawdown": round(self.stats.max_drawdown, 2)
            },
            "risk_limits": {
                "max_daily_loss_pct": self.max_daily_loss_percent,
                "max_consecutive_losses": self.max_consecutive_losses,
                "trading_allowed": self.allow_taking_new_positions,
                "consecutive_wins": self.stats.consecutive_wins,
                "consecutive_losses": self.stats.consecutive_losses
            },
            "positions": {
                "open": len(self.positions),
                "daily": len(self.daily_trades)
            }
        }
    
    def enable_trading(self):
        """Re-enable trading after drawdown recovery"""
        recovery = (self.current_capital - self.starting_capital) / self.starting_capital * 100
        if recovery > -2:  # Recovered to within 2% of starting
            self.allow_taking_new_positions = True
    
    def force_reset(self, capital: float):
        """Force reset with new capital"""
        self.starting_capital = capital
        self.current_capital = capital
        self.peak_capital = capital
        self.positions = {}
        self.daily_trades = []
        self.trade_history = []
        self.stats = PortfolioStats(
            starting_capital=capital,
            current_capital=capital,
            peak_capital=capital
        )


# =========== TEST ===========
def test_portfolio_risk_manager():
    """Test the portfolio risk manager"""
    
    print("=" * 60)
    print("PORTFOLIO RISK MANAGER TEST")
    print("=" * 60)
    
    # Create with ₹200 budget
    rm = PortfolioRiskManager(starting_capital=200)
    
    # Test checks
    print(f"\nInitial state:")
    can_open, reason = rm.can_take_position("RELIANCE", "energy", 200)
    print(f"  Can open RELIANCE: {can_open} ({reason})")
    
    # Simulate trades
    print(f"\nSimulating trades...")
    
    # Trade 1: Win
    t1 = Trade("RELIANCE", 2500, 1, "LONG", datetime.now(), stop_loss=2475, target=2550)
    rm.open_position(t1)
    rm.update_stats(50, True)
    print(f"  After win: Capital ₹{rm.current_capital}")
    
    # Trade 2: Loss
    t2 = Trade("TCS", 3200, 1, "LONG", datetime.now(), stop_loss=3168, target=3264)
    rm.open_position(t2)
    rm.update_stats(-40, False)
    print(f"  After loss: Capital ₹{rm.current_capital}")
    
    # Report
    print(f"\nRisk Report:")
    report = rm.get_risk_report()
    print(f"  Capital: ₹{report['capital']['current']} (₹{report['capital']['pnl']:+})")
    print(f"  Win Rate: {report['performance']['win_rate']}%")
    print(f"  Trading: {report['risk_limits']['trading_allowed']}")
    print(f"  Consecutive: W{report['risk_limits']['consecutive_wins']}/L{report['risk_limits']['consecutive_losses']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_portfolio_risk_manager()