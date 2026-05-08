#!/usr/bin/env python3
"""
Paper Trading Test
============
Test the trading system in paper mode (no real money).

Usage:
    python3 paper_trade.py
"""

import yfinance as yf
from datetime import datetime


def get_market_data(symbol):
    """Get market data for symbol"""
    df = yf.Ticker(f"{symbol}.NS").history(period="5d", interval="15m")
    if len(df) < 20:
        return None
    return df


def analyze_signal(symbol, df):
    """Simple signal analysis"""
    close = df['Close']
    current = close.iloc[-1]
    
    # EMA
    ema_9 = close.ewm(span=9).mean().iloc[-1]
    ema_21 = close.ewm(span=21).mean().iloc[-1]
    
    # RSI
    delta = close.diff()
    gain_mean = delta.clip(lower=0).mean()
    loss_mean = -delta.clip(upper=0).mean()
    rsi = 100 - (100 / (1 + gain_mean / loss_mean)) if loss_mean > 0 else 50
    
    # VWAP
    vwap = (close * df['Volume']).sum() / df['Volume'].sum()
    
    # ATR
    atr = (df['High'] - df['Low']).iloc[-14:].mean()
    
    # Score
    score = 0
    reasons = []
    
    if ema_9 > ema_21:
        score += 30
        reasons.append("Bullish EMA")
    
    if 35 <= rsi <= 65:
        score += 25
        reasons.append(f"RSI {rsi:.0f}")
    
    if current >= vwap:
        score += 20
        reasons.append("Above VWAP")
    
    stop_loss = current - atr * 1.5
    target = current + atr * 2.0
    
    return {
        "symbol": symbol,
        "price": current,
        "signal": "BUY" if score >= 50 else "WAIT",
        "confidence": score,
        "stop_loss": stop_loss,
        "target": target,
        "reasons": ", ".join(reasons)
    }


def run_paper_test():
    """Run paper trading test"""
    
    print("="*60)
    print("QUANTFLOW - PAPER TRADING TEST")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Mode: PAPER (no real money)")
    print("="*60)
    
    capital = 5000
    max_risk = 2.0
    symbols = ["RELIANCE", "TCS", "INFY", "SBIN", "HDFCBANK", "ICICIBANK", "KOTAKBANK"]
    
    print(f"\nConfig:")
    print(f"  Capital: Rs.{capital:,}")
    print(f"  Max Risk: {max_risk}%/trade")
    print(f"  Symbols: {', '.join(symbols)}")
    
    print("\n" + "-"*60)
    print("SCANNING MARKET...")
    print("-"*60)
    
    signals = []
    
    for symbol in symbols:
        df = get_market_data(symbol)
        if df is None:
            continue
        
        result = analyze_signal(symbol, df)
        
        if result["signal"] == "BUY":
            signals.append(result)
            print(f"\n{result['signal']}: {symbol}")
            print(f"  Price: Rs.{result['price']:.2f}")
            print(f"  Confidence: {result['confidence']}%")
            print(f"  Stop Loss: Rs.{result['stop_loss']:.2f}")
            print(f"  Target: Rs.{result['target']:.2f}")
            print(f"  Reasons: {result['reasons']}")
    
    if not signals:
        print("\nNo buy signals (waiting for setup)")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    print(f"\nSignals Found: {len(signals)}")
    print(f"Capital: Rs.{capital}")


if __name__ == "__main__":
    run_paper_test()