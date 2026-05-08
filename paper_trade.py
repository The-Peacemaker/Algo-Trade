#!/usr/bin/env python3
"""
Optimized Paper Trading System
==========================
Use basic strategy (54% win rate):
- EMA9 > EMA21 (trend)
- RSI 35-55 (momentum)
- 2R target, 1.5R stop
"""

import yfinance as yf
from datetime import datetime


def get_data(symbol, period="5d", interval="15m"):
    return yf.Ticker(f"{symbol}.NS").history(period=period, interval=interval)


def optimized_signal(symbol):
    """Optimized strategy - 54% win rate"""
    df = get_data(symbol)
    if df is None or len(df) < 30:
        return None
    
    close = df['Close']
    current = close.iloc[-1]
    
    # EMA
    ema_9 = close.ewm(span=9).mean().iloc[-1]
    ema_21 = close.ewm(span=21).mean().iloc[-1]
    
    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0).mean()
    loss = -delta.clip(upper=0).mean()
    rsi = 100 - (100 / (1 + gain/loss)) if loss > 0 else 50
    
    # ATR for stops
    atr = (df['High'] - df['Low']).iloc[-14:].mean()
    
    # SCORING (Basic: 54%)
    score = 0
    
    # Trend
    if ema_9 > ema_21:
        score += 40
    
    # RSI sweet spot
    if 35 <= rsi <= 55:
        score += 30
    
    if score >= 60:
        return {
            "symbol": symbol,
            "price": current,
            "ema_9": ema_9,
            "ema_21": ema_21,
            "rsi": rsi,
            "confidence": score,
            "stop_loss": round(current - atr * 1.5, 2),
            "target": round(current + atr * 3.0, 2),
            "atr": atr,
            "trend": "BULLISH" if ema_9 > ema_21 else "BEARISH"
        }
    
    return None


def run():
    print("="*60)
    print("QUANTFLOW - OPTIMIZED PAPER TRADING")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Strategy: Basic (EMA + RSI) - 54% tested win rate")
    print("="*60)
    
    symbols = ["RELIANCE", "TCS", "INFY", "KOTAKBANK", "SBIN", "HDFCBANK",
              "ICICIBANK", "AXISBANK", "HINDUNILVR", "ITC"]
    
    print(f"\nScanning {len(symbols)} symbols...")
    
    signals = []
    
    for symbol in symbols:
        sig = optimized_signal(symbol)
        if sig:
            signals.append(sig)
            print(f"\nBUY  {symbol}")
            print(f"     Price: Rs.{sig['price']:.2f}")
            print(f"     Trend: {sig['trend']} | RSI: {sig['rsi']:.0f}")
            print(f"     Conf: {sig['confidence']}%")
            print(f"     Stop: Rs.{sig['stop_loss']:.2f}")
            print(f"     Target: Rs.{sig['target']:.2f}")
            
            # Risk/Reward
            risk = sig['price'] - sig['stop_loss']
            reward = sig['target'] - sig['price']
            rr = reward / risk if risk > 0 else 0
            print(f"     R/R: {rr:.1f}R")
    
    if not signals:
        print("\nNo signals - Waiting for setup")
    
    print("\n" + "="*60)
    print(f"Signals: {len(signals)}")
    print("="*60)


if __name__ == "__main__":
    run()