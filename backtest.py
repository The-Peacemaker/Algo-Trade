#!/usr/bin/env python3
"""
Historical Data Loader & Backtest
Loads historical data and simulates trading
"""

import asyncio
import logging
import random
from datetime import datetime
from trading_system import TradingSystem, TradeConfig, TradeDirection, SignalQuality
from data_fetcher import DataManager, MarketData, OHLC

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


def generate_historical_data(symbol: str, base_price: float, days: int = 30) -> list[OHLC]:
    """Generate realistic historical OHLC data"""
    data = []
    price = base_price
    
    for day in range(days):
        # Generate daily movement
        daily_change = random.uniform(-2, 2)  # -2% to +2%
        open_price = price
        close_price = price * (1 + daily_change / 100)
        
        high_price = max(open_price, close_price) * (1 + abs(random.uniform(0, 1)))
        low_price = min(open_price, close_price) * (1 - abs(random.uniform(0, 1)))
        
        volume = random.randint(50000, 200000)
        
        ohlc = OHLC(
            timestamp=datetime(2024, 1, 1) if day == 0 else datetime(2024, 1, 1 + day),
            open=round(open_price, 2),
            high=round(high_price, 2),
            low=round(low_price, 2),
            close=round(close_price, 2),
            volume=volume
        )
        data.append(ohlc)
        price = close_price
    
    return data


class Backtester:
    """Backtest the trading system"""
    
    def __init__(self, config: TradeConfig):
        self.config = config
        self.system = TradingSystem(config)
        self.data_manager = DataManager()
    
    def run_backtest(self, symbol: str, historical_data: list[OHLC], live_price: float) -> dict:
        """Run backtest with historical + live data"""
        
        # Load historical data
        for ohlc in historical_data:
            tick = type('Tick', (), {
                'symbol': symbol,
                'timestamp': ohlc.timestamp,
                'last_price': ohlc.close,
                'volume': ohlc.volume,
                'bid': ohlc.close - 1,
                'ask': ohlc.close + 1
            })()
            self.data_manager.add_tick(symbol, tick)
        
        # Get market data after historical
        market_data = self.data_manager.get_market_data(symbol)
        logger.info(f"Historical loaded. Current price: {market_data.current_price if market_data else live_price}")
        
        # Simulate live ticks
        for i in range(20):
            price_change = random.uniform(-0.5, 0.5)
            new_price = round(live_price + price_change, 2)
            
            from data_fetcher import TickData
            tick = TickData(
                symbol=symbol,
                timestamp=datetime.now(),
                last_price=new_price,
                volume=random.randint(50000, 150000),
                bid=round(new_price - 1, 2),
                ask=round(new_price + 1, 2)
            )
            
            self.data_manager.add_tick(symbol, tick)
            market_data = self.data_manager.get_market_data(symbol)
            
            if not market_data:
                continue
            
            # Get previous data for EMA crossover detection
            prev_data = self.data_manager.get_prev_market_data(symbol, 1)
            
            # Analyze
            signal = self.system.strategy.analyze_market_data(market_data, prev_data)
            
            # Check exit conditions
            self.system.check_exit_conditions(symbol, market_data)
            
            if signal.direction.value != "NO_TRADE" and signal.confidence >= 50:
                logger.info(f"Tick {i+1}: {signal.direction.value} | Conf: {signal.confidence}% | Price: {market_data.current_price:.2f}")
                logger.info(f"  → Entry: {signal.entry_price:.2f} | SL: {signal.stop_loss:.2f} | Target: {signal.target_price:.2f}")
                logger.info(f"  → {signal.reasoning[:60]}")
                
                # Execute trade if valid
                if signal.quality in [SignalQuality.STRONG, SignalQuality.MODERATE]:
                    self._execute_signal(symbol, signal)
        
        return self.system.get_status()
    
    def _execute_signal(self, symbol: str, signal):
        """Execute a signal"""
        if not self.system.risk_manager.check_daily_limits():
            return
        
        quantity, risk = self.system.risk_manager.calculate_position_size(
            signal.entry_price, signal.stop_loss
        )
        
        if quantity == 0:
            return
        
        from trading_system import Trade, TradeStatus
        trade = Trade(
            id=f"bt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            symbol=symbol,
            direction=signal.direction,
            entry_price=signal.entry_price,
            entry_time=datetime.now(),
            stop_loss=signal.stop_loss,
            target_price=signal.target_price,
            quantity=quantity,
            status=TradeStatus.ENTERED
        )
        
        self.system.active_trades.append(trade)
        self.system.risk_manager.daily_stats.trades_count += 1
        
        logger.info(f"*** TRADE EXECUTED: {trade.direction.value} {symbol} x {quantity} ***")


async def main():
    logger.info("=" * 60)
    logger.info("BACKTEST STARTING")
    logger.info("=" * 60)
    
    config = TradeConfig(
        capital=5000,
        max_risk_percent=2.0,
        max_trades_per_day=3,
        min_risk_reward=2.0,
        trading_symbols=["RELIANCE"],
        paper_mode=True
    )
    
    backtester = Backtester(config)
    
    # Generate historical data for RELIANCE
    hist_data = generate_historical_data("RELIANCE", 2500.0, 30)
    
    # Current live price
    live_price = 2525.0
    
    # Run backtest
    result = backtester.run_backtest("RELIANCE", hist_data, live_price)
    
    logger.info("=" * 60)
    logger.info("BACKTEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"Mode: {result['mode']}")
    logger.info(f"Capital: ₹{result['capital']}")
    logger.info(f"Trades executed: {result['daily_stats']['trades']}")
    logger.info(f"Wins: {result['daily_stats']['wins']}")
    logger.info(f"Losses: {result['daily_stats']['losses']}")
    logger.info(f"Total P&L: ₹{result['daily_stats']['pnl']:+.2f}")
    logger.info("=" * 60)


asyncio.run(main())