#!/usr/bin/env python3
"""
Algorithmic Trading System

A disciplined, risk-managed algorithmic trading system for Indian stock markets.
Implements technical analysis-based strategy with strict risk management rules.

Features:
- Technical indicators (VWAP, EMA, RSI)
- Risk management (position sizing, stop-loss, risk-reward)
- Signal generation based on multiple conditions
- Paper trading mode for testing

Usage:
    from trading_system import TradingSystem, TradeConfig
    
    config = TradeConfig(capital=5000, paper_mode=True)
    system = TradingSystem(config)
"""

import json
import logging
from datetime import datetime, time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
import math

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradeDirection(Enum):
    LONG = "LONG"
    SELL = "SELL"  # Short (intraday sell)
    NO_TRADE = "NO_TRADE"


class SignalQuality(Enum):
    STRONG = "STRONG"      # All conditions met
    MODERATE = "MODERATE"  # Most conditions met
    WEAK = "WEAK"          # Mixed signals
    NO_SIGNAL = "NO_SIGNAL"


class TradeStatus(Enum):
    PENDING = "PENDING"
    ENTERED = "ENTERED"
    EXITED = "EXITED"
    STOPPED = "STOPPED"


@dataclass
class OHLC:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass
class MarketData:
    symbol: str
    current_price: float
    vwap: float
    rsi: float = 0
    ema_9: float = 0
    ema_21: float = 0
    volume: int = 0
    avg_volume: int = 0
    ohlc: Optional[OHLC] = None


@dataclass
class TradeConfig:
    capital: float = 5000
    max_risk_percent: float = 2.0
    max_trades_per_day: int = 3
    min_risk_reward: float = 2.0
    trading_symbols: List[str] = field(default_factory=lambda: ["RELIANCE", "TCS", "INFY"])
    trading_start: str = "09:15"
    trading_end: str = "15:00"
    paper_mode: bool = True


@dataclass
class TradeSignal:
    direction: TradeDirection
    confidence: int  # 0-100
    entry_price: float
    stop_loss: float
    target_price: float
    risk_percent: float
    reasoning: str
    quality: SignalQuality = SignalQuality.NO_SIGNAL


@dataclass
class Trade:
    id: str
    symbol: str
    direction: TradeDirection
    entry_price: float
    entry_time: datetime
    stop_loss: float
    target_price: float
    quantity: int = 0
    status: TradeStatus = TradeStatus.PENDING
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: float = 0


@dataclass
class DailyStats:
    date: str
    trades: List[Trade] = field(default_factory=list)
    trades_count: int = 0
    wins: int = 0
    losses: int = 0
    total_pnl: float = 0
    consecutive_losses: int = 0


class RiskManager:
    def __init__(self, config: TradeConfig):
        self.config = config
        self.daily_stats = DailyStats(date=datetime.now().strftime("%Y-%m-%d"))

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> tuple[int, float]:
        """Calculate quantity and risk amount based on capital and stop loss"""
        risk_amount = (self.config.capital * self.config.max_risk_percent) / 100
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return 0, 0
            
        quantity = int(risk_amount / risk_per_share)
        actual_risk = quantity * risk_per_share
        
        return quantity, round(actual_risk, 2)

    def check_daily_limits(self) -> bool:
        """Check if daily trading limits are met"""
        if self.daily_stats.trades_count >= self.config.max_trades_per_day:
            logger.warning("Daily trade limit reached")
            return False
        
        if self.daily_stats.consecutive_losses >= 2:
            logger.warning("2 consecutive losses - stopping for the day")
            return False
        
        return True

    def record_trade_result(self, trade: Trade):
        self.daily_stats.trades.append(trade)
        self.daily_stats.trades_count += 1
        
        if trade.pnl > 0:
            self.daily_stats.wins += 1
            self.daily_stats.consecutive_losses = 0
        else:
            self.daily_stats.losses += 1
            self.daily_stats.consecutive_losses += 1
        
        self.daily_stats.total_pnl += trade.pnl


class StrategyEngine:
    def __init__(self, config: TradeConfig):
        self.config = config

    def analyze_market_data(self, data: MarketData, prev_data: Optional[MarketData] = None, bypass: bool = False) -> TradeSignal:
        """Analyze market data and generate trade signal"""
        
        # Handle None data
        if data is None:
            return TradeSignal(
                direction=TradeDirection.NO_TRADE,
                confidence=0,
                entry_price=0,
                stop_loss=0,
                target_price=0,
                risk_percent=0,
                reasoning="No market data",
                quality=SignalQuality.NO_SIGNAL
            )
        
        # Check market hours
        if not bypass and not self._is_market_hours(bypass=True):
            return TradeSignal(
                direction=TradeDirection.NO_TRADE,
                confidence=0,
                entry_price=data.current_price,
                stop_loss=0,
                target_price=0,
                risk_percent=0,
                reasoning="Outside market hours",
                quality=SignalQuality.NO_SIGNAL
            )
        
        # Analyze conditions
        long_conditions = self._check_long_conditions(data, prev_data)
        short_conditions = self._check_short_conditions(data, prev_data)
        
        if long_conditions["score"] >= 4:
            return self._create_signal(TradeDirection.LONG, data, prev_data, long_conditions)
        elif short_conditions["score"] >= 4:
            return self._create_signal(TradeDirection.SELL, data, prev_data, short_conditions)
        
        return TradeSignal(
            direction=TradeDirection.NO_TRADE,
            confidence=20,
            entry_price=data.current_price,
            stop_loss=0,
            target_price=0,
            risk_percent=0,
            reasoning="No clear signals - mixed or unclear conditions",
            quality=SignalQuality.NO_SIGNAL
        )

    def _is_market_hours(self, bypass: bool = False) -> bool:
        if bypass:
            return True
        now = datetime.now().time()
        start = time(int(self.config.trading_start.split(":")[0]), int(self.config.trading_start.split(":")[1]))
        end = time(int(self.config.trading_end.split(":")[0]), int(self.config.trading_end.split(":")[1]))
        return start <= now <= end

    def _check_long_conditions(self, data: MarketData, prev_data: Optional[MarketData]) -> Dict[str, Any]:
        score = 0
        reasons = []
        
        # 1. Price above VWAP (critical)
        if data.current_price > data.vwap:
            score += 2
            reasons.append("✓ Price above VWAP")
        else:
            return {"score": 0, "reasons": ["✗ Price below VWAP"]}  # Early exit
        
        # 2. Bullish EMA crossover
        if prev_data and data.ema_9 > data.ema_21 and prev_data.ema_9 <= prev_data.ema_21:
            score += 2
            reasons.append("✓ EMA bullish crossover")
        elif data.ema_9 > data.ema_21:
            score += 1
            reasons.append("✓ EMA9 > EMA21")
        
        # 3. Volume confirmation (must have)
        if data.volume > data.avg_volume * 1.3:
            score += 2
            reasons.append("✓ Volume spike")
        elif data.volume > data.avg_volume:
            score += 1
        
        # 4. RSI momentum
        if 35 < data.rsi < 65:
            score += 1
            reasons.append("✓ RSI in range")
        
        return {"score": score, "reasons": reasons}

    def _check_short_conditions(self, data: MarketData, prev_data: Optional[MarketData]) -> Dict[str, Any]:
        score = 0
        reasons = []
        
        # 1. Price below VWAP
        if data.current_price < data.vwap:
            score += 2
            reasons.append("✓ Price below VWAP")
        
        # 2. Bearish EMA crossover
        if prev_data and data.ema_9 < data.ema_21 and prev_data.ema_9 >= prev_data.ema_21:
            score += 2
            reasons.append("✓ EMA bearish crossover")
        elif data.ema_9 < data.ema_21:
            score += 1
        
        # 3. Volume confirmation
        if data.volume > data.avg_volume * 1.2:
            score += 2
        
        # 4. RSI not oversold
        if 30 < data.rsi < 70:
            score += 1
        
        return {"score": score, "reasons": reasons}

    def _create_signal(self, direction: TradeDirection, data: MarketData, prev_data: Optional[MarketData], conditions: Dict) -> TradeSignal:
        
        entry_price = data.current_price
        
        if direction == TradeDirection.LONG:
            stop_loss = entry_price * 0.985  # 1.5% stop
            target = entry_price * 1.035  # 3.5% target (1:2.3 RR)
        else:
            stop_loss = entry_price * 1.015
            target = entry_price * 0.965
        
        risk_percent = abs(entry_price - stop_loss) / entry_price * 100
        risk_reward_ratio = abs(target - entry_price) / abs(entry_price - stop_loss)
        
        quality = SignalQuality.STRONG if conditions["score"] >= 5 else SignalQuality.MODERATE
        confidence = min(conditions["score"] * 18, 95)
        
        if risk_reward_ratio < self.config.min_risk_reward:
            return TradeSignal(
                direction=TradeDirection.NO_TRADE,
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                target_price=target,
                risk_percent=0,
                reasoning=f"Poor RR ratio: {risk_reward_ratio:.1f}",
                quality=SignalQuality.WEAK
            )
        
        return TradeSignal(
            direction=direction,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=round(stop_loss, 2),
            target_price=round(target, 2),
            risk_percent=round(risk_percent, 2),
            reasoning=" | ".join(conditions["reasons"]),
            quality=quality
        )


class TradingSystem:
    def __init__(self, config: TradeConfig):
        self.config = config
        self.risk_manager = RiskManager(config)
        self.strategy = StrategyEngine(config)
        self.active_trades: List[Trade] = []
        self.symbol_data: Dict[str, List[MarketData]] = {}

    def on_tick(self, symbol: str, data: MarketData):
        """Process incoming market data tick"""
        if symbol not in self.symbol_data:
            self.symbol_data[symbol] = []
        
        self.symbol_data[symbol].append(data)
        prev_data = self.symbol_data[symbol][-2] if len(self.symbol_data[symbol]) > 1 else None
        
        signal = self.strategy.analyze_market_data(data, prev_data)
        
        if signal.direction != TradeDirection.NO_TRADE and signal.confidence >= 60:
            self._execute_signal(symbol, signal)

    def _execute_signal(self, symbol: str, signal: TradeSignal):
        if not self.risk_manager.check_daily_limits():
            return
        
        quantity, risk = self.risk_manager.calculate_position_size(
            signal.entry_price, signal.stop_loss
        )
        
        if quantity == 0:
            logger.warning(f"Cannot calculate position size for {symbol}")
            return
        
        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        trade = Trade(
            id=trade_id,
            symbol=symbol,
            direction=signal.direction,
            entry_price=signal.entry_price,
            entry_time=datetime.now(),
            stop_loss=signal.stop_loss,
            target_price=signal.target_price,
            quantity=quantity,
            status=TradeStatus.ENTERED
        )
        
        self.active_trades.append(trade)
        self.risk_manager.daily_stats.trades_count += 1
        
        self._log_trade(trade, signal)

    def _log_trade(self, trade: Trade, signal: TradeSignal):
        if self.config.paper_mode:
            mode = "PAPER"
        else:
            mode = "LIVE"
        
        logger.info(f"""
╔══════════════════════════════════════════════════════════════╗
║  {mode} TRADE EXECUTED                                      ║
╠══════════════════════════════════════════════════════════════╣
║  Symbol:      {trade.symbol:<10}  Direction:  {trade.direction.value}               ║
║  Entry:       ₹{trade.entry_price:<10.2f}  Stop Loss:   ₹{trade.stop_loss:<10.2f}              ║
║  Target:      ₹{trade.target_price:<10.2f}  Quantity:   {trade.quantity:<10d}              ║
║  Risk:        ₹{signal.risk_percent:.2f}%        Confidence: {signal.confidence}%              ║
║  Reasoning:   {signal.reasoning[:40]:<40}         ║
╚══════════════════════════════════════════════════════════════╝
        """)

    def exit_trade(self, trade: Trade, exit_price: float, reason: str):
        """Exit a trade"""
        trade.exit_price = exit_price
        trade.exit_time = datetime.now()
        trade.status = TradeStatus.EXITED
        
        if trade.direction == TradeDirection.LONG:
            trade.pnl = (exit_price - trade.entry_price) * trade.quantity
        else:
            trade.pnl = (trade.entry_price - exit_price) * trade.quantity
        
        self.risk_manager.record_trade_result(trade)
        
        logger.info(f"""
╔══════════════════════════════════════════════════════════════╗
║  TRADE EXITED                                              ║
╠══════════════════════════════════════════════════════════════╣
║  Symbol:     {trade.symbol:<10}  P&L:        ₹{trade.pnl:+.2f}                ║
║  Reason:     {reason:<40}         ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        self.active_trades.remove(trade)

    def check_exit_conditions(self, symbol: str, data: MarketData):
        """Check if any active trade should be exited"""
        for trade in self.active_trades:
            if trade.symbol != symbol:
                continue
            
            should_exit = False
            exit_reason = ""
            
            if trade.direction == TradeDirection.LONG:
                if data.current_price <= trade.stop_loss:
                    should_exit = True
                    exit_reason = "Stop loss hit"
                elif data.current_price >= trade.target_price:
                    should_exit = True
                    exit_reason = "Target reached"
                elif data.current_price < data.vwap:
                    should_exit = True
                    exit_reason = "Price below VWAP (trend reversal)"
            else:
                if data.current_price >= trade.stop_loss:
                    should_exit = True
                    exit_reason = "Stop loss hit"
                elif data.current_price <= trade.target_price:
                    should_exit = True
                    exit_reason = "Target reached"
                elif data.current_price > data.vwap:
                    should_exit = True
                    exit_reason = "Price above VWAP (trend reversal)"
            
            if should_exit:
                self.exit_trade(trade, data.current_price, exit_reason)

    def get_status(self) -> Dict[str, Any]:
        """Get current trading system status"""
        return {
            "mode": "PAPER" if self.config.paper_mode else "LIVE",
            "capital": self.config.capital,
            "daily_stats": {
                "trades": self.risk_manager.daily_stats.trades_count,
                "wins": self.risk_manager.daily_stats.wins,
                "losses": self.risk_manager.daily_stats.losses,
                "pnl": self.risk_manager.daily_stats.total_pnl,
                "consecutive_losses": self.risk_manager.daily_stats.consecutive_losses
            },
            "active_trades": len(self.active_trades)
        }