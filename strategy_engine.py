#!/usr/bin/env python3
"""
Quant Strategy Engine
=========================================
Multi-signal strategy engine for algorithmic trading

Signal Types:
1. VWAP Breakout - Price breaking VWAP with volume
2. EMA Crossover - Fast/slow EMA cross
3. RSI Momentum - RSI zone entries
4. Price Action - Candlestick patterns
5. Volume Spike - Unusual volume
6. Support/Resistance - Key level breaks

Strategy Types:
- Momentum (trend following)
- Mean Reversion (contrarian)
- Breakout (trend continuation)
- Scalping (quick trades)
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Dict, List, Optional, Callable
from enum import Enum
import random


class StrategyType(Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    COMPOSITE = "composite"


class SignalType(Enum):
    VWAP_BREAKOUT = "vwap_breakout"
    EMA_CROSSOVER = "ema_crossover"
    RSI_MOMENTUM = "rsi_momentum"
    PRICE_ACTION = "price_action"
    VOLUME_SPIKE = "volume_spike"
    SUPPORT_RESISTANCE = "support_resistance"


@dataclass
class Signal:
    """Trading signal"""
    signal_type: SignalType
    direction: str  # LONG, SHORT, NEUTRAL
    confidence: float  # 0-100
    entry_price: float
    stop_loss: float
    target: float
    reasoning: str
    timeframe: str = "5m"
    indicators: Dict = field(default_factory=dict)


@dataclass
class StrategyConfig:
    """Strategy configuration"""
    strategy_type: StrategyType
    min_confidence: float = 60
    max_positions: int = 3
    use_bracket_orders: bool = True
    
    # Signal weights
    vwap_weight: float = 0.25
    ema_weight: float = 0.25
    rsi_weight: float = 0.20
    volume_weight: float = 0.15
    price_action_weight: float = 0.15
    
    # Risk settings
    risk_per_trade: float = 1.0  # %
    target_return: float = 2.0  # % (2:1 RR)


class QuantStrategyEngine:
    """
    Quant Strategy Engine
    
    Generates trading signals through:
    - Multiple indicator analysis
    - Signal scoring system
    - Dynamic confidence calculation
    - Strategy-specific filtering
    """
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        
        # Signal history
        self.signal_history: List[Signal] = []
        self.active_signals: Dict[str, Signal] = {}
        
        # Performance tracking
        self.total_signals = 0
        self.winning_signals = 0
    
    def analyze_market_data(
        self,
        symbol: str,
        price: float,
        vwap: float,
        ema_9: float,
        ema_21: float,
        ema_50: float,
        rsi: float,
        volume: int,
        avg_volume: int,
        prev_price: float,
        prev_ema_9: float,
        prev_ema_21: float,
        high: float,
        low: float,
        open_price: float
    ) -> Optional[Signal]:
        """Generate trading signal from market data"""
        
        signals = {}
        
        # 1. VWAP Breakout Signal
        vwap_signal = self._check_vwap_breakout(price, vwap, volume, avg_volume)
        if vwap_signal:
            signals[SignalType.VWAP_BREAKOUT] = vwap_signal
        
        # 2. EMA Crossover Signal  
        ema_signal = self._check_ema_crossover(ema_9, ema_21, prev_ema_9, prev_ema_21)
        if ema_signal:
            signals[SignalType.EMA_CROSSOVER] = ema_signal
        
        # 3. RSI Momentum Signal
        rsi_signal = self._check_rsi_momentum(rsi)
        if rsi_signal:
            signals[SignalType.RSI_MOMENTUM] = rsi_signal
        
        # 4. Volume Spike Signal
        volume_signal = self._check_volume_spike(volume, avg_volume)
        if volume_signal:
            signals[SignalType.VOLUME_SPIKE] = volume_signal
        
        # 5. Price Action Signal
        pa_signal = self._check_price_action(open_price, high, low, price, prev_price)
        if pa_signal:
            signals[SignalType.PRICE_ACTION] = pa_signal
        
        if not signals:
            return None
        
        # Calculate weighted confidence
        combined = self._calculate_weighted_confidence(signals)
        
        # Filter by strategy type
        filtered = self._apply_strategy_filter(combined)
        
        if filtered and filtered.confidence >= self.config.min_confidence:
            self.total_signals += 1
            return filtered
        
        return None
    
    def _check_vwap_breakout(self, price: float, vwap: float, 
                            volume: int, avg_volume: int) -> Optional[Signal]:
        """Check VWAP breakout signal"""
        
        # Bullish breakout
        if price > vwap and volume > avg_volume * 1.3:
            conf = min(50 + (volume / avg_volume * 30), 90)
            reasoning = f"Price {price} above VWAP {vwap} with {volume/avg_volume:.1f}x volume"
            
            return Signal(
                signal_type=SignalType.VWAP_BREAKOUT,
                direction="LONG",
                confidence=conf,
                entry_price=price,
                stop_loss=price * 0.99,
                target=price * 1.02,
                reasoning=reasoning,
                indicators={"vwap": vwap, "volume_ratio": volume/avg_volume}
            )
        
        # Bearish breakdown
        if price < vwap and volume > avg_volume * 1.3:
            conf = min(50 + (volume / avg_volume * 30), 90)
            
            return Signal(
                signal_type=SignalType.VWAP_BREAKOUT,
                direction="SHORT",
                confidence=conf,
                entry_price=price,
                stop_loss=price * 1.01,
                target=price * 0.98,
                reasoning=f"Price {price} below VWAP {vwap} with volume spike",
                indicators={"vwap": vwap}
            )
        
        return None
    
    def _check_ema_crossover(self, ema_9: float, ema_21: float,
                              prev_ema_9: float, prev_ema_21: float) -> Optional[Signal]:
        """Check EMA crossover signal"""
        
        # Bullish crossover
        if ema_9 > ema_21 and prev_ema_9 <= prev_ema_21:
            return Signal(
                signal_type=SignalType.EMA_CROSSOVER,
                direction="LONG",
                confidence=75,
                entry_price=ema_9,
                stop_loss=ema_21,
                target=ema_9 * 1.02,
                reasoning=f"EMA9 {ema_9} crossed above EMA21 {ema_21}",
                indicators={"ema_9": ema_9, "ema_21": ema_21}
            )
        
        # Bearish crossover
        if ema_9 < ema_21 and prev_ema_9 >= prev_ema_21:
            return Signal(
                signal_type=SignalType.EMA_CROSSOVER,
                direction="SHORT",
                confidence=75,
                entry_price=ema_9,
                stop_loss=ema_21,
                target=ema_9 * 0.98,
                reasoning=f"EMA9 crossed below EMA21",
                indicators={"ema_9": ema_9, "ema_21": ema_21}
            )
        
        return None
    
    def _check_rsi_momentum(self, rsi: float) -> Optional[Signal]:
        """Check RSI momentum signal"""
        
        # Oversold bounce (bullish)
        if rsi < 35:
            conf = (35 - rsi) * 2 + 30
            return Signal(
                signal_type=SignalType.RSI_MOMENTUM,
                direction="LONG",
                confidence=min(conf, 80),
                entry_price=0,  # Current price
                stop_loss=0,
                target=0,
                reasoning=f"RSI oversold at {rsi:.0f} - potential bounce",
                indicators={"rsi": rsi}
            )
        
        # Overbought reversal (bearish)
        if rsi > 65:
            conf = (rsi - 65) * 2 + 30
            
            return Signal(
                signal_type=SignalType.RSI_MOMENTUM,
                direction="SHORT",
                confidence=min(conf, 80),
                entry_price=0,
                stop_loss=0,
                target=0,
                reasoning=f"RSI overbought at {rsi:.0f}",
                indicators={"rsi": rsi}
            )
        
        return None
    
    def _check_volume_spike(self, volume: int, avg_volume: int) -> Optional[Signal]:
        """Check volume spike signal"""
        
        if volume > avg_volume * 2:
            return Signal(
                signal_type=SignalType.VOLUME_SPIKE,
                direction="NEUTRAL",
                confidence=60,
                entry_price=0,
                stop_loss=0,
                target=0,
                reasoning=f"Volume spike: {volume/avg_volume:.1f}x average",
                indicators={"volume_ratio": volume/avg_volume}
            )
        
        return None
    
    def _check_price_action(self, open_price: float, high: float, 
                          low: float, price: float, prev_price: float) -> Optional[Signal]:
        """Check price action signal"""
        
        # Bullish engulfing
        if prev_price < open_price and price > high:
            return Signal(
                signal_type=SignalType.PRICE_ACTION,
                direction="LONG",
                confidence=70,
                entry_price=price,
                stop_loss=low,
                target=price * 1.015,
                reasoning="Bullish engulfing pattern",
                indicators={"pattern": "bullish_engulfing"}
            )
        
        return None
    
    def _calculate_weighted_confidence(self, signals: Dict[SignalType, Signal]) -> Signal:
        """Calculate weighted confidence from signals"""
        
        weights = {
            SignalType.VWAP_BREAKOUT: self.config.vwap_weight,
            SignalType.EMA_CROSSOVER: self.config.ema_weight,
            SignalType.RSI_MOMENTUM: self.config.rsi_weight,
            SignalType.VOLUME_SPIKE: self.config.volume_weight,
            SignalType.PRICE_ACTION: self.config.price_action_weight,
        }
        
        weighted_sum = 0
        weight_total = 0
        main_signal = None
        main_direction = "NEUTRAL"
        
        for sig_type, signal in signals.items():
            weight = weights.get(sig_type, 0.1)
            weighted_sum += signal.confidence * weight
            weight_total += weight
            
            if not main_signal or signal.confidence > main_signal.confidence:
                main_signal = signal
                main_direction = signal.direction
        
        confidence = weighted_sum / weight_total if weight_total > 0 else 0
        
        return Signal(
            signal_type=SignalType.VWAP_BREAKOUT,  # Composite
            direction=main_direction,
            confidence=confidence,
            entry_price=main_signal.entry_price if main_signal else 0,
            stop_loss=main_signal.stop_loss if main_signal else 0,
            target=main_signal.target if main_signal else 0,
            reasoning=f"Composite signal from {len(signals)} sources",
            indicators={st: si.confidence for st, si in signals.items()}
        )
    
    def _apply_strategy_filter(self, signal: Signal) -> Optional[Signal]:
        """Apply strategy-specific filtering"""
        
        if self.config.strategy_type == StrategyType.MOMENTUM:
            # Require trending (EMA aligned)
            if signal.indicators.get("ema_9", 0) < signal.indicators.get("ema_21", 0):
                return None
        
        elif self.config.strategy_type == StrategyType.MEAN_REVERSION:
            # Require oversold/overbought
            rsi_conf = signal.indicators.get("rsi", 50)
            if 35 < rsi_conf < 65:
                return None
        
        elif self.config.strategy_type == StrategyType.BREAKOUT:
            # Require volume
            if signal.indicators.get("volume_ratio", 1) < 1.5:
                return None
        
        return signal
    
    def record_result(self, was_win: bool):
        """Record signal result"""
        if was_win:
            self.winning_signals += 1
    
    def get_strategy_stats(self) -> Dict:
        """Get strategy performance stats"""
        
        win_rate = (self.winning_signals / self.total_signals * 100) if self.total_signals > 0 else 0
        
        return {
            "total_signals": self.total_signals,
            "winning_signals": self.winning_signals,
            "win_rate": round(win_rate, 1),
            "strategy_type": self.config.strategy_type.value,
            "min_confidence": self.config.min_confidence
        }


# ============ TEST ===========
def test_strategy_engine():
    """Test the strategy engine"""
    
    print("=" * 60)
    print("QUANT STRATEGY ENGINE TEST")
    print("=" * 60)
    
    # Create momentum strategy
    config = StrategyConfig(
        strategy_type=StrategyType.MOMENTUM,
        min_confidence=60
    )
    
    engine = QuantStrategyEngine(config)
    
    # Test with sample data (Bullish scenario)
    signal = engine.analyze_market_data(
        symbol="RELIANCE",
        price=2550,
        vwap=2520,
        ema_9=2540,
        ema_21=2510,
        ema_50=2480,
        rsi=45,
        volume=150000,
        avg_volume=100000,
        prev_price=2530,
        prev_ema_9=2500,
        prev_ema_21=2520,
        high=2560,
        low=2540,
        open_price=2545
    )
    
    if signal:
        print(f"\nSignal Generated:")
        print(f"  Direction: {signal.direction}")
        print(f"  Confidence: {signal.confidence}%")
        print(f"  Entry: ₹{signal.entry_price}")
        print(f"  Stop: ₹{signal.stop_loss}")
        print(f"  Target: ₹{signal.target}")
        print(f"  Reason: {signal.reasoning}")
        print(f"  Indicators: {signal.indicators}")
    else:
        print("\nNo signal generated")
    
    # Strategy stats
    stats = engine.get_strategy_stats()
    print(f"\nStrategy Stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_strategy_engine()