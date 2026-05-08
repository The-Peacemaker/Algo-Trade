#!/usr/bin/env python3
"""
Live Backtest with Real NSE Data
============================
Complete backtest system using real market data.
Shows actual trade signals and performance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class TradeSignal:
    """Trade signal"""
    symbol: str
    entry_time: datetime
    price: float
    signal_type: str  # BUY, SELL
    confidence: int
    stop_loss: float
    target: float
    quantity: int
    candle_pattern: str = ""
    rsi: float = 50
    trend: str = "sideways"


@dataclass
class BacktestTrade:
    """Executed trade"""
    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float
    pnl_percent: float
    reason: str  # target, stop_loss, time
    holding_minutes: int
    confidence: int


class RealBacktester:
    """Real data backtester"""
    
    def __init__(self, starting_capital: float = 5000):
        self.capital = starting_capital
        self.starting_capital = starting_capital
        self.trades: List[BacktestTrade] = []
        self.positions: Dict[str, dict] = {}
        
    def fetch_historical(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Fetch historical data"""
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            df = ticker.history(period=f"{days}d", interval="5m")
            return df
        except:
            return pd.DataFrame()
    
    def analyze_bar(self, df: pd.DataFrame, idx: int) -> Dict:
        """Analyze single bar"""
        if idx < 50:
            return {"signal": "neutral", "confidence": 0}
        
        data = df.iloc[:idx+1]
        current = df.iloc[idx]
        prev = df.iloc[idx-1] if idx > 0 else current
        
        close = current['Close']
        
        # Calculate indicators on the fly
        sma_9 = data['Close'].iloc[-9:].mean()
        sma_20 = data['Close'].iloc[-20:].mean()
        
        # RSI
        deltas = data['Close'].diff()
        gains = deltas.clip(lower=0)
        losses = -deltas.clip(upper=0)
        avg_gain = gains.iloc[-14:].mean()
        avg_loss = losses.iloc[-14:].mean()
        if avg_loss == 0:
            rsi = 70
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = data['Close'].ewm(span=12).mean().iloc[-1]
        ema_26 = data['Close'].ewm(span=26).mean().iloc[-1]
        macd = ema_12 - ema_26
        
        # Volume
        avg_vol = data['Volume'].iloc[-20:].mean()
        vol_ratio = current['Volume'] / avg_vol
        
        # VWAP
        pv = (data['Close'] * data['Volume']).sum()
        v = data['Volume'].sum()
        vwap = pv / v if v > 0 else close
        
        # Score
        score = 0
        
        if close > sma_20:
            score += 15
        else:
            score -= 15
        
        if rsi < 35:
            score += 20
        elif rsi > 65:
            score -= 20
        elif rsi < 45:
            score += 5
        
        if macd > 0:
            score += 10
        else:
            score -= 10
        
        if vol_ratio > 1.5:
            score += 5
        
        if close > vwap:
            score += 5
        else:
            score -= 5
        
        # Candle patterns
        trend = "bullish" if sma_9 > sma_20 else "bearish" if sma_9 < sma_20 else "sideways"
        
        # Determine signal
        if score >= 40:
            sig = "strong_buy"
            conf = min(score, 100)
        elif score >= 20:
            sig = "buy"
            conf = score - 20
        elif score <= -40:
            sig = "strong_sell"
            conf = min(abs(score), 100)
        elif score <= -20:
            sig = "sell"
            conf = abs(score) - 20
        else:
            sig = "neutral"
            conf = abs(score)
        
        # Stop loss and target
        atr = (data['High'] - data['Low']).iloc[-14:].mean()
        stop_loss = close - (atr * 1.5)
        target = close + (atr * 2)
        
        return {
            "signal": sig,
            "confidence": conf,
            "price": close,
            "rsi": rsi,
            "macd": macd,
            "trend": trend,
            "sma_9": sma_9,
            "sma_20": sma_20,
            "stop_loss": round(stop_loss, 2),
            "target": round(target, 2),
            "atr": round(atr, 2),
            "volume_ratio": round(vol_ratio, 2),
            "vwap": round(vwap, 2)
        }
    
    def run_backtest(self, symbol: str, days: int = 30) -> List[BacktestTrade]:
        """Run backtest on a symbol"""
        print(f"\n{'='*60}")
        print(f"BACKTEST: {symbol}")
        print(f"{'='*60}")
        
        df = self.fetch_historical(symbol, days)
        
        if len(df) < 100:
            print(f"Insufficient data")
            return []
        
        print(f"Data: {len(df)} bars loaded")
        
        trades = []
        position = None
        
        for i in range(50, len(df) - 1):
            current_time = df.index[i].to_pydatetime()
            analysis = self.analyze_bar(df, i)
            
            sig = analysis["signal"]
            price = analysis["price"]
            conf = analysis["confidence"]
            
            if position:
                # Check exit conditions
                exit_reason = ""
                exit_price = price
                
                # Stop loss hit
                if price <= position["stop_loss"]:
                    exit_reason = "stop_loss"
                    exit_price = position["stop_loss"]
                # Target hit
                elif price >= position["target"]:
                    exit_reason = "target"
                    exit_price = position["target"]
                # Time exit (2 hours)
                elif (current_time - position["entry_time"]).total_seconds() > 7200:
                    exit_reason = "time"
                
                if exit_reason:
                    pnl = (exit_price - position["price"]) * position["quantity"]
                    pnl_pct = (pnl / (position["price"] * position["quantity"])) * 100
                    
                    trade = BacktestTrade(
                        symbol=symbol,
                        entry_time=position["entry_time"],
                        exit_time=current_time,
                        entry_price=position["price"],
                        exit_price=exit_price,
                        quantity=position["quantity"],
                        pnl=round(pnl, 2),
                        pnl_percent=round(pnl_pct, 2),
                        reason=exit_reason,
                        holding_minutes=int((current_time - position["entry_time"]).total_seconds() / 60),
                        confidence=position["confidence"]
                    )
                    trades.append(trade)
                    position = None
            
            # Entry signal
            if not position and conf >= 30:
                if sig in ["buy", "strong_buy"]:
                    # Calculate quantity
                    qty = max(1, int(self.capital * 0.1 / price))
                    
                    position = {
                        "symbol": symbol,
                        "entry_time": current_time,
                        "price": price,
                        "quantity": qty,
                        "stop_loss": analysis["stop_loss"],
                        "target": analysis["target"],
                        "confidence": conf,
                        "entry_reason": sig
                    }
                    
                    print(f"  → BUY at ₹{price:.2f} | SL:₹{analysis['stop_loss']:.2f} | Tgt:₹{analysis['target']:.2f} | Conf:{conf}%")
        
        self.trades.extend(trades)
        return trades
    
    def calculate_stats(self) -> Dict:
        """Calculate statistics"""
        if not self.trades:
            return {"total": 0, "wins": 0, "losses": 0}
        
        wins = [t for t in self.trades if t.pnl > 0]
        losses = [t for t in self.trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in self.trades)
        win_rate = len(wins) / len(self.trades) * 100
        
        avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.pnl for t in losses) / len(losses) if losses else 0
        
        # Sharpe
        returns = [t.pnl_percent for t in self.trades]
        avg_ret = sum(returns) / len(returns)
        std = (sum((r - avg_ret) ** 2 for r in returns) / len(returns)) ** 0.5
        sharpe = (avg_ret / std * (252 * 6.5) ** 0.5) if std > 0 else 0
        
        # Max drawdown
        peak = self.starting_capital
        dd = 0
        capital = self.starting_capital
        for t in self.trades:
            capital += t.pnl
            if capital > peak:
                peak = capital
            drawdown = peak - capital
            if drawdown > dd:
                dd = drawdown
        
        return {
            "total": len(self.trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 1),
            "total_pnl": round(total_pnl, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "sharpe": round(sharpe, 2),
            "max_dd": round(dd, 2),
            "final_capital": round(self.starting_capital + total_pnl, 2)
        }


def run_full_backtest():
    """Run full backtest on multiple symbols"""
    
    print("="*70)
    print("REAL NSE BACKTEST WITH LIVE MARKET DATA")
    print("="*70)
    
    # Test with different capital levels
    capital_levels = [500, 1000, 2000, 5000, 10000, 50000]
    
    # NSE stocks to test
    symbols = ['RELIANCE', 'TCS', 'INFY', 'SBIN', 'HDFCBANK', 'ICICIBANK', 
              'KOTAKBANK', 'AXISBANK', 'HINDUNILVR', 'ITC']
    
    for capital in capital_levels:
        tester = RealBacktester(starting_capital=capital)
        
        for symbol in symbols[:5]:  # Test 5 symbols per level
            trades = tester.run_backtest(symbol, days=15)
        
        stats = tester.calculate_stats()
        
        print(f"\n{'='*60}")
        print(f"CAPITAL: ₹{capital:>6} | Trades: {stats['total']:>2} | Win: {stats['win_rate']:.0f}% | P&L: ₹{stats['total_pnl']:>+8.2f}")
        print(f"{'='*60}")
        
        for t in tester.trades[:5]:
            print(f"  {t.symbol}: ₹{t.entry_price:.0f} → ₹{t.exit_price:.0f} | {t.reason:8} | PnL: ₹{t.pnl:>+7.2f} ({t.pnl_percent:+.1f}%)")
        
        if len(tester.trades) > 5:
            print(f"  ... and {len(tester.trades) - 5} more trades")
    
    # Compare with benchmark
    print(f"\n{'='*70}")
    print("BENCHMARK COMPARISON")
    print(f"{'='*70}")
    
    # Nifty 50 return for same period
    nifty = yf.Ticker("^NSEI")
    nif = nifty.history(period="15d")
    if len(nif) >= 2:
        nif_ret = (nif['Close'].iloc[-1] - nif['Close'].iloc[0]) / nif['Close'].iloc[0] * 100
        print(f"Nifty 50 (15d): {nif_ret:+.2f}%")
    
    # Our system performance
    all_tester = RealBacktester(starting_capital=5000)
    for symbol in symbols:
        all_tester.run_backtest(symbol, days=15)
    
    stats = all_tester.calculate_stats()
    print(f"Algo System (15d): Win {stats['win_rate']:.0f}% | P&L ₹{stats['total_pnl']:+.0f} | Sharpe {stats['sharpe']:.2f}")


if __name__ == "__main__":
    run_full_backtest()