#!/usr/bin/env python3
"""
Live Data Connector - Real-time market data
Supports: WebSocket feeds, REST polling
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class DataFeed:
    """Base class for live data feeds"""
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.callback: Optional[Callable] = None
        self.running = False
    
    def set_callback(self, callback: Callable):
        self.callback = callback
    
    async def connect(self):
        raise NotImplementedError
    
    async def disconnect(self):
        pass
    
    async def start(self):
        self.running = True
        await self.connect()
    
    async def stop(self):
        self.running = False
        await self.disconnect()


class WebSocketFeed(DataFeed):
    """WebSocket-based live data feed"""
    
    def __init__(self, symbols: List[str], provider: str = "angel_one"):
        super().__init__(symbols)
        self.provider = provider
        self.ws = None
        self.reconnect_delay = 5
    
    async def connect(self):
        logger.info(f"Connecting to {self.provider} WebSocket...")
        
        if self.provider == "angel_one":
            await self._connect_angel_one()
        elif self.provider == "zerodha":
            await self._connect_zerodha()
        else:
            logger.warning(f"Unknown provider: {self.provider}")
    
    async def _connect_angel_one(self):
        """Angel One SmartAPI WebSocket"""
        # Angel One uses different endpoints for market data
        # This requires API key + session token
        logger.info("Angel One WebSocket: Use SmartAPI credentials in broker_integration.py")
        # In production: connect to wss://api.angelone.in/smartwebsocket
    
    async def _connect_zerodha(self):
        """Zerodha Kite WebSocket"""
        logger.info("Zerodha WebSocket: Use Kite credentials")


class PollingFeed(DataFeed):
    """REST API polling-based feed (fallback)"""
    
    def __init__(self, symbols: List[str], api_client=None, interval: float = 5.0):
        super().__init__(symbols)
        self.api_client = api_client
        self.interval = interval
        self.task = None
    
    async def connect(self):
        logger.info(f"Starting polling feed for {self.symbols} every {self.interval}s")
        self.task = asyncio.create_task(self._poll_loop())
    
    async def disconnect(self):
        if self.task:
            self.task.cancel()
    
    async def _poll_loop(self):
        """Polling loop"""
        while self.running:
            try:
                for symbol in self.symbols:
                    data = await self._fetch_data(symbol)
                    if data and self.callback:
                        await self._dispatch(symbol, data)
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from API"""
        if self.api_client:
            return await self.api_client.get_quote(symbol)
        return None
    
    async def _dispatch(self, symbol: str, data: Dict):
        """Dispatch data to callback"""
        if self.callback:
            try:
                result = self.callback(symbol, data)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Callback error: {e}")


class MockLiveFeed(DataFeed):
    """Mock live feed for testing"""
    
    def __init__(self, symbols: List[str], base_prices: Dict[str, float]):
        super().__init__(symbols)
        self.prices = base_prices.copy()
        self.task = None
    
    async def connect(self):
        logger.info("MockLiveFeed connected")
        self.task = asyncio.create_task(self._generate_ticks())
    
    async def disconnect(self):
        if self.task:
            self.task.cancel()
    
    async def _generate_ticks(self):
        """Generate realistic ticks"""
        import random
        
        while self.running:
            for symbol in self.symbols:
                if symbol in self.prices:
                    # Random walk
                    change = random.uniform(-0.3, 0.3)
                    self.prices[symbol] = round(self.prices[symbol] + change, 2)
                    
                    data = {
                        "symbol": symbol,
                        "timestamp": datetime.now(),
                        "last_price": self.prices[symbol],
                        "volume": random.randint(10000, 100000),
                        "bid": self.prices[symbol] - 0.5,
                        "ask": self.prices[symbol] + 0.5
                    }
                    
                    if self.callback:
                        await self._dispatch(symbol, data)
            
            await asyncio.sleep(2)  # 2 second ticks


class LiveDataManager:
    """Manages live data for trading"""
    
    def __init__(self):
        self.feed: Optional[DataFeed] = None
        self.data_buffer: Dict[str, List[Dict]] = {}
    
    def start_live(self, symbols: List[str], feed_type: str = "mock", **kwargs):
        """Start live data feed"""
        
        if feed_type == "mock":
            base_prices = kwargs.get("base_prices", {
                "RELIANCE": 2500, "TCS": 3200, "INFY": 1400
            })
            self.feed = MockLiveFeed(symbols, base_prices)
        elif feed_type == "websocket":
            self.feed = WebSocketFeed(symbols, provider=kwargs.get("provider", "angel_one"))
        elif feed_type == "polling":
            self.feed = PollingFeed(symbols, api_client=kwargs.get("api_client"))
        
        return self.feed
    
    def set_tick_handler(self, handler: Callable):
        """Set tick handler"""
        if self.feed:
            self.feed.set_callback(handler)
    
    async def run(self):
        """Run the feed"""
        if self.feed:
            await self.feed.start()
            
            # Keep running
            while self.feed.running:
                await asyncio.sleep(1)


# Demo usage
async def demo():
    """Demo live data"""
    logger.info("=" * 60)
    logger.info("LIVE DATA FEED DEMO")
    logger.info("=" * 60)
    
    manager = LiveDataManager()
    
    # Use mock feed for demo
    feed = manager.start_live(
        ["RELIANCE", "TCS", "INFY"],
        feed_type="mock",
        base_prices={"RELIANCE": 2500, "TCS": 3200, "INFY": 1400}
    )
    
    # Set handler
    async def on_tick(symbol: str, data: Dict):
        logger.info(f"  {symbol}: ₹{data['last_price']} (vol: {data['volume']})")
    
    manager.set_tick_handler(on_tick)
    
    # Run for 10 seconds
    feed_task = asyncio.create_task(manager.run())
    await asyncio.sleep(10)
    feed_task.cancel()
    
    logger.info("Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())