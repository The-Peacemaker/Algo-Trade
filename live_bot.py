#!/usr/bin/env python3
"""
Complete Live Trading Bot
Integrates: Strategy Engine + Live Data + Risk Management
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from trading_system import TradingSystem, TradeConfig, TradeSignal, TradeDirection, SignalQuality, Trade, TradeStatus
from data_fetcher import DataManager, MarketData, TickData, OHLC
from live_data import LiveDataManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LiveTradingBot:
    """Complete live trading bot"""
    
    def __init__(self, config: TradeConfig):
        self.config = config
        self.system = TradingSystem(config)
        self.data_manager = DataManager()
        self.data_manager_live = LiveDataManager()
        
        self.running = False
        self.tick_count = 0
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logger.info("Shutdown signal received...")
        self.running = False
    
    async def on_tick(self, symbol: str, data: dict):
        """Process incoming tick"""
        self.tick_count += 1
        
        # Convert to OHLC
        tick = TickData(
            symbol=symbol,
            timestamp=data.get("timestamp", datetime.now()),
            last_price=data["last_price"],
            volume=data["volume"],
            bid=data.get("bid", data["last_price"] - 1),
            ask=data.get("ask", data["last_price"] + 1)
        )
        
        # Add to data manager
        self.data_manager.add_tick(symbol, tick)
        
        # Get market data
        market_data = self.data_manager.get_market_data(symbol)
        if not market_data:
            return
        
        # Get previous for EMA crossover
        prev_data = self.data_manager.get_prev_market_data(symbol, 1)
        
        # Analyze
        signal_obj = self.system.strategy.analyze_market_data(market_data, prev_data, bypass=True)
        
        # Check exit conditions
        self.system.check_exit_conditions(symbol, market_data)
        
        # Log signals (throttled)
        if signal_obj.direction != TradeDirection.NO_TRADE:
            logger.info(f"📊 {symbol}: {signal_obj.direction.value} | Conf: {signal_obj.confidence}% | Price: ₹{market_data.current_price}")
            logger.info(f"   Entry: {signal_obj.entry_price} | SL: {signal_obj.stop_loss} | Target: {signal_obj.target_price}")
        
        # Execute if valid signal
        if signal_obj.direction != TradeDirection.NO_TRADE and signal_obj.confidence >= 75:
            if signal_obj.quality in [SignalQuality.STRONG, SignalQuality.MODERATE]:
                await self._execute_trade(symbol, signal_obj)
    
    async def _execute_trade(self, symbol: str, signal: TradeSignal):
        """Execute trade"""
        # Check limits
        if not self.system.risk_manager.check_daily_limits():
            logger.info("Daily limits reached")
            return
        
        # Check if already in position
        for trade in self.system.active_trades:
            if trade.symbol == symbol:
                logger.info(f"Already in position for {symbol}")
                return
        
        # Get current market data
        market_data = self.data_manager.get_market_data(symbol)
        if not market_data:
            logger.warning(f"No market data for {symbol}")
            return
        
        # Calculate position size
        quantity, risk = self.system.risk_manager.calculate_position_size(
            signal.entry_price, signal.stop_loss
        )
        
        if quantity == 0:
            logger.warning(f"Cannot size position for {symbol}")
            return
        
        # Execute
        self.system.on_tick(symbol, market_data)
        
        mode = "PAPER" if self.config.paper_mode else "LIVE"
        logger.info(f"""
╔══════════════════════════════════════════╗
║  🔔 {mode} TRADE EXECUTED              ║
╠══════════════════════════════════════════╣
║  Symbol:     {symbol:<10}              ║
║  Direction:  {signal.direction.value:<5}                ║
║  Entry:     ₹{signal.entry_price:<.2f}                ║
║  Stop:      ₹{signal.stop_loss:<.2f}                ║
║  Target:    ₹{signal.target_price:<.2f}                ║
║  Qty:       {quantity:<d}                    ║
║  Risk:      {signal.risk_percent:.2f}%                   ║
╚══════════════════════════════════════════╝
        """)
    
    async def start(self):
        """Start the bot"""
        logger.info("=" * 60)
        logger.info("🚀 LIVE TRADING BOT STARTED")
        logger.info("=" * 60)
        logger.info(f"Mode: {'PAPER' if self.config.paper_mode else 'LIVE'}")
        logger.info(f"Capital: ₹{self.config.capital}")
        logger.info(f"Max Risk/Trade: {self.config.max_risk_percent}%")
        logger.info(f"Symbols: {self.config.trading_symbols}")
        logger.info("=" * 60)
        
        self.running = True
        
        # Start live data feed (mock for demo)
        feed = self.data_manager_live.start_live(
            self.config.trading_symbols,
            feed_type="mock",
            base_prices={
                "RELIANCE": 2500,
                "TCS": 3200,
                "INFY": 1400
            }
        )
        
        self.data_manager_live.set_tick_handler(self.on_tick)
        
        # Run
        await self.data_manager_live.run()
        
        # Wait for shutdown
        while self.running:
            await asyncio.sleep(1)
            
            # Status every 60 seconds
            if self.tick_count % 30 == 0:
                status = self.system.get_status()
                logger.info(f"📊 Status: {status['active_trades']} active, {status['daily_stats']['trades']} today")
        
        await self.shutdown()
    
    async def shutdown(self):
        """Shutdown"""
        logger.info("Shutting down...")
        
        if self.data_manager_live.feed:
            await self.data_manager_live.feed.stop()
        
        # Final stats
        status = self.system.get_status()
        logger.info("=" * 60)
        logger.info("📈 FINAL STATS")
        logger.info("=" * 60)
        logger.info(f"Total Trades: {status['daily_stats']['trades']}")
        logger.info(f"Wins: {status['daily_stats']['wins']} | Losses: {status['daily_stats']['losses']}")
        logger.info(f"P&L: ₹{status['daily_stats']['pnl']:+.2f}")
        logger.info("=" * 60)


async def main():
    """Main"""
    config = TradeConfig(
        capital=5000,
        max_risk_percent=2.0,
        max_trades_per_day=3,
        min_risk_reward=2.0,
        trading_symbols=["RELIANCE", "TCS", "INFY"],
        trading_start="09:15",
        trading_end="15:00",
        paper_mode=True  # Change to False for live
    )
    
    bot = LiveTradingBot(config)
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        sys.exit(0)