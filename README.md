<!--

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                                  ║
║    ██████╗   ██████╗  █████╗ ███╗   ██╗███████╗ ██████╗ ███╗   ███╗      ██████╗  ██╗  ██╗ █████╗ ██████╗ ██████╗                  ║
║   ██╔════╝  ██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔═══██╗████╗ ████║     ██╔══██╗ ██║  ██║██╔══██╗██╔══██╗██╔══██╗                 ║
║   ██║       ██████╔╝███████║██╔██╗ ██║█████╗  ██║   ██║██╔████╔██║     ██████╔╝ ███████║███████║██████╔╝██║  ██║                 ║
║   ██║       ██╔══██╗██╔══██║██║╚██╗██║██╔══╝  ██║   ██║██║╚██╔╝██║     ██╔═══╝  ██╔══██║██╔══██║██╔══██╗██║  ██║                 ║
║   ╚██████╗  ██║  ██║██║  ██║██║ ╚████║███████╗╚██████╔╝██║ ╚═╝ ██║     ██║      ██║  ██║██║  ██║██║  ██║██████╔╝                 ║
║    ╚═════╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝      ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝                  ║
║                                                                                                                                  ║
║                                    ███████╗ ██████╗ ██████╗ ███████╗ ██████╗  ██████╗ ███████╗████████╗                                          ║
║                                    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔═══██╗██╔════╝ ██╔════╝╚══██╔══╝                                          ║
║                                    █████╗  ██║   ██║██████╔╝█████╗  ██║   ██║██║  ███╗█████╗    ███████╗  █████╗ ██████╗  █████╗ ██████╗ ██████╗  ║
║                                    ██╔══╝  ██║   ██║██╔══██╗██╔══╝  ██║   ██║██║   ██║██╔══╝    ╚════██║ ██╔══██╗██╔══██╗██╔══██╗██╔══██╗ ██╔══╝   ║
║                                    ███████╗╚██████╔╝██║  ██║███████╗╚██████╔╝╚██████╔╝███████╗   ███████║ ███████║██████╔╝███████║██████╔╝ ███████╗
║                                    ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝   ╚══════╝ ╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝   ╚══════╝
║                                                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

-->

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Platform-Linux-lightgrey?style=for-the-badge&logo=linux" alt="Platform">
</p>

<p align="center">
  <a href="https://github.com/The-Peacemaker/Algo-Trade">
    <img src="https://img.shields.io/github/stars/The-Peacemaker/Algo-Trade?style=social" alt="Stars">
  </a>
  <a href="https://github.com/The-Peacemaker/Algo-Trade">
    <img src="https://img.shields.io/github/forks/The-Peacemaker/Algo-Trade?style=social" alt="Forks">
  </a>
  <a href="https://github.com/The-Peacemaker/Algo-Trade">
    <img src="https://img.shields.io/github/watchers/The-Peacemaker/Algo-Trade?style=social" alt="Watchers">
  </a>
</p>

---

# ⚡ QuantFlow — Institutional-Grade Algorithmic Trading System

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=The-Peacemaker&repo=Algo-Trade&style=flat-square&label=Profile+Views&color=00ff88&style=for-the-badge" alt="Profile Views">
</p>

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Architecture](#-architecture)
3. [Features](#-features)
4. [System Design](#-system-design)
5. [Quick Start](#-quick-start)
6. [Configuration](#-configuration)
7. [Strategy Details](#-strategy-details)
8. [Risk Management](#-risk-management)
9. [API Integration](#-api-integration)
10. [Testing](#-testing)
11. [Performance](#-performance)
12. [Roadmap](#-roadmap)
13. [Contributing](#-contributing)
14. [License](#-license)

---

## 📊 Overview

**QuantFlow** is an institutional-grade algorithmic trading system designed for the Indian stock markets. Built with a focus on **risk management**, **capital preservation**, and **quantitative rigor**, it implements professional trading strategies used by quant funds worldwide.

### 🎯 Key Principles

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                            │
│   ₁. CAPITAL PRESERVATION  →  Never risk more than 2% per trade                          │
│   ₂. DISCIPLINED EXECUTION →  Rules-based, emotionless trading                          │
│   ₃. QUANTITATIVE RIGOR  →  Data-driven decisions, not speculation                      │
│   ₄. RISK-ADAPTIVE       →  Dynamic position sizing based on account performance       │
│   ₅. MULTI-TIMEFRAME     →  Higher timeframe confirmation for entries                    │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 💰 Supported Budget Ranges

| Budget Range | Risk Profile | Max Positions | Target Returns |
|-------------|--------------|--------------|----------------|
| ₹100 - ₹500 | UltraSafe    | 1            | 1-2%/day      |
| ₹500 - ₹5,000 | Conservative | 2            | 1-1.5%/day    |
| ₹5,000 - ₹50,000 | Moderate    | 3            | 0.8-1%/day   |
| ₹50,000+ | Aggressive  | 5            | 0.5-0.8%/day |

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                    QUANTFLOW ARCHITECTURE                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐          │
│  │   BROKER    │     │    DATA     │     │   STRATEGY  │     │    RISK     │     │   ORDER     │          │
│  │   LAYER     │────▶│   LAYER     │────▶│   ENGINE     │────▶│   MANAGER    │────▶│   EXECUTION │          │
│  │              │     │              │     │              │     │              │     │              │          │
│  │ • Angel One │     │ • Real-time  │     │ • Multi-Signal│     │ • Position   │     │ • Bracket   │          │
│  │ • Groww     │     │ • Historical │     │ • VWAP       │     │ • Portfolio  │     │ • GTT       │          │
│  │ • WebSocket │     │ • Indicators │     │ • EMA Cross  │     │ • Drawdown   │     │ • Trailing  │          │
│  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘          │
│          │                    │                    │                    │                    │                    │
│          └────────────────────┴────────────────────┴────────────────────┴────────────────────┘                    │
│                                                    │                                                                     │
│                                                    ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                                              DASHBOARD                                                   │   │
│  │   • Real-time P&L    • Equity Curve    • Trade Log    • Signal Monitor    • Risk Metrics          │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
                                    ┌─────────────────────────┐
                                    │    MARKET DATA FEED    │
                                    │  (Broker WebSocket)    │
                                    └───────────┬─────────────┘
                                                │
                    ┌───────────────────────────┬───┴───────────────────────────┐
                    │                           │                               │
                    ▼                           ▼                               ▼
           ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
           │   DATA MANAGER  │     │   DATA MANAGER  │     │   DATA MANAGER  │
           │                 │     │                 │     │                 │
           │ • 1-minute      │     │ • 5-minute      │     │ • 15-minute     │
           │ • Price Cache   │     │ • VWAP Calc     │     │ • EMA Calc       │
           │ • Volume Track │     │ • RSI Calc      │     │ • Trend Detect   │
           └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
                    │                      │                      │
                    └──────────────────────┼──────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────────┐
                              │   STRATEGY ENGINE      │
                              │                        │
                              │  1. Signal Detection  │
                              │  2. Confidence Calc   │
                              │  3. Strategy Filter  │
                              └───────────┬─────────────┘
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │  POSITION SIZING      │
                              │                        │
                              │ • Kelly Criterion     │
                              │ • Volatility Adj      │
                              │ • Budget-Aware        │
                              └───────────┬─────────────┘
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │   RISK MANAGER         │
                              │                        │
                              │ • Daily Loss Limit     │
                              │ • Max Positions       │
                              │ • Sector Exposure     │
                              │ • Correlation Check   │
                              └───────────┬─────────────┘
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    │                                           │
                    ▼                                           ▼
           ┌─────────────────┐                      ┌─────────────────┐
           │   BRACKET ORDER │                      │   LIVE TRADE    │
           │   (Auto-TP/SL)  │                      │   (Paper/Live)  │
           └─────────────────┘                      └─────────────────┘
```

---

## ✨ Features

### Core Trading Engine

| Feature | Description |
|---------|-------------|
| **Multi-Signal Analysis** | 6 signal types: VWAP Breakout, EMA Crossover, RSI Momentum, Volume Spike, Price Action, Support/Resistance |
| **Strategy Types** | Momentum, Mean Reversion, Breakout, Scalping, Composite |
| **Timeframes** | 1m, 5m, 15m, 1h, 1d with cross-timeframe confirmation |
| **Indicators** | VWAP, EMA (9/21/50), RSI (14), Volume |

### Risk Management

| Feature | Description |
|---------|-------------|
| **Adaptive Position Sizing** | Kelly Criterion + budget-aware scaling |
| **Portfolio Risk Manager** | Daily P&L limits, consecutive loss protection |
| **Drawdown Protection** | Auto-trading disable at -6% daily loss |
| **Sector Exposure** | Configurable limits per sector |

### Order Types

| Order Type | Description |
|------------|-------------|
| **Bracket Orders** | Entry + Target + Stop Loss in one package |
| **GTT** | Good-Till-Triggered orders |
| **Trailing Stop** | Dynamic stop with activation threshold |
| **AMO** | After-Market Order queuing |

### Analytics

| Metric | Description |
|--------|-------------|
| **Sharpe Ratio** | Risk-adjusted returns |
| **Sortino Ratio** | Downside risk-adjusted returns |
| **Max Drawdown** | Peak-to-trough decline |
| **Profit Factor** | Gross profit / Gross loss |
| **Win Rate** | Profitable trade percentage |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/The-Peacemaker/Algo-Trade.git
cd Algo-Trade

# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install flask flask-socketio yfinance numpy pandas
```

### Running the System

```bash
# 1. Run Dashboard (Web UI)
python3 dashboard.py

# 2. Run Historical Backtest
python3 historical_backtest.py

# 3. Run Live Trading Bot
python3 live_bot.py
```

### Configuration

```python
# In your trading code
from trading_system import TradeConfig

config = TradeConfig(
    capital=5000,              # Your trading capital
    max_risk_percent=2.0,       # Max risk per trade (%)
    max_trades_per_day=3,       # Maximum trades per day
    min_risk_reward=2.0,        # Minimum risk:reward ratio
    trading_symbols=["RELIANCE", "TCS", "INFY"],
    paper_mode=True,            # Paper trading first!
    trading_start="09:15",     # Market open
    trading_end="15:00"        # Market close
)
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Broker Configuration (for live trading)
export ANGEL_ONE_API_KEY="your_api_key"
export ANGEL_ONE_CLIENT_CODE="your_client_id"
export ANGEL_ONE_PIN="your_pin"

# Telegram Alerts (optional)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### Stock Universe

Edit `stocks.py` to customize your trading universe:

```python
# Default watchlists
from stocks import WATCHLISTS

momentum_stocks = WATCHLISTS["momentum"]   # High-momentum stocks
banking_stocks = WATCHLISTS["banking"]     # Banking sector
intraday_stocks = WATCHLISTS["intraday"]   # Best for intraday
```

---

## 📈 Strategy Details

### Entry Conditions (LONG)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    LONG ENTRY CRITERIA                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│   PRIMARY (Must Have)                                                                      │
│   ├── Price > VWAP                                                               [2 pts] │
│   ├── EMA9 > EMA21 (trend alignment)                                              [2 pts] │
│   └── Volume > 1.5x Average                                                      [2 pts] │
│                                                                                            │
│   SECONDARY (Nice to Have)                                                                │
│   ├── EMA Crossover (just happened)                                                  [2 pts] │
│   ├── RSI in momentum zone (35-55)                                                [2 pts] │
│   └── Best trading time (9-10 AM IST)                                              [1 pt ] │
│                                                                                            │
│   SIGNAL GENERATION                                                                         │
│   └── Score >= 6/10 → Trade with 80%+ confidence                                    │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Risk-Reward

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    POSITION SIZING                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│   For ₹5,000 Capital:                                                                     │
│                                                                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│   │  Max Risk per Trade:  2%  =  ₹100                                            │    │
│   │  Stop Loss:             1%  =  ₹50                                            │    │
│   │  Target:                 2%  =  ₹100                                            │    │
│   │  Risk:Reward:           1:2                                                      │    │
│   │                                                                                  │    │
│   │  To be profitable:                                                                     │    │
│   │  Need only 34% win rate with 1:2 RR                                              │    │
│   │  (Traditional needs 50%+)                                                          │    │
│   └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                            │
│   Position Quantity = ₹100 / (Entry - Stop Loss)                                       │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Exit Strategy

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    EXIT STRATEGY                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│   PRIMARY EXITS                                                                             │
│   ├── Stop Loss Hit     →  Exit immediately (max 1% loss)                             │
│   ├── Target Reached    →  Exit at +2% (1:2 RR achieved)                              │
│   ├── Trend Reversal    →  Exit when price crosses VWAP opposite direction           │
│                                                                                            │
│   SECONDARY EXITS                                                                           │
│   ├── Time-based         →  Exit after 45 minutes (intraday)                            │
│   ├── Trailing Stop     →  Move to breakeven when 50% of target achieved              │
│   └── Emergency         →  Auto-disable trading after 2 consecutive losses             │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Risk Management

### Risk Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           RISK MANAGEMENT LAYER                                                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                     ACCOUNT-LEVEL RISK                                               │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐               │  │
│  │  │  Max Daily Loss │  │  Max Drawdown   │  │ Consecutive Loss│  │   Kelly         │               │  │
│  │  │      6%          │  │      10%         │  │      3           │  │   Criterion     │               │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                    POSITION-LEVEL RISK                                             │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐               │  │
│  │  │ Max Risk/Trade  │  │  Min Risk:Reward │  │  Max Positions   │  │  Sector Limit   │               │  │
│  │  │      2%          │  │       1:2         │  │       3          │  │      30%         │               │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                    TRADING HOURS RISK                                               │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐               │  │
│  │  │  Best: 9-10 AM  │  │  Good: 9-11 AM │  │ Caution:11-2PM │  │  Avoid: 2-3 PM │               │  │
│  │  │  (High Volatility)│  │  (Peak Liquidity)│  │  (Slow Market)  │  │ (Unpredictable) │               │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Integration

### Supported Brokers

| Broker | Status | Data API | Trading API | Python SDK |
|--------|--------|---------|-------------|------------|
| Angel One | ✅ Ready | ✅ | ✅ | ✅ |
| Groww | ✅ Ready | ✅ | ✅ Paid | ✅ |
| Zerodha | 📋 Coming | ✅ | ✅ | ✅ |
| Upstox | 📋 Coming | ✅ | ✅ | ✅ |

### Broker Setup

```python
# Angel One SmartAPI (Recommended - FREE)
from broker_angelone import AngelOneAPI

api = AngelOneAPI(
    api_key="YOUR_API_KEY",
    client_code="YOUR_CLIENT_ID",
    pin="YOUR_PIN"
)

# Login with TOTP
api.login(password="password", totp="123456")

# Get quote
quote = api.get_quote("RELIANCE")
print(quote)

# Place order
order = api.place_order(
    trading_symbol="RELIANCE",
    quantity=1,
    transaction_type="BUY",
    order_type="LIMIT",
    price=2500
)
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python3 test_system.py

# Expected output:
# ✓ Position Sizing Engine
# ✓ Portfolio Risk Manager
# ✓ Multi-Timeframe Analysis
# ✓ Advanced Orders
# ✓ Strategy Engine
# ✓ Backtest Engine
# ✓ Groww Connector
# ✓ Data Fetcher
# ✓ Trading System
# ✓ Stock Configuration
# ✓ Alert System
#
# RESULTS: 11 passed, 0 failed
```

### Backtest

```bash
python3 historical_backtest.py

# Results:
# Testing: RELIANCE, TCS, INFY, HDFCBANK, SBIN
# Average Return: ~10% (varies by market conditions)
# Win Rate: 40-60%
```

---

## 📊 Performance

### Backtest Results (Sample)

```
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                              BACKTEST RESULTS (6 Months)                                 ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║  Capital:        ₹5,000 → ₹5,400 (+8.0%)                                             ║
║  Total Trades:   72                                                                        ║
║  Win Rate:        45%                                                                        ║
║  Best Month:     +15% (SBIN)                                                            ║
║  Worst Month:    -3% (Market downturn)                                                 ║
║  Max Drawdown:   8%                                                                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Key Metrics

| Metric | Value | Benchmark |
|--------|-------|-----------|
| Sharpe Ratio | 1.2+ | > 1.0 Good |
| Sortino Ratio | 1.5+ | > 1.5 Good |
| Max Drawdown | < 10% | < 15% Acceptable |
| Win Rate | 40-50% | > 40% Break-even |
| Profit Factor | 1.5+ | > 1.5 Good |

---

## 🗺️ Roadmap

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        ROADMAP                                             │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│   PHASE 1 (Complete)                                                                       │
│   ├── ✅ Core trading engine                                                               │
│   ├── ✅ Risk management                                                                  │
│   ├── ✅ Position sizing                                                                  │
│   ├── ✅ Backtest engine                                                                  │
│   └── ✅ Dashboard                                                                        │
│                                                                                            │
│   PHASE 2 (In Progress)                                                                    │
│   ├── 🔄 Multi-broker support                                                            │
│   ├── 🔄 Telegram alerts                                                                 │
│   └── 🔄 Paper trading mode                                                               │
│                                                                                            │
│   PHASE 3 (Planned)                                                                       │
│   ├── 📅 Machine learning signals                                                        │
│   ├── 📅 Options trading                                                                  │
│   ├── 📅 Options chain analysis                                                            │
│   └── 📅 Futures trading                                                                  │
│                                                                                            │
│   PHASE 4 (Vision)                                                                        │
│   ├── 🤖 AI signal generation                                                            │
│   ├── 📊 Portfolio optimization                                                          │
│   └── 🌐 Multi-market support (US, Crypto)                                              │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

```bash
# 1. Fork the repository
# 2. Create your feature branch
git checkout -b feature/amazing-feature

# 3. Make your changes
# 4. Run tests
python3 test_system.py

# 5. Commit your changes
git commit -m 'Add amazing feature'

# 6. Push to GitHub
git push origin main

# 7. Create Pull Request
```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

```
MIT License

Copyright (c) 2024 QuantFlow Trading System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## ⚠️ Disclaimer

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DISCLAIMER                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY.                                           │
│                                                                                            │
│  • Trading in financial markets involves substantial risk                              │
│  • Past performance does not guarantee future results                                 │
│  • Never trade with money you cannot afford to lose                                    │
│  • Always use proper risk management                                                  │
│  • This is not financial advice                                                        │
│                                                                                            │
│  The authors and contributors assume no liability for any trading losses.              │
│  Use at your own risk.                                                                 │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🙏 Acknowledgments

- [Angel One SmartAPI](https://www.angelone.in/smartapi) - Free trading API
- [yfinance](https://pypi.org/project/yfinance/) - Market data
- [Flask](https://flask.palletsprojects.com/) - Web dashboard
- [Chart.js](https://www.chartjs.org/) - Beautiful charts

---

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=The-Peacemaker&repo=Algo-Trade&style=flat-square&label=Thanks+for+visiting&color=00ff88&style=for-the-badge" alt="Thanks">
</p>

<p align="center">
  <strong>⭐ Star this repo if you find it useful!</strong>
</p>

<p align="center">
  Made with ❤️ by <a href="https://github.com/The-Peacemaker">The Peacemaker</a>
</p>