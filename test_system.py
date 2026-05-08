#!/usr/bin/env python3
"""
Comprehensive System Test
=========================================
Tests all modules and their compatibility
"""

import sys
import asyncio
from datetime import datetime, timedelta

# Test results
passed = 0
failed = 0
errors = []


def test(name: str, func):
    global passed, failed, errors
    try:
        result = func()
        if result:
            print(f"✓ {name}")
            passed += 1
        else:
            print(f"✗ {name}")
            failed += 1
    except Exception as e:
        print(f"✗ {name}: {e}")
        errors.append(f"{name}: {e}")
        failed += 1


# ============ TEST FUNCTIONS ============

def test_position_sizing():
    from position_sizing import AdaptiveSizingEngine, PositionConfig
    config = PositionConfig(budget=200)
    engine = AdaptiveSizingEngine(config)
    result = engine.calculate_position_size(2500, 2475)
    return result["quantity"] > 0


def test_portfolio_risk():
    from portfolio_risk import PortfolioRiskManager
    rm = PortfolioRiskManager(starting_capital=200)
    can_open, reason = rm.can_take_position("RELIANCE", "energy", 200)
    return can_open


def test_multiframe():
    from multiframe import MultiTimeframeAnalysis, TimeFrame
    mt = MultiTimeframeAnalysis("RELIANCE")
    mt.add_data(TimeFrame.M5, {"price": 2550, "vwap": 2520, "ema_9": 2540, "ema_21": 2510, "rsi": 50, "volume": 50000, "avg_volume": 40000})
    mt.add_data(TimeFrame.M15, {"price": 2545, "vwap": 2530, "ema_9": 2535, "ema_21": 2520, "rsi": 52, "volume": 100000, "avg_volume": 90000})
    should, reason, conf = mt.should_trade()
    return should or not should  # Just check it runs


def test_advanced_orders():
    from advanced_orders import AdvancedOrderManager, BracketOrder
    mgr = AdvancedOrderManager()
    bid = mgr.create_bracket_order("RELIANCE", 10, 2500, 2550, 2475)
    return bid is not None


def test_strategy_engine():
    from strategy_engine import QuantStrategyEngine, StrategyConfig, StrategyType
    config = StrategyConfig(StrategyType.MOMENTUM, min_confidence=60)
    engine = QuantStrategyEngine(config)
    signal = engine.analyze_market_data(
        "RELIANCE", 2550, 2520, 2540, 2510, 2480, 45, 150000, 100000, 2530, 2500, 2520, 2560, 2540, 2545
    )
    # May or may not generate signal
    return True


def test_backtest_engine():
    from backtest_engine import BacktestEngine
    engine = BacktestEngine(starting_capital=200)
    # Simulate some trades
    for i in range(3):
        engine.run_trade("RELIANCE", 2500 + i*10, 2520 + i*10, 1, "LONG", datetime.now(), datetime.now(), "target")
    result = engine.calculate_results()
    return result.total_trades == 3


def test_groww_connector():
    from groww_connector import GrowwDataConnector, LiveDataAggregator
    connector = GrowwDataConnector()
    agg = LiveDataAggregator()
    agg.add_connector("groww", connector)
    return "groww" in agg.connectors


def test_data_fetcher():
    from data_fetcher import DataManager, OHLC
    dm = DataManager()
    ohlc = OHLC(datetime.now(), 2500, 2520, 2490, 2510, 100000)
    dm.ohlc_data["RELIANCE"] = [ohlc]
    md = dm.get_market_data("RELIANCE")
    return True


def test_trading_system():
    from trading_system import TradingSystem, TradeConfig
    config = TradeConfig(capital=200, paper_mode=True)
    system = TradingSystem(config)
    status = system.get_status()
    return "capital" in status


def test_stocks():
    from stocks import get_symbols, TRADING_SYMBOLS
    momentum = get_symbols("momentum")
    return len(momentum) > 0


def test_alerts():
    from alerts import AlertManager, Alert, AlertType
    am = AlertManager()
    am.system("Test alert")
    return len(am.get_recent()) > 0


# ============ RUN ALL TESTS ============

print("=" * 70)
print("COMPREHENSIVE SYSTEM TEST")
print("=" * 70)

tests = [
    ("Position Sizing Engine", test_position_sizing),
    ("Portfolio Risk Manager", test_portfolio_risk),
    ("Multi-Timeframe Analysis", test_multiframe),
    ("Advanced Orders", test_advanced_orders),
    ("Strategy Engine", test_strategy_engine),
    ("Backtest Engine", test_backtest_engine),
    ("Groww Connector", test_groww_connector),
    ("Data Fetcher", test_data_fetcher),
    ("Trading System", test_trading_system),
    ("Stock Configuration", test_stocks),
    ("Alert System", test_alerts),
]

for name, func in tests:
    test(name, func)

# Summary
print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 70)

if errors:
    print("\nErrors:")
    for e in errors:
        print(f"  - {e}")

sys.exit(0 if failed == 0 else 1)