#!/usr/bin/env python3
"""
Market Data Fetcher and Indicator Calculator

Provides:
- Real-time tick data handling
- OHLC candle management
- Technical indicators (VWAP, EMA, RSI)
- Mock data provider for testing

Supports multiple data sources including:
- WebSocket feeds
- REST API polling
- Mock data for backtesting
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TickData:
    symbol: str
    timestamp: datetime
    last_price: float
    volume: int
    bid: float
    ask: float
    open_int: int = 0


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
    rsi: float
    ema_9: float
    ema_21: float
    volume: int
    avg_volume: int
    ohlc: Optional[OHLC] = None


class MockDataProvider:
    """Mock data provider for testing"""
    
    def __init__(self, config: dict):
        self.config = config
        self.symbols = config.get("symbols", ["RELIANCE", "TCS", "INFY"])
        self.prices = {
            "RELIANCE": 2500.0,
            "TCS": 3200.0,
            "INFY": 1400.0
        }
        self.callback: Optional[Callable] = None
        self.last_data: Dict[str, TickData] = {}
        self.running = False
    
    def set_callback(self, callback: Callable):
        self.callback = callback
    
    async def connect(self):
        self.running = True
        logger.info("Mock data provider connected")
        asyncio.create_task(self._generate_data())
    
    async def disconnect(self):
        self.running = False
        logger.info("Mock data provider disconnected")
    
    async def subscribe(self, symbols: List[str]):
        logger.info(f"Subscribed to: {symbols}")
    
    async def _generate_data(self):
        while self.running:
            for symbol in list(self.symbols):
                base_price = self.prices.get(symbol, 1000)
                change = random.uniform(-10, 10)
                new_price = round(base_price + change, 2)
                self.prices[symbol] = new_price
                
                tick = TickData(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    last_price=new_price,
                    volume=random.randint(1000, 10000),
                    bid=round(new_price - 1, 2),
                    ask=round(new_price + 1, 2)
                )
                
                self.last_data[symbol] = tick
                
                if self.callback:
                    try:
                        result = self.callback(symbol, tick)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
            
            await asyncio.sleep(2)


class DataManager:
    """Manages market data and calculates indicators"""
    
    def __init__(self):
        self.ohlc_data: Dict[str, List[OHLC]] = {}
        self.volume_history: Dict[str, List[int]] = {}
    
    def add_tick(self, symbol: str, tick: TickData):
        if symbol not in self.ohlc_data:
            self.ohlc_data[symbol] = []
            self.volume_history[symbol] = []
        
        if not self.ohlc_data[symbol]:
            current = OHLC(
                timestamp=tick.timestamp,
                open=tick.last_price,
                high=tick.last_price,
                low=tick.last_price,
                close=tick.last_price,
                volume=tick.volume
            )
            self.ohlc_data[symbol].append(current)
        else:
            current = self.ohlc_data[symbol][-1]
            current.high = max(current.high, tick.last_price)
            current.low = min(current.low, tick.last_price)
            current.close = tick.last_price
            current.volume += tick.volume
        
        self.volume_history[symbol].append(tick.volume)
        
        if len(self.ohlc_data[symbol]) > 300:
            self.ohlc_data[symbol] = self.ohlc_data[symbol][-300:]
        if len(self.volume_history[symbol]) > 300:
            self.volume_history[symbol] = self.volume_history[symbol][-300:]
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        if symbol not in self.ohlc_data or not self.ohlc_data[symbol]:
            return None
        
        ohlcs = self.ohlc_data[symbol]
        volumes = self.volume_history.get(symbol, [])
        
        if len(ohlcs) < 1:
            return None
        
        current = ohlcs[-1]
        vwap = self._calculate_vwap(ohlcs)
        ema_9 = self._calculate_ema(ohlcs, 9)
        ema_21 = self._calculate_ema(ohlcs, 21)
        rsi = self._calculate_rsi(ohlcs)
        
        avg_vol = sum(volumes[-20:]) / len(volumes[-20:]) if volumes else 0
        
        return MarketData(
            symbol=symbol,
            current_price=current.close,
            vwap=vwap,
            rsi=rsi,
            ema_9=ema_9,
            ema_21=ema_21,
            volume=current.volume,
            avg_volume=int(avg_vol),
            ohlc=current
        )
    
    def _calculate_vwap(self, ohlcs: List[OHLC]) -> float:
        if not ohlcs:
            return 0
        pv = sum(o.close * o.volume for o in ohlcs[-50:])
        v = sum(o.volume for o in ohlcs[-50:])
        return pv / v if v else ohlcs[-1].close
    
    def _calculate_ema(self, ohlcs: List[OHLC], period: int) -> float:
        if len(ohlcs) < period:
            return ohlcs[-1].close if ohlcs else 0
        
        # First EMA = SMA of first 'period' bars
        sma = sum(o.close for o in ohlcs[:period]) / period
        
        mult = 2 / (period + 1)
        ema = sma
        
        # EMA for remaining bars
        for o in ohlcs[period:]:
            ema = (o.close - ema) * mult + ema
        
        return ema
    
    def _calculate_rsi(self, ohlcs: List[OHLC], period: int = 14) -> float:
        if len(ohlcs) < period + 1:
            return 50
        
        gains, losses = [], []
        for i in range(1, min(period + 1, len(ohlcs))):
            chg = ohlcs[i].close - ohlcs[i - 1].close
            gains.append(chg if chg > 0 else 0)
            losses.append(abs(chg) if chg < 0 else 0)
        
        avg_g = sum(gains) / period
        avg_l = sum(losses) / period
        
        if avg_l == 0:
            return 100
        
        rs = avg_g / avg_l
        return 100 - (100 / (1 + rs))
    
    def get_prev_market_data(self, symbol: str, bars_back: int = 1) -> Optional[MarketData]:
        if symbol not in self.ohlc_data or len(self.ohlc_data[symbol]) <= bars_back:
            return None
        
        ohlcs = self.ohlc_data[symbol]
        idx = -1 - bars_back
        prev = ohlcs[idx]
        volumes = self.volume_history.get(symbol, [])
        
        vwap = sum(o.close * o.volume for o in ohlcs[idx-50:idx]) / sum(o.volume for o in ohlcs[idx-50:idx]) if idx <= -51 else prev.close
        ema_9 = sum(o.close for o in ohlcs[idx-9:idx]) / 9 if idx <= -9 else prev.close
        ema_21 = sum(o.close for o in ohlcs[idx-21:idx]) / 21 if idx <= -21 else prev.close
        
        return MarketData(
            symbol=symbol,
            current_price=prev.close,
            vwap=vwap,
            rsi=50,
            ema_9=ema_9,
            ema_21=ema_21,
            volume=prev.volume,
            avg_volume=int(sum(volumes[-20:]) / 20) if volumes else 0,
            ohlc=prev
        )