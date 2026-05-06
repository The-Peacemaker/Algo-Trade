#!/usr/bin/env python3
"""
Proper Forward-Walking Backtest (No Look-Ahead Bias)
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


def fetch_yahoo_data(symbol: str, days: int = 180) -> List[Dict]:
    """Fetch historical data from Yahoo Finance"""
    import yfinance as yf
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        hist = ticker.history(period=f"{days}d")
        if hist.empty:
            return []
        
        data = []
        for idx, row in hist.iterrows():
            data.append({
                "Date": idx,
                "Open": row["Open"],
                "High": row["High"],
                "Low": row["Low"],
                "Close": row["Close"],
                "Volume": row["Volume"]
            })
        return data
    except Exception as e:
        logger.error(f"yfinance error: {e}")
        return []


class ForwardWalkBacktest:
    """Proper forward-walking backtest without look-ahead bias"""
    
    def __init__(self, initial_capital: float = 5000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
    
    def run(self, candles: List[Dict], symbol: str) -> Dict:
        """Run forward-walking backtest"""
        
        from data_fetcher import DataManager, OHLC
        from trading_system import TradeConfig
        
        config = TradeConfig(
            capital=self.initial_capital,
            max_risk_percent=2.0,
            max_trades_per_day=3,
            min_risk_reward=2.0,
            trading_symbols=[symbol],
            paper_mode=True
        )
        
        data_manager = DataManager()
        
        trades = []
        signals = []
        wins = 0
        losses = 0
        
        open_position = None
        
        # Walk through data chronologically
        for i in range(len(candles)):
            candle = candles[i]
            
            # Add to history (ONLY past data available at this point)
            ohlc_obj = OHLC(
                timestamp=datetime.now(),
                open=candle["Open"],
                high=candle["High"],
                low=candle["Low"],
                close=candle["Close"],
                volume=candle["Volume"]
            )
            
            data_manager.ohlc_data[symbol] = data_manager.ohlc_data.get(symbol, []) + [ohlc_obj]
            data_manager.volume_history[symbol] = data_manager.volume_history.get(symbol, []) + [ohlc_obj.volume]
            
            # Need warmup period
            if i < 30:
                continue
            
            market_data = data_manager.get_market_data(symbol)
            prev_data = data_manager.get_prev_market_data(symbol, 1)
            
            if market_data is None:
                continue
            
            # Generate signal using ONLY past data
            from trading_system import StrategyEngine, TradeDirection
            engine = StrategyEngine(config)
            signal = engine.analyze_market_data(market_data, prev_data, bypass=True)
            
            # Track signal (no execution yet)
            if signal.direction != TradeDirection.NO_TRADE and signal.confidence >= 80:
                signals.append({
                    "bar": i,
                    "price": market_data.current_price,
                    "dir": signal.direction.value,
                    "conf": signal.confidence
                })
                
                # Execute ONLY if no open position
                if open_position is None and signal.direction in [TradeDirection.LONG]:
                    risk = self.capital * 0.02  # 2% risk
                    stop_distance = abs(market_data.current_price - signal.stop_loss)
                    if stop_distance > 0:
                        qty = int(risk / stop_distance)
                        if qty > 0:
                            open_position = {
                                "entry_price": market_data.current_price,
                                "entry_bar": i,
                                "qty": qty,
                                "stop_loss": signal.stop_loss,
                                "target": signal.target_price,
                                "direction": signal.direction.value
                            }
            
            # Check exit conditions (using current bar - no look-ahead)
            if open_position is not None:
                current_price = market_data.current_price
                
                should_exit = False
                exit_reason = ""
                
                if open_position["direction"] == "LONG":
                    if current_price <= open_position["stop_loss"]:
                        should_exit = True
                        exit_reason = "SL hit"
                    elif current_price >= open_position["target"]:
                        should_exit = True
                        exit_reason = "Target hit"
                
                if should_exit:
                    pnl = 0
                    if open_position["direction"] == "LONG":
                        pnl = (current_price - open_position["entry_price"]) * open_position["qty"]
                    
                    trades.append({
                        "entry": open_position["entry_price"],
                        "exit": current_price,
                        "qty": open_position["qty"],
                        "pnl": pnl,
                        "reason": exit_reason,
                        "bars_held": i - open_position["entry_bar"]
                    })
                    
                    self.capital += pnl
                    
                    if pnl > 0:
                        wins += 1
                    else:
                        losses += 1
                    
                    open_position = None
        
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        return {
            "symbol": symbol,
            "initial": self.initial_capital,
            "final": round(self.capital, 2),
            "return_pct": round(total_return, 2),
            "signals": len(signals),
            "trades": len(trades),
            "wins": wins,
            "losses": losses,
            "win_rate": round(wins/len(trades)*100, 1) if trades else 0
        }


async def main():
    logger.info("=" * 60)
    logger.info("PROPER FORWARD-WALKING BACKTEST")
    logger.info("=" * 60)
    
    test_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN"]
    all_results = []
    
    for symbol in test_symbols:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing: {symbol}")
        
        data = fetch_yahoo_data(symbol, 180)
        if not data:
            continue
        
        logger.info(f"Loaded {len(data)} bars")
        
        engine = ForwardWalkBacktest(initial_capital=5000)
        result = engine.run(data, symbol)
        all_results.append(result)
        
        logger.info(f"Capital: ₹{result['initial']} → ₹{result['final']}")
        logger.info(f"Return: {result['return_pct']}%")
        logger.info(f"Trades: {result['trades']} | Win: {result['win_rate']}%")
    
    # Summary
    if all_results:
        avg_return = sum(r["return_pct"] for r in all_results) / len(all_results)
        avg_trades = sum(r["trades"] for r in all_results)
        avg_win = sum(r["win_rate"] for r in all_results) / len(all_results)
        
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Avg Return: {avg_return:.1f}%")
        logger.info(f"Total Trades: {avg_trades}")
        logger.info(f"Avg Win Rate: {avg_win:.1f}%")


asyncio.run(main())