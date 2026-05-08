#!/usr/bin/env python3
"""
Simplified Core Strategy
====================
Institutional-grade simplicity: 3 indicators maximum.

Core Indicators:
1. EMA(21) - Trend direction
2. RSI(14) - Momentum (overbought/oversold)
3. VWAP - Fair value / support

This avoids indicator overfitting while maintaining edge.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Tuple
from datetime import datetime


class SimplifiedStrategy:
    """
    3-Indicator Strategy
    
    Entry Rules:
    1. EMA9 > EMA21 (bullish trend)
    2. RSI between 35-65 (not overbought)
    3. Price at or above VWAP (fair value)
    
    Exit Rules:
    1. Target: 2R (2x risk)
    2. Stop: 1R max
    3. Time: Exit if no movement in 2 hours
    
    This simplifies the original 15+ indicator system
    to avoid curve-fitting.
    """
    
    def __init__(self, min_confidence: int = 60):
        self.min_confidence = min_confidence
    
    def analyze(self, symbol: str, period: str = "10d", 
               interval: str = "15m") -> Dict:
        """Analyze symbol with 3 indicators"""
        
        # Fetch data
        df = yf.Ticker(f"{symbol}.NS").history(
            period=period, 
            interval=interval
        )
        
        if len(df) < 50:
            return {"signal": "none", "confidence": 0}
        
        close = df['Close']
        
        # 1. EMA - Trend
        ema_9 = close.ewm(span=9).mean().iloc[-1]
        ema_21 = close.ewm(span=21).mean().iloc[-1]
        
        # 2. RSI - Momentum
        delta = close.diff()
        gain = delta.clip(lower=0).mean()
        loss = (-delta.clip(upper=0)).mean()
        rsi = 100 - (100 / (1 + gain/loss)) if loss > 0 else 50
        
        # 3. VWAP - Fair value
        pv = (close * df['Volume']).sum()
        volume_sum = df['Volume'].sum()
        vwap = pv / volume_sum if volume_sum > 0 else close.iloc[-1]
        
        current = close.iloc[-1]
        
        # ATR for stops
        atr = (df['High'] - df['Low']).iloc[-14:].mean()
        
        # Scoring (simplified)
        score = 0
        
        # Trend: EMA9 > EMA21
        if ema_9 > ema_21:
            score += 30
            trend = "bullish"
        else:
            trend = "bearish"
        
        # Momentum: RSI sweet spot (35-65)
        if 35 <= rsi <= 65:
            score += 25
        elif rsi < 30:
            score += 30  # Oversold = buy opportunity
        elif rsi > 70:
            score -= 30  # Overbought = avoid
        
        # Value: Price near VWAP
        if current >= vwap:
            score += 20
        elif current >= vwap * 0.99:
            score += 10  # Near VWAP
        
        # Calculate trade parameters
        if score >= self.min_confidence:
            stop_loss = current - (atr * 1.5)
            target = current + (atr * 2.0)  # 2R minimum
            risk = current - stop_loss
            
            signal = "buy" if score >= self.min_confidence else "none"
        else:
            stop_loss = 0
            target = 0
            risk = 0
            signal = "none"
        
        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": min(score, 100),
            "price": current,
            "ema_9": ema_9,
            "ema_21": ema_21,
            "rsi": rsi,
            "vwap": vwap,
            "stop_loss": stop_loss,
            "target": target,
            "atr": atr,
            "trend": trend,
            "reasons": self._get_reasons(score, trend, rsi, current, vwap)
        }
    
    def _get_reasons(self, score: int, trend: str, rsi: float, 
                   price: float, vwap: float) -> str:
        """Get human-readable reasons"""
        reasons = []
        
        if score >= 30:
            reasons.append(f"Trend: {trend}")
        if 35 <= rsi <= 65 or rsi < 30:
            reasons.append(f"RSI: {rsi:.0f}")
        if price >= vwap:
            reasons.append(f"Above VWAP")
        
        return " | ".join(reasons) if reasons else "No signal"
    
    def scan(self, symbols: list) -> list:
        """Scan multiple symbols"""
        results = []
        
        for symbol in symbols:
            analysis = self.analyze(symbol)
            
            if analysis["signal"] == "buy":
                results.append(analysis)
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return results


def test_simplified():
    """Test the simplified strategy"""
    
    print("="*60)
    print("SIMPLIFIED 3-INDICATOR STRATEGY TEST")
    print("="*60)
    
    strategy = SimplifiedStrategy(min_confidence=60)
    
    # Test symbols
    symbols = ['RELIANCE', 'TCS', 'INFY', 'SBIN', 'HDFCBANK']
    
    for symbol in symbols:
        analysis = strategy.analyze(symbol)
        
        if analysis["signal"] == "buy":
            print(f"\nBUY: {symbol}")
            print(f"  Price: Rs.{analysis['price']:.2f}")
            print(f"  RSI: {analysis['rsi']:.0f}")
            print(f"  Trend: {analysis['trend']}")
            print(f"  VWAP: Rs.{analysis['vwap']:.2f}")
            print(f"  Confidence: {analysis['confidence']}%")
            print(f"  SL: Rs.{analysis['stop_loss']:.2f}")
            print(f"  Target: Rs.{analysis['target']:.2f}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_simplified()