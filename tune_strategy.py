#!/usr/bin/env python3
"""
Aggressive Strategy Tuning
========================
Test multiple strategy variations to find best one.
"""

import yfinance as yf
from datetime import datetime


def get_data(symbol, days=30):
    return yf.Ticker(f"{symbol}.NS").history(period=f"{days}d", interval="5m")


def analyze(symbol):
    df = get_data(symbol)
    if len(df) < 50:
        return None
    
    close = df['Close']
    c = close.iloc[-1]
    
    ema_9 = close.ewm(span=9).mean().iloc[-1]
    ema_21 = close.ewm(span=21).mean().iloc[-1]
    ema_50 = close.ewm(span=50).mean().iloc[-1]
    
    delta = close.diff()
    gain = delta.clip(lower=0).mean()
    loss = -delta.clip(upper=0).mean()
    rsi = 100 - (100 / (1 + gain/loss)) if loss > 0 else 50
    
    ema_12 = close.ewm(span=12).mean().iloc[-1]
    ema_26 = close.ewm(span=26).mean().iloc[-1]
    macd = ema_12 - ema_26
    
    vwap = (close * df['Volume']).sum() / df['Volume'].sum()
    atr = (df['High'] - df['Low']).iloc[-14:].mean()
    
    return {
        'symbol': symbol, 'price': c,
        'ema_9': ema_9, 'ema_21': ema_21, 'ema_50': ema_50,
        'rsi': rsi, 'macd': macd, 'vwap': vwap, 'atr': atr
    }


def strategy_basic(a):
    """Basic: EMA trend + RSI"""
    score = 0
    if a['ema_9'] > a['ema_21']:
        score += 40
    if 35 <= a['rsi'] <= 55:
        score += 30
    return score


def strategy_momentum(a):
    """Momentum: Strong stocks only"""
    score = 0
    if a['price'] > a['ema_9'] > a['ema_21']:
        score += 50
    if 40 <= a['rsi'] <= 60:
        score += 30
    if a['macd'] > 0:
        score += 20
    return score


def strategy_value(a):
    """Value: Buy at support"""
    score = 0
    if a['price'] >= a['vwap']:
        score += 40
    if a['rsi'] < 50:  # Oversold = buy
        score += 40
    if a['price'] < a['ema_21]:  # Pullback
        score += 20
    return score


def strategy_counter(a):
    """Counter-trend: Buy oversold"""
    score = 0
    if a['rsi'] < 35:  # Oversold bounce
        score += 50
    if a['price'] < a['vwap']:  # Below fair value
        score += 30
    if a['macd'] < 0:  # Turning point
        score += 20
    return score


def strategy_breakout(a):
    """Breakout: Strong momentum"""
    score = 0
    if a['ema_9'] > a['ema_21'] > a['ema_50']:
        score += 40
    if a['rsi'] > 50 and a['rsi'] < 70:
        score += 30
    if a['macd'] > 2:  # Strong momentum
        score += 30
    return score


def backtest(symbol, strategy_func, num_trades=20):
    """Quick backtest"""
    df = get_data(symbol, days=15)
    if len(df) < 100:
        return None
    
    wins = 0
    losses = 0
    
    for i in range(30, min(num_trades*3 + 30, len(df)-10)):
        df_slice = df.iloc[:i+1]
        
        close = df_slice['Close']
        
        # Build analysis
        c = close.iloc[-1]
        e9 = close.ewm(span=9).mean().iloc[-1]
        e21 = close.ewm(span=21).mean().iloc[-1]
        e50 = close.ewm(span=50).mean().iloc[-1]
        
        d = close.diff()
        g = d.clip(lower=0).mean()
        l = -d.clip(upper=0).mean()
        rsi = 100 - (100 / (1 + g/l)) if l > 0 else 50
        
        e12 = close.ewm(span=12).mean().iloc[-1]
        e26 = close.ewm(span=26).mean().iloc[-1]
        macd = e12 - e26
        
        vwap = (close * df_slice['Volume']).sum() / df_slice['Volume'].sum()
        atr = (df_slice['High'] - df_slice['Low']).iloc[-14:].mean()
        
        a = {
            'symbol': symbol, 'price': c,
            'ema_9': e9, 'ema_21': e21, 'ema_50': e50,
            'rsi': rsi, 'macd': macd, 'vwap': vwap, 'atr': atr
        }
        
        score = strategy_func(a)
        
        if score >= 60:
            sl = c - atr * 1.5
            tgt = c + atr * 2.5
            
            for j in range(1, min(15, len(df)-i)):
                if i + j >= len(df):
                    break
                fut = df.iloc[i+j]['Close']
                
                if fut >= tgt:
                    wins += 1
                    break
                elif fut <= sl:
                    losses += 1
                    break
    
    return {'wins': wins, 'losses': losses}


def main():
    print("="*70)
    print("STRATEGY TUNING - FIND BEST APPROACH")
    print("="*70)
    
    strategies = [
        ("Basic (Trend+RSI)", strategy_basic),
        ("Momentum", strategy_momentum),
        ("Value (Support)", strategy_value),
        ("Counter (Oversold)", strategy_counter),
        ("Breakout", strategy_breakout)
    ]
    
    symbols = ["RELIANCE", "TCS", "INFY", "KOTAKBANK", "SBIN", "HDFCBANK"]
    
    results = []
    
    for name, func in strategies:
        total_wins = 0
        total_losses = 0
        
        for sym in symbols:
            bt = backtest(sym, func)
            if bt:
                total_wins += bt['wins']
                total_losses += bt['losses']
        
        total = total_wins + total_losses
        wr = total_wins / total * 100 if total > 0 else 0
        results.append((name, total_wins, total_losses, wr))
        
        print(f"{name:20} -> Wins:{total_wins:3d} Losses:{total_losses:3d} WR:{wr:.0f}%")
    
    # Find best
    results.sort(key=lambda x: x[3], reverse=True)
    
    print("\n" + "="*70)
    print(f"BEST: {results[0][0]} with {results[0][3]:.0f}% win rate")
    print("="*70)
    
    # Show signals from best strategy
    best_name, best_func = next((n, f) for n, f in strategies if n == results[0][0])
    
    print(f"\n--- SIGNALS FROM {best_name} ---")
    
    for sym in symbols:
        a = analyze(sym)
        if a:
            score = best_func(a)
            if score >= 60:
                print(f"BUY {sym:12} @ Rs.{a['price']:.2f} RSI:{a['rsi']:.0f} Conf:{score}%")


if __name__ == "__main__":
    main()