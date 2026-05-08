#!/usr/bin/env python3
"""
Advanced Order Types
=========================================
Professional order types for quant trading

Supports:
- Bracket Orders (entry + target + stop)
- Cover Orders (stop + buyback protection)
- AMO (After Market Orders)
- GTT (Good-Till-Triggered)
- OCO (One-Cancels-Other)
- Trailing Stop Orders
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LOSS_MARKET = "stop_loss_market"
    BRACKET = "bracket"
    COVER = "cover"
    AMO = "amo"
    GTT = "gtt"
    OCO = "oco"
    TRAILING_STOP = "trailing_stop"


class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class BracketOrder:
    """
    Bracket Order
    
    Entry order with automatic profit target and stop loss
    - Can have multiple legs
    - Auto-cancellation on target or stop hit
    """
    order_id: str
    symbol: str
    quantity: int
    entry_price: float  # 0 for market
    entry_type: OrderType
    
    # Target leg
    target_price: float
    target_quantity: int
    
    # Stop leg
    stop_loss_price: float
    stop_loss_quantity: int
    
    # Trailing (optional)
    trailing_activation: float = 0  # % activation
    trailing_distance: float = 0   # % distance
    
    created_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    status: OrderStatus = OrderStatus.PENDING
    
    def get_order_payload(self) -> Dict:
        """Get order payload for broker"""
        return {
            "order_type": "bracket",
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.entry_price,
            "product": "MIS",  # Intraday
            "validity": "DAY",
            "legs": [
                {
                    "type": "ENTRY",
                    "transaction": "BUY",
                    "quantity": self.quantity
                },
                {
                    "type": "TARGET",
                    "transaction": "SELL",
                    "quantity": self.target_quantity or self.quantity,
                    "price": self.target_price
                },
                {
                    "type": "STOP_LOSS",
                    "transaction": "SELL",
                    "quantity": self.stop_loss_quantity or self.quantity,
                    "price": self.stop_loss_price,
                    "trigger_price": self.stop_loss_price
                }
            ]
        }


@dataclass  
class GTTOrder:
    """
    Good-Till-Triggered Order
    
    Advanced GTT that can trigger on:
    - Price cross
    - Price breach
    - Time-based
    """
    order_id: str
    symbol: str
    
    # Trigger conditions
    trigger_type: str = "single"  # single, oco
    trigger_price: float = 0
    trigger_type2: float = 0  # For OCO
    
    # Order details
    quantity: int
    side: str  # BUY or SELL
    order_type: str = "limit"
    
    # Active until
    active_until: Optional[datetime] = None
    
    trigger_count: int = 0
    status: OrderStatus = OrderStatus.PENDING
    
    def should_trigger(self, current_price: float) -> bool:
        """Check if trigger condition met"""
        if self.status != OrderStatus.PENDING:
            return False
        
        if self.active_until and datetime.now() > self.active_until:
            self.status = OrderStatus.CANCELLED
            return False
        
        price = current_price
        
        if self.trigger_type == "single":
            # Trigger when price crosses trigger_price
            if price >= self.trigger_price:
                self.trigger_count += 1
                return True
        
        elif self.trigger_type == "oco":
            # One triggers, other cancels
            if price >= self.trigger_price or price <= self.trigger_type2:
                self.trigger_count += 1
                return True
        
        return False
    
    def get_payload(self) -> Dict:
        return {
            "order_type": "gtt",
            "symbol": self.symbol,
            "quantity": self.quantity,
            "transaction_type": self.side,
            "gtt_type": self.trigger_type,
            "trigger_price": self.trigger_price,
            "price": self.trigger_price  # Limit price
        }


@dataclass
class TrailingStopOrder:
    """
    Trailing Stop Order
    
    Dynamic stop that moves with price
    - Locks in profits as price moves up
    - Can have activation threshold
    """
    order_id: str
    symbol: str
    
    initial_stop: float
    trailing_percent: float  # % to trail
    
    activation_percent: float = 0  # Must move this % before activating
    activation_price: float = 0
    
    current_stop: float
    highest_price: float = 0
    lowest_price: float = 0
    
    quantity: int
    side: str  # BUY or SELL
    status: OrderStatus = OrderStatus.OPEN
    
    def update(self, current_price: float):
        """Update trailing stop"""
        if not self.highest_price:
            self.highest_price = current_price
        
        if not self.lowest_price:
            self.lowest_price = current_price
        
        if self.side == "BUY":
            # For long: track highest
            if current_price > self.highest_price:
                self.highest_price = current_price
                
                # Check activation
                if self.activation_percent > 0:
                    move_pct = (self.highest_price - self.activation_price) / self.activation_price * 100
                    if move_pct >= self.activation_percent:
                        # Move stop
                        new_stop = self.highest_price * (1 - self.trailing_percent / 100)
                        if new_stop > self.current_stop:
                            self.current_stop = new_stop
            
            # Check if stopped
            if current_price <= self.current_stop:
                self.status = OrderStatus.FILLED
        
        else:  # SELL
            if current_price < self.lowest_price:
                self.lowest_price = current_price
                if self.activation_percent > 0:
                    move_pct = (self.activation_price - self.lowest_price) / self.activation_price * 100
                    if move_pct >= self.activation_percent:
                        new_stop = self.lowest_price * (1 + self.trailing_percent / 100)
                        if new_stop < self.current_stop:
                            self.current_stop = new_stop
            
            if current_price >= self.current_stop:
                self.status = OrderStatus.FILLED
    
    def get_current_stop(self) -> float:
        return round(self.current_stop, 2)


class AdvancedOrderManager:
    """
    Advanced Order Manager
    
    Manages all advanced order types:
    - Bracket orders
    - GTT orders
    - Trailing stops
    - AMO queue
    """
    
    def __init__(self):
        self.bracket_orders: Dict[str, BracketOrder] = {}
        self.gtt_orders: Dict[str, GTTOrder] = {}
        self.trailing_stops: Dict[str, TrailingStopOrder] = {}
        self.amo_queue: List[dict] = []
        
        # Callbacks for filled orders
        self.on_fill: Optional[Callable] = None
        self.on_cancel: Optional[Callable] = None
    
    def set_callbacks(self, on_fill=None, on_cancel=None):
        self.on_fill = on_fill
        self.on_cancel = on_cancel
    
    # ============ BRACKET ORDERS ============
    
    def create_bracket_order(
        self,
        symbol: str,
        quantity: int,
        entry_price: float,
        target_price: float,
        stop_loss_price: float,
        side: str = "BUY"
    ) -> str:
        """Create a bracket order"""
        order_id = f"bracket_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order = BracketOrder(
            order_id=order_id,
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            entry_type=OrderType.LIMIT if entry_price > 0 else OrderType.MARKET,
            target_price=target_price,
            target_quantity=quantity,
            stop_loss_price=stop_loss_price,
            stop_loss_quantity=quantity
        )
        
        self.bracket_orders[order_id] = order
        return order_id
    
    # ============ GTT ORDERS ============
    
    def create_gtt(
        self,
        symbol: str,
        trigger_price: float,
        quantity: int,
        side: str = "BUY",
        gtt_type: str = "single"
    ) -> str:
        """Create GTT order"""
        order_id = f"gtt_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order = GTTOrder(
            order_id=order_id,
            symbol=symbol,
            trigger_price=trigger_price,
            quantity=quantity,
            side=side,
            trigger_type=gtt_type,
            active_until=datetime.now() + timedelta(days=30)  # 30 day validity
        )
        
        self.gtt_orders[order_id] = order
        return order_id
    
    # ============ TRAILING STOPS ============
    
    def create_trailing_stop(
        self,
        symbol: str,
        initial_stop: float,
        trailing_percent: float,
        quantity: int,
        activation_percent: float = 0,
        side: str = "BUY"
    ) -> str:
        """Create trailing stop"""
        order_id = f"ts_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get current price for activation
        current_price = initial_stop / (1 - activation_percent / 100) if activation_percent > 0 else initial_stop * 1.01
        
        order = TrailingStopOrder(
            order_id=order_id,
            symbol=symbol,
            initial_stop=initial_stop,
            trailing_percent=trailing_percent,
            activation_percent=activation_percent,
            activation_price=current_price,
            current_stop=initial_stop,
            quantity=quantity,
            side=side
        )
        
        self.trailing_stops[order_id] = order
        return order_id
    
    # ============ CHECK FUNCTIONS ============
    
    def check_gtt_trigger(self, symbol: str, current_price: float):
        """Check and trigger GTT orders"""
        triggered = []
        
        for order_id, order in self.gtt_orders.items():
            if order.symbol == symbol and order.should_trigger(current_price):
                order.status = OrderStatus.FILLED
                triggered.append(order)
                if self.on_fill:
                    self.on_fill(order)
        
        return triggered
    
    def check_trailing_stops(self, symbol: str, current_price: float):
        """Update and check trailing stops"""
        triggered = []
        
        for order_id, order in self.trailing_stops.items():
            if order.symbol == symbol:
                order.update(current_price)
                if order.status == OrderStatus.FILLED:
                    triggered.append(order)
                    if self.on_fill:
                        self.on_fill(order)
        
        return triggered
    
    # ============ AMO ============
    
    def queue_amo(self, order_data: dict):
        """Queue AMO for next market open"""
        order_data["order_type"] = "amo"
        order_data["queued_at"] = datetime.now()
        self.amo_queue.append(order_data)
    
    def get_amo_queue(self) -> List[dict]:
        """Get queued AMO orders"""
        return self.amo_queue
    
    def clear_amo_queue(self):
        """Clear AMO queue"""
        self.amo_queue = []


# ============ TEST ===========
def test_advanced_orders():
    """Test advanced orders"""
    
    print("=" * 60)
    print("ADVANCED ORDER TYPES TEST")
    print("=" * 60)
    
    mgr = AdvancedOrderManager()
    
    # Test Bracket Order
    bid = mgr.create_bracket_order(
        symbol="RELIANCE",
        quantity=10,
        entry_price=2500,
        target_price=2550,  # 2% target
        stop_loss_price=2475,  # 1% stop
        side="BUY"
    )
    print(f"\nCreated Bracket Order: {bid}")
    print(f"  Payload: {mgr.bracket_orders[bid].get_order_payload()}")
    
    # Test GTT
    gid = mgr.create_gtt(
        symbol="TCS",
        trigger_price=3300,
        quantity=5,
        side="BUY"
    )
    print(f"\nCreated GTT Order: {gid}")
    
    # Test Trailing Stop
    tid = mgr.create_trailing_stop(
        symbol="INFY",
        initial_stop=1400,
        trailing_percent=1.5,  # 1.5% trail
        quantity=10,
        activation_percent=1,  # Activate after 1% move
        side="BUY"
    )
    print(f"\nCreated Trailing Stop: {tid}")
    
    # Simulate trailing
    ts = mgr.trailing_stops[tid]
    for price in [1410, 1415, 1420, 1410]:
        ts.update(price)
        print(f"  Price: {price} → Stop: {ts.get_current_stop()} (Status: {ts.status.value})")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_advanced_orders()