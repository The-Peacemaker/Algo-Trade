#!/usr/bin/env python3
"""
Live System Analysis & Tuning
=====================
Analyze current signals, test different parameters, and optimize.
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd


def get_data(symbol, days=30):
    """Get market data"""
    return yf.Ticker(f"{symbol}.NS").history(period=f"{days}d", interval="15m")


def analyze_full(symbol, df=None):
    """Full analysis with all metrics"""
    if df is None:
        df = get_data(symbol)
    
    if len(df) < 50:
        return None
    
    close = df['Close']
    current = close.iloc[-1]
    
    # EMA
    ema_9 = close.ewm(span=9).mean().iloc[-1]
    ema_21 = close.ewm(span=21).mean().iloc[-1]
    ema_50 = close.ewm(span=50).mean().iloc[-1]
    
    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0).mean()
    loss = -delta.clip(upper=0).mean()
    rsi = 100 - (100 / (1 + gain/loss)) if loss > 0 else 50
    
    # MACD
    ema_12 = close.ewm(span=12).mean().iloc[-1]
    ema_26 = close.ewm(span=26).mean().iloc[-1]
    macd = ema_12 - ema_26
    macd_signal = macd  # Simplified
    
    # VWAP
    vwap = (close * df['Volume']).sum() / df['Volume'].sum()
    
    # ATR
    atr = (df['High'] - df['Low']).iloc[-14:].mean()
    
    # Stochastic
    low_14 = df['Low'].iloc[-14:].min()
    high_14 = df['High'].iloc[-14:].max()
    stoch = 100 * (current - low_14) / (high_14 - low_14) if high_14 != low_14 else 50
    
    # Volume
    avg_vol = df['Volume'].iloc[-20:].mean()
    vol_ratio = df['Volume'].iloc[-1] / avg_vol
    
    return {
        'symbol': symbol,
        'price': current,
        'ema_9': ema_9,
        'ema_21': ema_21,
        'ema_50': ema_50,
        'rsi': rsi,
        'macd': macd,
        'vwap': vwap,
        'atr': atr,
        'stoch': stoch,
        'vol_ratio': vol_ratio,
        'trend': 'bullish' if ema_9 > ema_21 > ema_50 else 'bearish' if ema_9 < ema_21 < ema_50 else 'sideways'
    }


def score_buy_v1(analysis):
    """Original v1 scoring (score >= 50)"""
    s = analysis
    score = 0
    
    if s['ema_9'] > s['ema_21']:
        score += 30
    if 35 <= s['rsi'] <= 65:
        score += 25
    if s['macd'] > 0:
        score += 15
    if s['price'] >= s['vwap']:
        score += 20
    
    return score


def score_buy_v2(analysis):
    """Tighter v2 scoring - need multipleconfirmations"""
    s = analysis
    score = 0
    
    # Must be in strong uptrend
    if s['ema_9'] > s['ema_21'] > s['ema_50']:
        score += 35
    
    # RSI sweet spot (not overbought)
    if 40 <= s['rsi'] <= 55:
        score += 25
    elif s['rsi'] < 40:  # Oversold = buy
        score += 30
    
    # MACD bullish
    if s['macd'] > 0:
        score += 15
    
    # Price above VWAP
    if s['price'] > s['vwap']:
        score += 15
    
    # Good volume
    if s['vol_ratio'] > 1.0:
        score += 10
    
    return score


def score_buy_v3(analysis):
    """Very tight v3 - institutional style"""
    s = analysis
    score = 0
    
    # STRICT: All 3 EMAs aligned
    if s['ema_9'] > s['ema_21'] > s['ema_50']:
        score += 40
    
    # RSI not overbought
    if s['rsi'] < 60:
        score += 20
    
    # MACD turning positive
    if s['macd'] > 0:
        score += 15
    
    # RSI not oversold
    if s['rsi'] > 30:
        score += 10
    
    return score


def backtest_signal(symbol, scoring_func, days=10):
    """Backtest a scoring function"""
    df = get_data(symbol, days)
    
    if len(df) < 100:
        return None
    
    trades = []
    capital = 5000
    
    for i in range(50, len(df)-10):
        df_slice = df.iloc[:i+1]
        analysis = analyze_full(symbol, df_slice)
        
        score = scoring_func(analysis)
        
        if score >= 60:
            entry = df_slice['Close'].iloc[-1]
            atr = analysis['atr']
            sl = entry - atr * 1.5
            tgt = entry + atr * 2.0
            
            # Simulate next 10 candles
            for j in range(1, min(15, len(df)-i)):
                if i + j >= len(df):
                    break
                exit_price = df.iloc[i+j]['Close']
                
                if exit_price >= tgt:
                    trades.append({'result': 'WIN', 'pnl': tgt - entry})
                    break
                elif exit_price <= sl:
                    trades.append({'result': 'LOSS', 'pnl': sl - entry})
                    break
            else:
                trades.append({'result': 'HOLD', 'pnl': 0})
    
    return trades


def run_analysis():
    """Run full analysis"""
    
    print("="*70)
    print("QUANTFLOW - LIVE ANALYSIS & TUNING")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    symbols = ["RELIANCE", "TCS", "INFY", "SBIN", "HDFCBANK", "ICICIBANK", 
              "KOTAKBANK", "AXISBANK", "HINDUNILVR", "ITC"]
    
    # Step 1: Current signals
    print("\n--- STEP 1: CURRENT SIGNALS ---")
    
    results = []
    for symbol in symbols:
        a = analyze_full(symbol)
        if a:
            v1 = score_buy_v1(a)
            v2 = score_buy_v2(a)
            v3 = score_buy_v3(a)
            
            results.append({
                'symbol': symbol,
                'price': a['price'],
                'trend': a['trend'],
                'rsi': a['rsi'],
                'macd': a['macd'],
                'vwap': a['vwap'],
                'v1': v1,
                'v2': v2,
                'v3': v3
            })
            
            best = max(v1, v2, v3)
            if best >= 60:
                print(f"{symbol:12} Rs.{a['price']:>7.2f} | Trend:{a['trend']:8} | RSI:{a['rsi']:>4.0f} | V1:{v1:>2} V2:{v2:>2} V3:{v3:>2} -> {'BUY' if best >= 60 else 'WAIT'}")
    
    # Step 2: Best scoring version
    print("\n--- STEP 2: SCORING VERSION COMPARISON ---")
    
    versions = [
        ("V1 (Original)", score_buy_v1),
        ("V2 (Tighter)", score_buy_v2),
        ("V3 (Strict)", score_buy_v3)
    ]
    
    for name, func in versions:
        wins = 0
        losses = 0
        for symbol in ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']:
            trades = backtest_signal(symbol, func, days=10)
            if trades:
                for t in trades:
                    if t['result'] == 'WIN':
                        wins += 1
                    elif t['result'] == 'LOSS':
                        losses += 1
        
        total = wins + losses
        wr = wins / total * 100 if total > 0 else 0
        print(f"{name:15} -> Wins: {wins}, Losses: {losses}, Win Rate: {wr:.0f}%")
    
    # Step 3: Best signal now
    print("\n--- STEP 3: BEST SIGNALS NOW ---")
    
    for r in results:
        if r['v3'] >= 55:  # Using strictest version
            a = next(a for a in [analyze_full(r['symbol'])] if a)
            print(f"BUY: {r['symbol']:12} @ Rs.{r['price']:.2f}")
            print(f"    Trend:{r['trend']} | RSI:{r['rsi']:.0f} | MACD:{r['macd']:.2f}")
            print(f"    Conf:{r['v3']}% | SL:Rs.{r['price'] - a['atr']*1.5:.2f} | Tgt:Rs.{r['price'] + a['atr']*2:.2f}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    run_analysis()