#!/usr/bin/env python3
"""
Signal Demo - Test the trading system with predefined signals
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from trading_system import TradingSystem, TradeConfig, TradeSignal, TradeDirection, SignalQuality
from data_fetcher import DataManager, MarketData, TickData, OHLC

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class SignalTester:
    """Test trading signals"""
    
    def __init__(self):
        self.config = TradeConfig(
            capital=5000,
            max_risk_percent=2.0,
            max_trades_per_day=3,
            min_risk_reward=2.0,
            trading_symbols=["RELIANCE", "TCS", "INFY"],
            paper_mode=True
        )
        self.system = TradingSystem(self.config)
        self.data_manager = DataManager()
    
    def create_live_tick(self, symbol: str, price: float, volume: int) -> MarketData:
        """Create a live tick"""
        tick = TickData(
            symbol=symbol,
            timestamp=datetime.now(),
            last_price=price,
            volume=volume,
            bid=price - 1,
            ask=price + 1
        )
        self.data_manager.add_tick(symbol, tick)
        return self.data_manager.get_market_data(symbol)
    
    def test_scenario_1(self):
        """Test: Bullish breakout scenario"""
        logger.info("\n" + "=" * 60)
        logger.info("SCENARIO 1: BULLISH BREAKOUT")
        logger.info("=" * 60)
        
        # Reset
        self.system = TradingSystem(self.config)
        self.data_manager = DataManager()
        
        # Generate OHLC bars directly - bullish trend
        base_price = 2500
        for i in range(30):
            price = base_price * (1 + 0.005 * i)  # Up 0.5% per bar
            ohlc = OHLC(
                timestamp=datetime.now(),
                open=round(price * 0.998, 2),
                high=round(price * 1.005, 2),
                low=round(price * 0.995, 2),
                close=round(price, 2),
                volume=100000 + i * 2000
            )
            # Use internal add_tick but with direct OHLC creation
            self.data_manager.ohlc_data["RELIANCE"] = self.data_manager.ohlc_data.get("RELIANCE", []) + [ohlc]
            self.data_manager.volume_history["RELIANCE"] = self.data_manager.volume_history.get("RELIANCE", []) + [ohlc.volume]
        
        # Live tick
        live_price = 2590
        market_data = self.data_manager.get_market_data("RELIANCE")
        
        if market_data is None:
            logger.error("No market data!")
            return
        
        prev_data = self.data_manager.get_prev_market_data("RELIANCE", 1)
        signal = self.system.strategy.analyze_market_data(market_data, prev_data)
        
        logger.info(f"Price: {market_data.current_price:.2f} | VWAP: {market_data.vwap:.2f}")
        logger.info(f"EMA9: {market_data.ema_9:.2f} | EMA21: {market_data.ema_21:.2f}")
        
        # Debug OHLC history
        ohlcs = self.data_manager.ohlc_data.get("RELIANCE", [])
        logger.info(f"OHLC bars: {len(ohlcs)}")
        if ohlcs:
            logger.info(f"First: {ohlcs[0].close}, Last: {ohlcs[-1].close}")
        
        logger.info(f"RSI: {market_data.rsi:.2f} | Vol: {market_data.volume}")
        logger.info(f"Direction: {signal.direction.value}")
        logger.info(f"Confidence: {signal.confidence}%")
        logger.info(f"Entry: {signal.entry_price} | SL: {signal.stop_loss} | Target: {signal.target_price}")
        logger.info(f"Reasoning: {signal.reasoning}")
    
    def test_scenario_2(self):
        """Test: Bearish breakdown scenario"""
        logger.info("\n" + "=" * 60)
        logger.info("SCENARIO 2: BEARISH BREAKDOWN")
        logger.info("=" * 60)
        
        # Reset
        self.system = TradingSystem(self.config)
        self.data_manager = DataManager()
        
        # Generate bearish trend
        base_price = 3200
        for i in range(30):
            price = base_price * (1 - 0.005 * i)
            tick = TickData(
                symbol="TCS",
                timestamp=datetime.now(),
                last_price=round(price, 2),
                volume=100000 + i * 2000,
                bid=round(price - 1, 2),
                ask=round(price + 1, 2)
            )
            self.data_manager.add_tick("TCS", tick)
        
        live_price = 3100
        market_data = self.create_live_tick("TCS", live_price, 150000)
        
        if market_data is None:
            return
        
        prev_data = self.data_manager.get_prev_market_data("TCS", 1)
        signal = self.system.strategy.analyze_market_data(market_data, prev_data)
        
        logger.info(f"Price: {market_data.current_price:.2f} | VWAP: {market_data.vwap:.2f}")
        logger.info(f"Direction: {signal.direction.value} | Conf: {signal.confidence}%")
        logger.info(f"Reasoning: {signal.reasoning}")
    
    def test_scenario_3(self):
        """Test: Sideways - NO TRADE"""
        logger.info("\n" + "=" * 60)
        logger.info("SCENARIO 3: SIDEWAYS MARKET (NO TRADE)")
        logger.info("=" * 60)
        
        # Reset
        self.system = TradingSystem(self.config)
        self.data_manager = DataManager()
        
        # Sideways - low volume
        base_price = 1400
        for i in range(30):
            price = base_price + random.uniform(-5, 5)
            tick = TickData(
                symbol="INFY",
                timestamp=datetime.now(),
                last_price=round(price, 2),
                volume=30000,  # Low volume
                bid=round(price - 1, 2),
                ask=round(price + 1, 2)
            )
            self.data_manager.add_tick("INFY", tick)
        
        market_data = self.create_live_tick("INFY", 1400, 35000)
        
        if market_data is None:
            return
        
        prev_data = self.data_manager.get_prev_market_data("INFY", 1)
        signal = self.system.strategy.analyze_market_data(market_data, prev_data)
        
        logger.info(f"Direction: {signal.direction.value} | Conf: {signal.confidence}%")
        logger.info(f"Reasoning: {signal.reasoning}")


async def main():
    tester = SignalTester()
    
    tester.test_scenario_1()
    tester.test_scenario_2()
    tester.test_scenario_3()
    
    logger.info("\n" + "=" * 60)
    logger.info("ALL SCENARIOS COMPLETED")
    logger.info("=" * 60)


asyncio.run(main())