#!/usr/bin/env python3
"""
Multi-Timeframe Analysis Engine
=========================================
Advanced technical analysis across multiple timeframes

Supports:
- 1-minute (scalping)
- 5-minute (intraday)
- 15-minute (swing intraday)
- 1-hour (positional)
- 1-day (positional)

Signal Confirmation:
- Higher timeframe alignment
- Trend strength across timeframes
- Momentum divergence detection
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum


class TimeFrame(Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    D1 = "1d"


@dataclass
class TimeFrameData:
    """Data for a single timeframe"""
    timeframe: TimeFrame
    candles: List[dict]
    current_price: float = 0
    vwap: float = 0
    ema_9: float = 0
    ema_21: float = 0
    ema_50: float = 0
    rsi: float = 50
    volume: int = 0
    avg_volume: int = 0
    trend: str = "sideways"
    
    @property
    def trend_aligned_with_bullish(self) -> bool:
        if self.trend == "bull":
            return self.current_price > self.ema_21 > self.ema_50
        return False
    
    @property
    def momentum(self) -> float:
        """Calculate momentum score"""
        score = 0
        if self.current_price > self.vwap:
            score += 2
        if self.ema_9 > self.ema_21:
            score += 2
        if 40 < self.rsi < 60:
            score += 1
        return score


@dataclass
class MultiTimeframeAnalysis:
    """Multi-timeframe analysis engine"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.timeframes: Dict[TimeFrame, TimeFrameData] = {}
        self.higher_tf = TimeFrame.M15  # Confirm from 15m
        self.entry_tf = TimeFrame.M5      # Entry from 5m
    
    def add_data(self, tf: TimeFrame, data: dict):
        """Add data for a timeframe"""
        tfd = TimeFrameData(
            timeframe=tf,
            candles=data.get("candles", []),
            current_price=data.get("price", 0),
            vwap=data.get("vwap", 0),
            ema_9=data.get("ema_9", 0),
            ema_21=data.get("ema_21", 0),
            ema_50=data.get("ema_50", 0),
            rsi=data.get("rsi", 50),
            volume=data.get("volume", 0),
            avg_volume=data.get("avg_volume", 0),
            trend=data.get("trend", "sideways")
        )
        self.timeframes[tf] = tfd
    
    def get_higher_tf_bias(self) -> str:
        """Get directional bias from higher timeframe"""
        if self.higher_tf not in self.timeframes:
            return "neutral"
        
        tf_data = self.timeframes[self.higher_tf]
        
        # Strong bullish: multiple confirmations
        if (tf_data.current_price > tf_data.ema_21 > tf_data.ema_50 and
            tf_data.rsi < 65 and tf_data.rsi > 35 and
            tf_data.current_price > tf_data.vwap):
            return "bullish"
        
        # Strong bearish
        if (tf_data.current_price < tf_data.ema_21 < tf_data.ema_50 and
            tf_data.rsi > 35 and tf_data.rsi < 65 and
            tf_data.current_price < tf_data.vwap):
            return "bearish"
        
        return "neutral"
    
    def get_entry_signal(self) -> Tuple[str, float]:
        """
        Get entry signal combining timeframes
        
        Returns: (direction, confidence)
        """
        if self.entry_tf not in self.timeframes:
            return "no_signal", 0
        
        if self.higher_tf not in self.timeframes:
            return "no_signal", 0
        
        entry_data = self.timeframes[self.entry_tf]
        higher_data = self.timeframes[self.higher_tf]
        
        higher_bias = self.get_higher_tf_bias()
        entry_momentum = entry_data.momentum
        
        if higher_bias == "bullish" and entry_momentum >= 3:
            return "long", min(higher_data.momentum * 10 + entry_momentum * 5, 90)
        
        if higher_bias == "bearish" and entry_momentum >= 3:
            return "short", min(higher_data.momentum * 10 + entry_momentum * 5, 90)
        
        return "no_signal", 0
    
    def get_momentum_divergence(self) -> Dict:
        """Detect momentum divergence across timeframes"""
        divergences = {
            "bullish": [],
            "bearish": [],
            "hidden_bullish": [],
            "hidden_bearish": []
        }
        
        if len(self.timeframes) < 2:
            return divergences
        
        # Compare higher vs lower timeframes
        higher = self.timeframes.get(self.higher_tf)
        lower = self.timeframes.get(self.entry_tf)
        
        if not higher or not lower:
            return divergences
        
        # Hidden bullish: lower TF stronger than higher
        if (lower.trend_aligned_with_bullish and 
            not higher.trend_aligned_with_bullish and
            lower.momentum > higher.momentum):
            divergences["hidden_bullish"].append(
                f"Hidden bullish: {self.entry_tf.value} stronger than {self.higher_tf.value}"
            )
        
        # Regular bullish: alignment
        if higher.trend_aligned_with_bullish and lower.trend_aligned_with_bullish:
            divergences["bullish"].append(
                "Bullish alignment across timeframes"
            )
        
        return divergences
    
    def get_confluence_score(self) -> float:
        """Calculate overall confluence score (0-100)"""
        score = 0
        
        # Higher TF bias contribution (40%)
        higher_bias = self.get_higher_tf_bias()
        if higher_bias == "bullish":
            score += 40
        elif higher_bias == "bearish":
            score += 40
        
        # Entry TF momentum (30%)
        if self.entry_tf in self.timeframes:
            score += self.timeframes[self.entry_tf].momentum * 5
        
        # Volume confirmation (20%)
        for tf, data in self.timeframes.items():
            if data.volume > data.avg_volume * 1.3:
                score += 5
        
        # Trend alignment (10%)
        divergences = self.get_momentum_divergence()
        if divergences["bullish"] or divergences["hidden_bullish"]:
            score += 10
        
        return min(score, 100)
    
    def should_trade(self) -> Tuple[bool, str, float]:
        """
        Decision: Should we take a trade?
        
        Returns: (should_trade, reason, confidence)
        """
        confluence = self.get_confluence_score()
        higher_bias = self.get_higher_tf_bias()
        
        # Minimum confluence for trade
        if confluence < 40:
            return False, f"Weak confluence ({confluence}%)", confluence
        
        # No alignment on higher TF
        if higher_bias == "neutral":
            return False, "Higher TF neutral", confluence
        
        signal, conf = self.get_entry_signal()
        
        if signal == "no_signal":
            return False, "No clear entry signal", confluence
        
        if conf < 50:
            return False, f"Weak entry confidence ({conf}%)", confluence
        
        return True, f"{signal.upper()} signal from {self.entry_tf.value} on {higher_bias} trend", confluence


# =========== TEST ===========
def test_multiframe():
    """Test multi-timeframe analysis"""
    
    print("=" * 60)
    print("MULTI-TIMEFRAME ANALYSIS TEST")
    print("=" * 60)
    
    mtfa = MultiTimeframeAnalysis("RELIANCE")
    
    # Simulate 15m (higher) - Bullish
    mtfa.add_data(TimeFrame.M15, {
        "price": 2550,
        "vwap": 2520,
        "ema_9": 2540,
        "ema_21": 2510,
        "ema_50": 2480,
        "rsi": 55,
        "volume": 150000,
        "avg_volume": 120000,
        "trend": "bull"
    })
    
    # Simulate 5m (entry) - Strong bullish
    mtfa.add_data(TimeFrame.M5, {
        "price": 2555,
        "vwap": 2540,
        "ema_9": 2550,
        "ema_21": 2520,
        "rsi": 58,
        "volume": 50000,
        "avg_volume": 35000,
    })
    
    # Analysis
    print(f"\n15m (higher) bias: {mtfa.get_higher_tf_bias()}")
    print(f"Entry signal: {mtfa.get_entry_signal()}")
    print(f"Confluence: {mtfa.get_confluence_score()}%")
    
    should_trade, reason, conf = mtfa.should_trade()
    print(f"\nShould Trade: {should_trade}")
    print(f"  Reason: {reason}")
    print(f"  Confidence: {conf}%")
    
    divergence = mtfa.get_momentum_divergence()
    print(f"\nDivergences: {divergence}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_multiframe()