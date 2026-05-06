#!/usr/bin/env python3
"""
Stock Universe Configuration

Defines tradable symbols for different strategies:
- Nifty 50 stocks
- BankNifty component stocks
- F&O indices
- Stock options

Usage:
    from stocks import get_symbols, WATCHLISTS
    
    equity_stocks = get_symbols("momentum")
    bank_stocks = get_symbols("banking")
    all_stocks = get_symbols("all")
"""

# Trading symbols with exchange and segment info
TRADING_SYMBOLS = {
    # Nifty 50 Stocks
    "RELIANCE": {"exchange": "NSE", "segment": "EQUITY"},
    "TCS": {"exchange": "NSE", "segment": "EQUITY"},
    "INFY": {"exchange": "NSE", "segment": "EQUITY"},
    "HDFCBANK": {"exchange": "NSE", "segment": "EQUITY"},
    "SBIN": {"exchange": "NSE", "segment": "EQUITY"},
    "BHARTIARTL": {"exchange": "NSE", "segment": "EQUITY"},
    "HINDUNILVR": {"exchange": "NSE", "segment": "EQUITY"},
    "ICICIBANK": {"exchange": "NSE", "segment": "EQUITY"},
    "KOTAKBANK": {"exchange": "NSE", "segment": "EQUITY"},
    "AXISBANK": {"exchange": "NSE", "segment": "EQUITY"},
    "LT": {"exchange": "NSE", "segment": "EQUITY"},
    "M&M": {"exchange": "NSE", "segment": "EQUITY"},
    "TITAN": {"exchange": "NSE", "segment": "EQUITY"},
    "ADANIPORTS": {"exchange": "NSE", "segment": "EQUITY"},
    "SUNPHARMA": {"exchange": "NSE", "segment": "EQUITY"},
    
    # Banknifty Component Stocks (Top Banks)
    "HDFCBANK": {"exchange": "NSE", "segment": "EQUITY"},
    "ICICIBANK": {"exchange": "NSE", "segment": "EQUITY"},
    "KOTAKBANK": {"exchange": "NSE", "segment": "EQUITY"},
    "AXISBANK": {"exchange": "NSE", "segment": "EQUITY"},
    "SBIN": {"exchange": "NSE", "segment": "EQUITY"},
    "INDUSINDBK": {"exchange": "NSE", "segment": "EQUITY"},
    "BANDHANBNK": {"exchange": "NSE", "segment": "EQUITY"},
    "FEDERALBNK": {"exchange": "NSE", "segment": "EQUITY"},
    "IDFCFIRSTB": {"exchange": "NSE", "segment": "EQUITY"},
    
    # F&O Index Futures
    "NIFTY": {"exchange": "NSE", "segment": "INDEX_FUT"},
    "BANKNIFTY": {"exchange": "NSE", "segment": "INDEX_FUT"},
    "FINNIFTY": {"exchange": "NSE", "segment": "INDEX_FUT"},
    "MIDCPNIFTY": {"exchange": "NSE", "segment": "INDEX_FUT"},
}

# Popular Stock Options (CE/PE)
STOCK_OPTIONS = {
    # Banknifty Options (WeeklyExpiry)
    "BANKNIFTY": {"expiry": "WEEKLY", "strike_range": 1000},
    
    # Nifty Options
    "NIFTY": {"expiry": "WEEKLY", "strike_range": 100},
    
    # Popular Stock Options
    "RELIANCE": {"expiry": "MONTHLY", "strike_range": 50},
    "TCS": {"expiry": "MONTHLY", "strike_range": 100},
    "INFY": {"expiry": "MONTHLY", "strike_range": 50},
    "HDFCBANK": {"expiry": "MONTHLY", "strike_range": 50},
    "SBIN": {"expiry": "MONTHLY", "strike_range": 50},
    "BHARTIARTL": {"expiry": "MONTHLY", "strike_range": 100},
}


# Default watchlist for different strategies
WATCHLISTS = {
    "momentum": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN"],
    "banking": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "AXISBANK", "SBIN"],
    "intraday": ["RELIANCE", "TCS", "INFY", "NIFTY", "BANKNIFTY"],
    "options": ["NIFTY", "BANKNIFTY"],
    "all": list(TRADING_SYMBOLS.keys())[:15]
}


def get_symbols(watchlist: str = "momentum") -> list:
    """Get symbols for a watchlist"""
    return WATCHLISTS.get(watchlist, WATCHLISTS["momentum"])


def is_options_eligible(symbol: str) -> bool:
    """Check if symbol has options"""
    return symbol in STOCK_OPTIONS


def get_expiry_type(symbol: str) -> str:
    """Get expiry type for symbol"""
    if symbol in STOCK_OPTIONS:
        return STOCK_OPTIONS[symbol].get("expiry", "MONTHLY")
    return "MONTHLY"