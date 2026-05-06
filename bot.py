#!/usr/bin/env python3
"""
Main Trading Bot - Entry Point
Run this to start the algorithmic trading system
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from trading_system import TradingSystem, TradeConfig, TradeSignal
from data_fetcher import MockDataProvider, DataManager, TickData, OHLC, MarketData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


class TradingBot:
    """
    Main trading bot
    Orchestrates data fetching, signal generation, and trade execution
    """
    
    def __init__(self):
        self.config = TradeConfig(
            capital=5000,
            max_risk_percent=2.0,
            max_trades_per_day=3,
            min_risk_reward=2.0,
            trading_symbols=["RELIANCE", "TCS", "INFY"],
            trading_start="09:15",
            trading_end="15:00",
            paper_mode=True
        )
        
        self.system = TradingSystem(self.config)
        self.data_manager = DataManager()
        self.provider = None
        self.running = False
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logger.info("Received shutdown signal...")
        self.running = False
    
    async def start(self):
        """Start the trading bot"""
        logger.info("=" * 60)
        logger.info("ALGORITHMIC TRADING SYSTEM STARTED")
        logger.info("=" * 60)
        logger.info(f"Mode: {'PAPER' if self.config.paper_mode else 'LIVE'}")
        logger.info(f"Capital: ₹{self.config.capital}")
        logger.info(f"Max Risk/Trade: {self.config.max_risk_percent}%")
        logger.info(f"Symbols: {self.config.trading_symbols}")
        logger.info("=" * 60)
        
        self.running = True
        
        # Initialize mock data provider for testing
        self.provider = MockDataProvider({"symbols": self.config.trading_symbols})
        
        # Connect mock data
        await self.provider.connect()
        
        # Subscribe to symbols
        await self.provider.subscribe(self.config.trading_symbols)
        
        # Process data in main loop
        while self.running:
            try:
                # Get latest tick data from provider
                for symbol in self.config.trading_symbols:
                    tick = self.provider.last_data.get(symbol)
                    if tick:
                        await self.process_tick(symbol, tick)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)
        
        await self.shutdown()
    
    async def process_tick(self, symbol: str, tick):
        """Process incoming tick data"""
        
        # Add tick to data manager
        self.data_manager.add_tick(symbol, tick)
        
        # Get calculated market data
        market_data = self.data_manager.get_market_data(symbol)
        
        if not market_data:
            return
        
        # Check exit conditions for active trades
        self.system.check_exit_conditions(symbol, market_data)
        
        # Analyze and generate signal
        prev_data = None
        if symbol in self.data_manager.ohlc_data and len(self.data_manager.ohlc_data[symbol]) > 1:
            prev_ohlc = self.data_manager.ohlc_data[symbol][-2]
            prev_data = MarketData(
                symbol=symbol,
                current_price=prev_ohlc.close,
                vwap=market_data.vwap,
                rsi=market_data.rsi,
                ema_9=market_data.ema_9,
                ema_21=market_data.ema_21,
                volume=prev_ohlc.volume,
                avg_volume=market_data.avg_volume
            )
        
        # Feed to strategy engine
        signal = self.system.strategy.analyze_market_data(market_data, prev_data)
        
        # Log signal (limit logging frequency)
        if signal.direction.value != "NO_TRADE" and signal.confidence > 50:
            logger.info(f"[{symbol}] {signal.direction.value} | Conf: {signal.confidence}% | Price: {market_data.current_price:.2f}")
            logger.info(f"  → Entry: {signal.entry_price:.2f} | SL: {signal.stop_loss:.2f} | Target: {signal.target_price:.2f}")
            logger.info(f"  → {signal.reasoning}")
    
    async def shutdown(self):
        """Shutdown the bot"""
        logger.info("Shutting down trading system...")
        
        if self.provider:
            await self.provider.disconnect()
        
        # Print final stats
        status = self.system.get_status()
        logger.info("=" * 60)
        logger.info("FINAL DAILY STATS")
        logger.info("=" * 60)
        logger.info(f"Total Trades: {status['daily_stats']['trades']}")
        logger.info(f"Wins: {status['daily_stats']['wins']} | Losses: {status['daily_stats']['losses']}")
        logger.info(f"Total P&L: ₹{status['daily_stats']['pnl']:+.2f}")
        logger.info("=" * 60)
        
        logger.info("Trading system stopped.")


async def main():
    """Main entry point"""
    bot = TradingBot()
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)