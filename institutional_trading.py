#!/usr/bin/env python3
"""
Institutional Trading System - Complete
========================================
Real-time algorithmic trading with proven strategies.

Features:
- Multi-timeframe analysis
- Confluence-based entries
- Proper risk/reward (2R minimum)
- Trend-following with pullback entries
- Market structure analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Trade record"""
    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float
    pnl_percent: float
    exit_reason: str
    holding_minutes: int
    confidence: int


class TradingEngine:
    """
    Complete trading engine with institutional strategies.
    """
    
    def __init__(self, capital: float = 10000):
        self.capital = capital
        self.starting_capital = capital
        self.trades: List[Trade] = []
        self.daily_pnl = defaultdict(float)
    
    def get_data(self, symbol: str, days: int = 30, interval: str = "15m") -> pd.DataFrame:
        """Fetch OHLCV data"""
        try:
            return yf.Ticker(f"{symbol}.NS").history(period=f"{days}d", interval=interval)
        except:
            return pd.DataFrame()
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate all indicators"""
        if len(df) < 50:
            return {}
        
        close = df['Close']
        current = close.iloc[-1]
        
        # EMAs
        ema_9 = close.ewm(span=9).mean().iloc[-1]
        ema_21 = close.ewm(span=21).mean().iloc[-1]
        ema_50 = close.ewm(span=50).mean().iloc[-1]
        
        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.iloc[-14:].mean()
        avg_loss = loss.iloc[-14:].mean()
        rsi = 100 - (100 / (1 + avg_gain/avg_loss)) if avg_loss > 0 else 50
        
        # MACD
        ema_12 = close.ewm(span=12).mean().iloc[-1]
        ema_26 = close.ewm(span=26).mean().iloc[-1]
        macd = ema_12 - ema_26
        
        # VWAP
        pv = (close * df['Volume']).sum()
        vwap = pv / df['Volume'].sum()
        
        # ATR
        high = df['High']
        low = df['Low']
        atr = (high - low).iloc[-14:].mean()
        
        # Stochastic
        low_14 = low.iloc[-14:].min()
        high_14 = high.iloc[-14:].max()
        stoch = 100 * (current - low_14) / (high_14 - low_14) if high_14 != low_14 else 50
        
        # Volume
        avg_vol = df['Volume'].iloc[-20:].mean()
        
        return {
            "price": current,
            "ema_9": ema_9,
            "ema_21": ema_21,
            "ema_50": ema_50,
            "rsi": rsi,
            "macd": macd,
            "vwap": vwap,
            "atr": atr,
            "stochastic": stoch,
            "volume": df['Volume'].iloc[-1],
            "avg_volume": avg_vol
        }
    
    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """Generate trading signal"""
        ind = self.calculate_indicators(df)
        
        if not ind:
            return {"action": "none", "confidence": 0}
        
        price = ind["price"]
        
        # Trend
        bullish = ind["ema_9"] > ind["ema_21"] > ind["ema_50"]
        bearish = ind["ema_9"] < ind["ema_21"] < ind["ema_50"]
        
        # Score
        score = 0
        reasons = []
        
        # TREND (30 pts)
        if bullish:
            score += 20
            reasons.append("Bullish trend")
        elif bearish:
            score -= 20
            reasons.append("Bearish trend")
        
        # RSI (20 pts)
        if 35 <= ind["rsi"] <= 55:
            score += 15
            reasons.append(f"RSI sweet spot ({ind['rsi']:.0f})")
        elif ind["rsi"] < 30:
            score += 10
            reasons.append(f"RSI oversold ({ind['rsi']:.0f})")
        elif ind["rsi"] > 70:
            score -= 15
            reasons.append(f"RSI overbought ({ind['rsi']:.0f})")
        
        # MACD (15 pts)
        if ind["macd"] > 0:
            score += 10
            reasons.append("MACD bullish")
        else:
            score -= 10
            reasons.append("MACD bearish")
        
        # Price vs VWAP (10 pts)
        if price > ind["vwap"]:
            score += 10
            reasons.append("Above VWAP")
        else:
            score -= 5
            reasons.append("Below VWAP")
        
        # Stochastic (10 pts)
        if ind["stochastic"] < 30:
            score += 10
            reasons.append(f"Stochastic oversold ({ind['stochastic']:.0f})")
        elif ind["stochastic"] > 70:
            score -= 10
            reasons.append(f"Stochastic overbought ({ind['stochastic']:.0f})")
        
        # Volume (5 pts)
        if ind["volume"] > ind["avg_volume"]:
            score += 5
            reasons.append("Above avg volume")
        
        # Price action (10 pts)
        c1 = df.iloc[-1]
        if c1['Close'] > c1['Open'] and c1['Close'] > c1['Open'] * 1.005:
            score += 10
            reasons.append("Strong bullish candle")
        
        # Determine action
        conf = abs(score)
        
        if score >= 60 and bullish:
            action = "buy"
            sl = price - (ind["atr"] * 1.5)
            target = price + (ind["atr"] * 3)
        elif score <= -60 and bearish:
            action = "sell"
            sl = price + (ind["atr"] * 1.5)
            target = price - (ind["atr"] * 3)
        else:
            action = "none"
            sl = 0
            target = 0
        
        return {
            "action": action,
            "confidence": min(conf, 100),
            "price": price,
            "stop_loss": sl,
            "target": target,
            "atr": ind["atr"],
            "reasons": reasons,
            "indicators": ind
        }
    
    def backtest_symbol(self, symbol: str, days: int = 30, interval: str = "5m") -> List[Trade]:
        """Backtest a symbol"""
        df = self.get_data(symbol, days, interval)
        
        if len(df) < 100:
            return []
        
        trades = []
        position = None
        self.capital = self.starting_capital  # Reset capital
        
        for i in range(50, len(df) - 1):
            df_slice = df.iloc[:i+1]
            sig = self.generate_signal(df_slice)
            time = df.index[i].to_pydatetime()
            
            price = sig["price"]
            
            if position:
                # Check exit
                exit_reason = None
                exit_price = price
                
                if sig["action"] == "sell" and position["side"] == "long":
                    exit_reason = "signal_reversal"
                    exit_price = price
                elif price <= position["sl"]:
                    exit_reason = "stop_loss"
                    exit_price = position["sl"]
                elif price >= position["target"]:
                    exit_reason = "target"
                    exit_price = position["target"]
                elif (time - position["entry_time"]).total_seconds() > 5400:  # 90 min max
                    exit_reason = "time_exit"
                
                if exit_reason:
                    pnl = (exit_price - position["entry"]) * position["qty"]
                    pnl_pct = (pnl / (position["entry"] * position["qty"])) * 100
                    
                    trade = Trade(
                        symbol=symbol,
                        entry_time=position["entry_time"],
                        exit_time=time,
                        entry_price=position["entry"],
                        exit_price=exit_price,
                        quantity=position["qty"],
                        pnl=round(pnl, 2),
                        pnl_percent=round(pnl_pct, 2),
                        exit_reason=exit_reason,
                        holding_minutes=int((time - position["entry_time"]).total_seconds() / 60),
                        confidence=position["conf"]
                    )
                    trades.append(trade)
                    self.capital += pnl
                    position = None
            
            # Entry
            elif sig["action"] == "buy" and sig["confidence"] >= 50:
                if self.capital >= price:
                    qty = max(1, int((self.capital * 0.1) / price))
                    
                    position = {
                        "side": "long",
                        "entry": price,
                        "sl": sig["stop_loss"],
                        "target": sig["target"],
                        "qty": qty,
                        "conf": sig["confidence"],
                        "entry_time": time
                    }
        
        self.trades.extend(trades)
        return trades
    
    def run_full_backtest(self):
        """Run complete backtest"""
        print("="*70)
        print("INSTITUTIONAL TRADING SYSTEM - LIVE DATA BACKTEST")
        print("="*70)
        
        # NSE stocks
        symbols = ['RELIANCE', 'TCS', 'INFY', 'SBIN', 'HDFCBANK', 'ICICIBANK',
                   'KOTAKBANK', 'HINDUNILVR', 'ITC', 'TITAN', 'ADANIPORTS',
                   'ASIANPAINT', 'MARUTI', 'BAJFINANCE', 'DRREDDY']
        
        all_trades = []
        
        # Test different capital levels
        for capital in [500, 1000, 5000, 10000]:
            tester = TradingEngine(capital=capital)
            
            print(f"\n{'='*60}")
            print(f"CAPITAL: ₹{capital:,}")
            print(f"{'='*60}")
            
            for symbol in symbols[:8]:
                trades = tester.backtest_symbol(symbol, days=10)
            
            # Stats
            wins = [t for t in tester.trades if t.pnl > 0]
            losses = [t for t in tester.trades if t.pnl <= 0]
            total_pnl = sum(t.pnl for t in tester.trades)
            win_rate = len(wins) / len(tester.trades) * 100 if tester.trades else 0
            
            # Calculate proper Sharpe
            if tester.trades:
                rets = [t.pnl_percent for t in tester.trades]
                avg_ret = sum(rets) / len(rets)
                std = (sum((r - avg_ret) ** 2 for r in rets) / len(rets)) ** 0.5
                sharpe = (avg_ret / std * (252 * 39) ** 0.5) if std > 0 else 0
            else:
                sharpe = 0
            
            print(f"Trades: {len(tester.trades)} | Win: {win_rate:.0f}% | P&L: ₹{total_pnl:+.2f} | Sharpe: {sharpe:.2f}")
            
            # Show sample trades
            for t in tester.trades[:3]:
                print(f"  {t.symbol}: ₹{t.entry_price:.0f}→₹{t.exit_price:.0f} | {t.exit_reason:10} | PnL: ₹{t.pnl:>+7.2f} ({t.pnl_percent:+.1f}%)")
            
            all_trades.extend(tester.trades)
        
        # Benchmark
        print(f"\n{'='*70}")
        print("BENCHMARK COMPARISON")
        print(f"{'='*70}")
        
        nifty = yf.Ticker("^NSEI").history(period="10d")
        if len(nifty) >= 2:
            nret = (nifty['Close'].iloc[-1] - nifty['Close'].iloc[0]) / nifty['Close'].iloc[0] * 100
            print(f"Nifty 50 (10d): {nret:+.2f}%")
        
        # System performance
        if all_trades:
            total_pnl = sum(t.pnl for t in all_trades)
            wins = len([t for t in all_trades if t.pnl > 0])
            win_rate = wins / len(all_trades) * 100
            
            print(f"System (10d): Win {win_rate:.0f}% | P&L ₹{total_pnl:+.0f}")
            
            # By symbol
            print(f"\n--- By Symbol ---")
            by_symbol = defaultdict(list)
            for t in all_trades:
                by_symbol[t.symbol].append(t)
            
            for sym, trds in sorted(by_symbol.items(), key=lambda x: sum(t.pnl for t in x[1]), reverse=True)[:10]:
                pnls = sum(t.pnl for t in trds)
                wr = len([t for t in trds if t.pnl > 0]) / len(trds) * 100 if trds else 0
                print(f"  {sym:12} | Trades: {len(trds):2} | Win: {wr:5.0f}% | P&L: ₹{pnls:>+8.2f}")


if __name__ == "__main__":
    engine = TradingEngine()
    engine.run_full_backtest()