#!/usr/bin/env python3
"""
Alert System

Real-time notification system for trading events:
- Signal alerts
- Trade execution alerts
- Stop-loss / Target alerts
- System notifications

Supports multiple handlers (console, email, telegram)
"""

import time
from datetime import datetime
from enum import Enum
from typing import Callable, List


class AlertType(Enum):
    SIGNAL = "SIGNAL"
    TRADE = "TRADE"
    STOP_LOSS = "STOP_LOSS"
    TARGET = "TARGET"
    SYSTEM = "SYSTEM"


class AlertPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Alert:
    def __init__(self, alert_type: AlertType, symbol: str, message: str, priority: AlertPriority = AlertPriority.MEDIUM):
        self.alert_type = alert_type
        self.symbol = symbol
        self.message = message
        self.priority = priority
        self.timestamp = datetime.now()
    
    def to_dict(self):
        return {
            "type": self.alert_type.value,
            "symbol": self.symbol,
            "message": self.message,
            "priority": self.priority.value,
            "timestamp": self.timestamp.strftime("%H:%M:%S")
        }


class AlertManager:
    """Alert notification manager"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        """Add notification handler"""
        self.handlers.append(handler)
    
    def send(self, alert: Alert):
        """Send alert to all handlers"""
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Notify all handlers
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")
    
    # Convenience methods
    def signal(self, symbol: str, direction: str, confidence: int):
        """New trading signal"""
        msg = f"📊 {direction} signal on {symbol} | Conf: {confidence}%"
        alert = Alert(AlertType.SIGNAL, symbol, msg, AlertPriority.HIGH if confidence > 85 else AlertPriority.MEDIUM)
        self.send(alert)
    
    def trade(self, symbol: str, direction: str, price: float, pnl: float = 0):
        """Trade executed"""
        pnl_str = f" | P&L: ₹{pnl:+.0f}" if pnl else ""
        msg = f"💰 {direction} {symbol} @ ₹{price}{pnl_str}"
        priority = AlertPriority.HIGH if pnl > 0 else AlertPriority.MEDIUM
        alert = Alert(AlertType.TRADE, symbol, msg, priority)
        self.send(alert)
    
    def stop_loss(self, symbol: str, price: float):
        """Stop loss hit"""
        msg = f"🛑 SL hit on {symbol} @ ₹{price}"
        alert = Alert(AlertType.STOP_LOSS, symbol, msg, AlertPriority.CRITICAL)
        self.send(alert)
    
    def target(self, symbol: str, price: float):
        """Target reached"""
        msg = f"🎯 Target hit on {symbol} @ ₹{price}"
        alert = Alert(AlertType.TARGET, symbol, msg, AlertPriority.HIGH)
        self.send(alert)
    
    def system(self, message: str):
        """System alert"""
        msg = f"⚙️ {message}"
        alert = Alert(AlertType.SYSTEM, "SYSTEM", msg, AlertPriority.MEDIUM)
        self.send(alert)
    
    def get_recent(self, count: int = 10) -> List[Alert]:
        """Get recent alerts"""
        return self.alerts[-count:]


# Console handler
def console_alert_handler(alert: Alert):
    """Print alerts to console"""
    prefix = ""
    if alert.priority == AlertPriority.CRITICAL:
        prefix = "🚨"
    elif alert.priority == AlertPriority.HIGH:
        prefix = "⚡"
    elif alert.alert_type == AlertType.TRADE:
        prefix = "💰"
    elif alert.alert_type == AlertType.SIGNAL:
        prefix = "📊"
    else:
        prefix = "ℹ️"
    
    print(f"{prefix} [{alert.timestamp.strftime('%H:%M:%S')}] {alert.message}")


# Global alert manager
alert_manager = AlertManager()
alert_manager.add_handler(console_alert_handler)


# Test
if __name__ == "__main__":
    print("Testing Alert System...")
    
    alert_manager.signal("RELIANCE", "LONG", 85)
    alert_manager.trade("TCS", "BUY", 3200, 150)
    alert_manager.stop_loss("INFY", 1350)
    alert_manager.target("HDFCBANK", 820)
    alert_manager.system("Trading bot started")
    
    print("\nRecent alerts:")
    for a in alert_manager.get_recent():
        print(f"  {a.message}")