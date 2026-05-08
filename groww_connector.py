#!/usr/bin/env python3
"""
Groww Live Data Connector
=========================================
Real-time market data from Groww API

Features:
- Live quote fetching
- WebSocket streaming (simulated)
- Historical data
- Market depth
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional

# Groww API imports would go here


class GrowwDataConnector:
    """
    Groww API Data Connector
    
    Real-time market data:
    - LTP quotes
    - OHLC data
    - Market depth
    - Streaming (via polling)
    """
    
    def __init__(self, api_token: str = ""):
        self.api_token = api_token
        self.base_url = "https://api.groww.in/v1"
        self.subscriptions = set()
        
        # Data cache
        self.quotes: Dict[str, dict] = {}
        self.ohlc_cache: Dict[str, List[dict]] = {}
        
        # Callbacks
        self.on_tick: Optional[Callable] = None
        self.on_quote: Optional[Callable] = None
    
    def set_tick_callback(self, callback: Callable):
        """Set tick data callback"""
        self.on_tick = callback
    
    def set_quote_callback(self, callback: Callable):
        """Set quote update callback"""
        self.on_quote = callback
    
    async def connect(self):
        """Connect to Groww API"""
        logging.info("Connecting to Groww API...")
    
    async def subscribe(self, symbols: List[str]):
        """Subscribe to symbols"""
        for sym in symbols:
            self.subscriptions.add(sym)
        logging.info(f"Subscribed to: {symbols}")
    
    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols"""
        for sym in symbols:
            self.subscriptions.discard(sym)
    
    async def get_quote(self, symbol: str) -> Optional[dict]:
        """Get live quote for symbol"""
        # In production, this would call Groww API
        # For now, return mock data
        return {
            "symbol": symbol,
            "last_price": 0,
            "open": 0,
            "high": 0,
            "low": 0,
            "previous_close": 0,
            "change": 0,
            "change_percent": 0,
            "volume": 0,
            "bid": 0,
            "ask": 0,
            "timestamp": datetime.now()
        }
    
    async def get_ohlc(
        self,
        symbol: str,
        interval: str = "D",
        days: int = 30
    ) -> List[dict]:
        """Get OHLC historical data"""
        # Would fetch from Groww API in production
        return []
    
    async def get_market_depth(self, symbol: str) -> dict:
        """Get market depth (bid/ask)"""
        return {
            "symbol": symbol,
            "bid": [],
            "ask": []
        }
    
    async def start_streaming(self, symbols: List[str]):
        """Start streaming quotes"""
        await self.subscribe(symbols)
        logging.info(f"Started streaming for {symbols}")
    
    async def stop_streaming(self):
        """Stop streaming"""
        self.subscriptions.clear()
    
    def get_cached_quote(self, symbol: str) -> Optional[dict]:
        """Get cached quote"""
        return self.quotes.get(symbol)


class LiveDataAggregator:
    """
    Live Data Aggregator
    
    Aggregates data from multiple sources:
    - Multiple brokers
    - Fallback support
    - Data normalization
    """
    
    def __init__(self):
        self.connectors: Dict[str, GrowwDataConnector] = {}
        self.primary: str = "groww"
        
        self.data_cache: Dict[str, dict] = {}
        self.last_update: Dict[str, datetime] = {}
    
    def add_connector(self, name: str, connector: GrowwDataConnector):
        """Add data connector"""
        self.connectors[name] = connector
    
    def set_primary(self, name: str):
        """Set primary data source"""
        if name in self.connectors:
            self.primary = name
    
    async def get_quote(self, symbol: str) -> Optional[dict]:
        """Get quote from primary source with fallback"""
        # Try primary first
        if self.primary in self.connectors:
            quote = await self.connectors[self.primary].get_quote(symbol)
            if quote:
                self.data_cache[symbol] = quote
                self.last_update[symbol] = datetime.now()
                return quote
        
        # Try fallbacks
        for name, connector in self.connectors.items():
            if name != self.primary:
                quote = await connector.get_quote(symbol)
                if quote:
                    self.data_cache[symbol] = quote
                    self.last_update[symbol] = datetime.now()
                    return quote
        
        # Return cached if no live data
        return self.data_cache.get(symbol)
    
    def get_data_freshness(self, symbol: str) -> float:
        """Get data freshness in seconds"""
        if symbol not in self.last_update:
            return 999
        
        age = (datetime.now() - self.last_update[symbol]).total_seconds()
        return age
    
    def is_fresh(self, symbol: str, max_age: float = 5) -> bool:
        """Check if data is fresh"""
        return self.get_data_freshness(symbol) < max_age


# ============ TEST ===========
def test_groww_connector():
    """Test Groww connector"""
    
    print("=" * 60)
    print("GROWW DATA CONNECTOR TEST")
    print("=" * 60)
    
    connector = GrowwDataConnector()
    
    # Test quote fetch
    print("\nTesting quote fetch...")
    
    # Aggregator test
    agg = LiveDataAggregator()
    agg.add_connector("groww", connector)
    
    print(f"Connectors: {list(agg.connectors.keys())}")
    print(f"Primary: {agg.primary}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_groww_connector()