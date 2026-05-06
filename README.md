# Algorithmic Trading System

A disciplined, risk-managed algorithmic trading system for Indian stock markets.

## Features

- **Technical Analysis**: VWAP, EMA (9/21), RSI indicators
- **Risk Management**: Position sizing, stop-loss, risk-reward
- **Multiple Strategies**: Momentum, banking, intraday, options
- **Real-time Dashboard**: Web UI with live charts
- **Broker Integration**: Angel One SmartAPI ready

## Quick Start

```bash
# Install dependencies
pip install flask flask-socketio yfinance

# Run backtest
python3 historical_backtest.py

# Run dashboard
python3 dashboard.py
```

## Project Structure

```
.
├── trading_system.py    # Core strategy engine
├── data_fetcher.py   # Market data & indicators
├── stocks.py        # Stock universe
├── alerts.py       # Notifications
├── broker_angelone.py  # Angel One API
├── dashboard.py    # Web dashboard
└── templates/
    └── index.html # UI
```

## Supported Brokers

- Angel One SmartAPI (recommended - free)
- Zerodha Kite (documentation provided)
- Groww Trade API (paid subscription)

## License

MIT

## Disclaimer

This is for educational purposes. Trade at your own risk.