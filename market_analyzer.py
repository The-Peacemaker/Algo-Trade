#!/usr/bin/env python3
"""
Real-Time Market Analyzer
====================
Professional-grade market analysis with real NSE data.
Uses yfinance for live market data + technical analysis.

Features:
- Real OHLCV data from NSE
- Technical indicators (VWAP, EMA, RSI, MACD, Bollinger)
- Candlestick pattern recognition
- Price action analysis
- Real-time signal generation
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"


class SignalType(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class CandlePattern:
    """Candlestick pattern"""
    name: str
    bullish: bool
    strength: float  # 0-100


@dataclass
class TechnicalIndicators:
    """Technical indicators"""
    # Price
    current_price: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    # Moving Averages
    sma_9: float
    sma_20: float
    sma_50: float
    ema_9: float
    ema_21: float
    ema_50: float
    
    # Trend Indicators
    vwap: float
    rsi: int
    macd: float
    macd_signal: float
    macd_hist: float
    
    # Volatility
    bb_upper: float
    bb_middle: float
    bb_lower: float
    atr: float
    
    # Momentum
    stochastic_k: float
    stochastic_d: float
    cci: float
    
    # Volume
    volume_ratio: float
    obv: float
    vwap_volume: float


@dataclass
class MarketAnalysis:
    """Complete market analysis"""
    symbol: str
    timestamp: datetime
    
    # Price Data
    price: float
    change: float
    change_percent: float
    
    # Indicators
    indicators: TechnicalIndicators
    
    # Patterns
    candle_patterns: List[CandlePattern]
    trend: TrendDirection
    
    # Signals
    signal: SignalType
    confidence: int  # 0-100
    
    # Summary
    summary: str


class CandlePatternDetector:
    """Detects candlestick patterns"""
    
    @staticmethod
    def detect(df: pd.DataFrame) -> List[CandlePattern]:
        patterns = []
        
        if len(df) < 5:
            return patterns
        
        # Get last 5 candles
        c1 = df.iloc[-1]  # Current
        c2 = df.iloc[-2]  # Previous
        c3 = df.iloc[-3]  # 2 back
        c4 = df.iloc[-4]  # 3 back
        c5 = df.iloc[-5]  # 4 back
        
        body = c1['Close'] - c1['Open']
        upper = c1['High'] - max(c1['Open'], c1['Close'])
        lower = min(c1['Open'], c1['Close']) - c1['Low']
        range_ = c1['High'] - c1['Low']
        
        # Doji
        if abs(body) < range_ * 0.1:
            patterns.append(CandlePattern("Doji", body >= 0, 60))
        
        # Hammer/Hanging Man
        if lower > body * 2 and upper < body * 0.5:
            if c1['Close'] > c1['Open'] and c1['Close'] > c2['Close']:
                patterns.append(CandlePattern("Hammer", True, 75))
            elif c1['Close'] < c1['Open'] and c1['Close'] < c2['Close']:
                patterns.append(CandlePattern("Hanging Man", False, 75))
        
        # Morning/Evening Star
        if (c3['Close'] < c3['Open'] and  # 3rd candle red
            c2['Close'] < c2['Open'] and  # 2nd candle red
            c1['Close'] > c1['Open'] and  # 1st candle green
            c1['Close'] > c2['Close'] and
            c1['Open'] < c2['Open']):
            patterns.append(CandlePattern("Morning Star", True, 80))
        
        if (c3['Close'] > c3['Open'] and
            c2['Close'] > c2['Open'] and
            c1['Close'] < c1['Open'] and
            c1['Close'] < c2['Close'] and
            c1['Open'] > c2['Open']):
            patterns.append(CandlePattern("Evening Star", False, 80))
        
        # Engulfing
        if (c2['Close'] < c2['Open'] and
            c1['Close'] > c1['Open'] and
            c1['Close'] > c2['Open'] and
            c1['Open'] < c2['Close']):
            patterns.append(CandlePattern("Bullish Engulfing", True, 75))
        
        if (c2['Close'] > c2['Open'] and
            c1['Close'] < c1['Open'] and
            c1['Close'] < c2['Open'] and
            c1['Open'] > c2['Close']):
            patterns.append(CandlePattern("Bearish Engulfing", False, 75))
        
        # Three White Soldiers / Black Crows
        if (c1['Close'] > c1['Open'] and
            c2['Close'] > c2['Open'] and
            c3['Close'] > c3['Open'] and
            all(df.iloc[-3:]['Close'] > df.iloc[-3:]['Open'])):
            patterns.append(CandlePattern("Three White Soldiers", True, 85))
        
        if (c1['Close'] < c1['Open'] and
            c2['Close'] < c2['Open'] and
            c3['Close'] < c3['Open'] and
            all(df.iloc[-3:]['Close'] < df.iloc[-3:]['Open'])):
            patterns.append(CandlePattern("Three Black Crows", False, 85))
        
        # Marubozu (strong move)
        if body > range_ * 0.9:
            patterns.append(CandlePattern("Marubozu", body > 0, 70))
        
        return patterns


class IndicatorCalculator:
    """Calculate technical indicators"""
    
    @staticmethod
    def calculate(df: pd.DataFrame) -> TechnicalIndicators:
        if len(df) < 50:
            raise ValueError("Need at least 50 candles for indicators")
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Basic price data
        current_price = latest['Close']
        
        # Moving Averages
        sma_9 = df['Close'].iloc[-9:].mean() if len(df) >= 9 else current_price
        sma_20 = df['Close'].iloc[-20:].mean() if len(df) >= 20 else current_price
        sma_50 = df['Close'].iloc[-50:].mean() if len(df) >= 50 else current_price
        
        ema_9 = IndicatorCalculator._ema(df['Close'], 9)
        ema_21 = IndicatorCalculator._ema(df['Close'], 21)
        ema_50 = IndicatorCalculator._ema(df['Close'], 50)
        
        # VWAP
        df_temp = df.copy()
        df_temp['PV'] = df_temp['Close'] * df_temp['Volume']
        vwap = df_temp['PV'].sum() / df_temp['Volume'].sum()
        
        # RSI
        rsi = IndicatorCalculator._rsi(df['Close'])
        
        # MACD
        macd, signal, hist = IndicatorCalculator._macd(df['Close'])
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = IndicatorCalculator._bollinger(df['Close'])
        
        # ATR
        atr = IndicatorCalculator._atr(df)
        
        # Stochastic
        stoch_k, stoch_d = IndicatorCalculator._stochastic(df)
        
        # CCI
        cci = IndicatorCalculator._cci(df)
        
        # Volume analysis
        avg_vol = df['Volume'].iloc[-20:].mean()
        volume_ratio = latest['Volume'] / avg_vol if avg_vol > 0 else 1
        
        # OBV
        obv = IndicatorCalculator._obv(df)
        
        # VWAP Volume
        df_temp['VP'] = df_temp['Close'] * df_temp['Volume']
        vwap_vol = df_temp['VP'].iloc[-20:].sum() / df_temp['Volume'].iloc[-20:].sum()
        
        return TechnicalIndicators(
            current_price=current_price,
            open=latest['Open'],
            high=latest['High'],
            low=latest['Low'],
            close=latest['Close'],
            volume=int(latest['Volume']),
            sma_9=round(sma_9, 2),
            sma_20=round(sma_20, 2),
            sma_50=round(sma_50, 2),
            ema_9=round(ema_9, 2),
            ema_21=round(ema_21, 2),
            ema_50=round(ema_50, 2),
            vwap=round(vwap, 2),
            rsi=round(rsi, 0),
            macd=round(macd, 2),
            macd_signal=round(signal, 2),
            macd_hist=round(hist, 2),
            bb_upper=round(bb_upper, 2),
            bb_middle=round(bb_middle, 2),
            bb_lower=round(bb_lower, 2),
            atr=round(atr, 2),
            stochastic_k=round(stoch_k, 2),
            stochastic_d=round(stoch_d, 2),
            cci=round(cci, 2),
            volume_ratio=round(volume_ratio, 2),
            obv=round(obv, 0),
            vwap_volume=round(vwap_vol, 2)
        )
    
    @staticmethod
    def _ema(series: pd.Series, period: int) -> float:
        if len(series) < period:
            return series.iloc[-1]
        
        ema = series.iloc[:period].mean()
        mult = 2 / (period + 1)
        
        for price in series.iloc[period:]:
            ema = (price - ema) * mult + ema
        
        return ema
    
    @staticmethod
    def _rsi(series: pd.Series, period: int = 14) -> float:
        if len(series) < period + 1:
            return 50
        
        deltas = series.diff()
        gains = deltas.clip(lower=0)
        losses = -deltas.clip(upper=0)
        
        avg_gain = gains.iloc[-period:].mean()
        avg_loss = losses.iloc[-period:].mean()
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def _macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        if len(series) < slow:
            return 0, 0, 0
        
        ema_fast = IndicatorCalculator._ema(series, fast)
        ema_slow = IndicatorCalculator._ema(series, slow)
        macd = ema_fast - ema_slow
        
        # Signal line (9-period EMA of MACD)
        macd_series = pd.Series([macd] * 10)
        macd_signal = IndicatorCalculator._ema(macd_series, signal) if len(macd_series) >= signal else macd
        
        hist = macd - macd_signal
        return macd, macd_signal, hist
    
    @staticmethod
    def _bollinger(series: pd.Series, period: int = 20, std_dev: float = 2):
        if len(series) < period:
            return series.iloc[-1], series.iloc[-1], series.iloc[-1]
        
        sma = series.iloc[-period:].mean()
        std = series.iloc[-period:].std()
        
        return sma + (std_dev * std), sma, sma - (std_dev * std)
    
    @staticmethod
    def _atr(df: pd.DataFrame, period: int = 14) -> float:
        if len(df) < period + 1:
            return 0
        
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        return true_range.iloc[-period:].mean()
    
    @staticmethod
    def _stochastic(df: pd.DataFrame, period: int = 14):
        if len(df) < period:
            return 50, 50
        
        low_min = df['Low'].iloc[-period:].min()
        high_max = df['High'].iloc[-period:].max()
        close = df['Close'].iloc[-1]
        
        if high_max == low_min:
            return 50, 50
        
        stoch_k = 100 * (close - low_min) / (high_max - low_min)
        
        # Smoothed %D
        stoch_d = stoch_k  # Simplified
        
        return stoch_k, stoch_d
    
    @staticmethod
    def _cci(df: pd.DataFrame, period: int = 20) -> float:
        if len(df) < period:
            return 0
        
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        sma = tp.iloc[-period:].mean()
        mad = tp.iloc[-period:].apply(lambda x: abs(x - sma)).mean()
        
        if mad == 0:
            return 0
        
        cci = (tp.iloc[-1] - sma) / (0.015 * mad)
        return cci
    
    @staticmethod
    def _obv(df: pd.DataFrame) -> float:
        obv = 0
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                obv += df['Volume'].iloc[i]
            elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                obv -= df['Volume'].iloc[i]
        return obv


class SignalGenerator:
    """Generate trading signals from analysis"""
    
    @staticmethod
    def generate(analysis: MarketAnalysis) -> Tuple[SignalType, int, str]:
        ind = analysis.indicators
        patterns = analysis.candle_patterns
        price = ind.current_price
        
        score = 0
        reasons = []
        
        # Price vs Moving Averages (20 points max)
        if price > ind.sma_20:
            score += 10
            reasons.append("Price > SMA20")
        else:
            score -= 10
            reasons.append("Price < SMA20")
        
        if price > ind.ema_9:
            score += 5
            reasons.append("Price > EMA9")
        
        # RSI (25 points max)
        if ind.rsi < 30:
            score += 15  # Oversold - BUY
            reasons.append(f"RSI oversold ({ind.rsi})")
        elif ind.rsi > 70:
            score -= 15  # Overbought - SELL
            reasons.append(f"RSI overbought ({ind.rsi})")
        elif ind.rsi < 45:
            score += 5
            reasons.append(f"RSI low ({ind.rsi})")
        elif ind.rsi > 55:
            score -= 5
            reasons.append(f"RSI high ({ind.rsi})")
        
        # MACD (15 points max)
        if ind.macd_hist > 0:
            score += 10
            reasons.append("MACD bullish")
        else:
            score -= 10
            reasons.append("MACD bearish")
        
        # Bollinger (10 points max)
        if price < ind.bb_lower:
            score += 10
            reasons.append("Near lower BB")
        elif price > ind.bb_upper:
            score -= 10
            reasons.append("Near upper BB")
        
        # Volume (10 points max)
        if ind.volume_ratio > 1.5:
            score += 5
            reasons.append(f"High volume ({ind.volume_ratio:.1f}x)")
        
        # VWAP (10 points max)
        if price > ind.vwap:
            score += 5
            reasons.append("Price > VWAP")
        else:
            score -= 5
            reasons.append("Price < VWAP")
        
        # Candle Patterns (20 points max)
        bullish_patterns = [p for p in patterns if p.bullish]
        bearish_patterns = [p for p in patterns if not p.bullish]
        
        for p in bullish_patterns:
            score += int(p.strength * 0.2)
        for p in bearish_patterns:
            score -= int(p.strength * 0.2)
        
        if bullish_patterns:
            reasons.append(f"Bullish: {[p.name for p in bullish_patterns[:3]]}")
        
        # Stochastic (10 points max)
        if ind.stochastic_k < 20:
            score += 10
            reasons.append(f"Stochastic oversold ({ind.stochastic_k:.0f})")
        elif ind.stochastic_k > 80:
            score -= 10
            reasons.append(f"Stochastic overbought ({ind.stochastic_k:.0f})")
        
        # Determine signal
        confidence = min(abs(score), 100)
        
        if score >= 60:
            signal = SignalType.STRONG_BUY
            summary = f"STRONG BUY - Score: {score} | {' | '.join(reasons[:4])}"
        elif score >= 30:
            signal = SignalType.BUY
            summary = f"BUY - Score: {score} | {' | '.join(reasons[:3])}"
        elif score <= -60:
            signal = SignalType.STRONG_SELL
            summary = f"STRONG SELL - Score: {score} | {' | '.join(reasons[:4])}"
        elif score <= -30:
            signal = SignalType.SELL
            summary = f"SELL - Score: {score} | {' | '.join(reasons[:3])}"
        else:
            signal = SignalType.NEUTRAL
            summary = f"NEUTRAL - Score: {score} | {' | '.join(reasons[:2])}"
        
        return signal, confidence, summary


class MarketAnalyzer:
    """Main market analyzer class"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
    
    def analyze(self, symbol: str, period: str = "5d", interval: str = "5m") -> Optional[MarketAnalysis]:
        """Analyze a symbol"""
        try:
            # Fetch data
            df = self._fetch_data(symbol, period, interval)
            if df is None or len(df) < 50:
                logger.warning(f"Insufficient data for {symbol}")
                return None
            
            # Calculate indicators
            indicators = IndicatorCalculator.calculate(df)
            
            # Detect patterns
            patterns = CandlePatternDetector.detect(df)
            
            # Determine trend
            trend = TrendDirection.SIDEWAYS
            if indicators.ema_9 > indicators.ema_21 > indicators.ema_50:
                trend = TrendDirection.BULLISH
            elif indicators.ema_9 < indicators.ema_21 < indicators.ema_50:
                trend = TrendDirection.BEARISH
            
            # Price change
            current = df.iloc[-1]['Close']
            prev = df.iloc[-2]['Close'] if len(df) > 1 else current
            change = current - prev
            change_pct = (change / prev) * 100
            
            # Generate signal
            analysis = MarketAnalysis(
                symbol=symbol,
                timestamp=datetime.now(),
                price=current,
                change=change,
                change_percent=change_pct,
                indicators=indicators,
                candle_patterns=patterns,
                trend=trend,
                signal=SignalType.NEUTRAL,
                confidence=0,
                summary=""
            )
            
            signal, confidence, summary = SignalGenerator.generate(analysis)
            analysis.signal = signal
            analysis.confidence = confidence
            analysis.summary = summary
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis error for {symbol}: {e}")
            return None
    
    def _fetch_data(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data from yfinance"""
        try:
            # Convert to yfinance format
            nse_symbol = f"{symbol}.NS"
            ticker = yf.Ticker(nse_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return None
            
            return df
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            return None


def print_analysis(a: MarketAnalysis):
    """Print formatted analysis"""
    ind = a.indicators
    
    print(f"\n{'='*70}")
    print(f"  {a.symbol:^15} | ₹{a.price:>8.2f} | {a.change:>+8.2f} ({a.change_percent:+.2f}%)")
    print(f"{'='*70}")
    
    print(f"  Signal: {a.signal.value:^12} | Confidence: {a.confidence}% | Trend: {a.trend.value}")
    print(f"  Summary: {a.summary}")
    
    print(f"\n--- Technical Indicators ---")
    print(f"  Price:     ₹{ind.current_price:.2f} | Open: ₹{ind.open:.2f} | High: ₹{ind.high:.2f} | Low: ₹{ind.low:.2f}")
    print(f"  SMA:       9:{ind.sma_9:>7.2f} | 20:{ind.sma_20:>7.2f} | 50:{ind.sma_50:>7.2f}")
    print(f"  EMA:       9:{ind.ema_9:>7.2f} | 21:{ind.ema_21:>7.2f} | 50:{ind.ema_50:>7.2f}")
    print(f"  VWAP:      ₹{ind.vwap:>8.2f} | RSI:{ind.rsi:>4.0f} | MACD:{ind.macd:>7.2f}")
    print(f"  BB:       {ind.bb_lower:>6.2f} | {ind.bb_middle:>6.2f} | {ind.bb_upper:>6.2f}")
    print(f"  ATR:      ₹{ind.atr:>7.2f} | Stoch:{ind.stochastic_k:>5.1f} | CCI:{ind.cci:>5.0f}")
    print(f"  Volume:   {ind.volume:,} ({ind.volume_ratio:.1f}x avg)")
    
    if a.candle_patterns:
        print(f"\n--- Candle Patterns ---")
        for p in a.candle_patterns[:5]:
            print(f"  {'🟢' if p.bullish else '🔴'} {p.name} ({p.strength}%)")


def scan_market(analyzer: MarketAnalyzer, symbols: List[str]) -> List[MarketAnalysis]:
    """Scan multiple symbols"""
    results = []
    
    for symbol in symbols:
        a = analyzer.analyze(symbol)
        if a:
            results.append(a)
    
    # Sort by confidence
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results


if __name__ == "__main__":
    # Test with real NSE data
    print("="*70)
    print("REAL-TIME MARKET ANALYZER - NSE DATA")
    print("="*70)
    
    analyzer = MarketAnalyzer()
    
    # Popular NSE stocks
    symbols = ['RELIANCE', 'TCS', 'INFY', 'SBIN', 'HDFCBANK', 'ICICIBANK', 
              'KOTAKBANK', 'AXISBANK', 'HINDUNILVR', 'ITC', 'TITAN']
    
    results = scan_market(analyzer, symbols)
    
    print(f"\n{'='*70}")
    print("MARKET SCAN RESULTS")
    print(f"{'='*70}")
    
    for a in results[:10]:
        print_analysis(a)
    
    # Summary
    print(f"\n{'='*70}")
    print("SIGNALS SUMMARY")
    print(f"{'='*70}")
    
    buy_signals = [a for a in results if a.signal in [SignalType.BUY, SignalType.STRONG_BUY]]
    sell_signals = [a for a in results if a.signal in [SignalType.SELL, SignalType.STRONG_SELL]]
    
    print(f"Buy Signals:  {len(buy_signals)}")
    for a in buy_signals[:5]:
        print(f"  🟢 {a.symbol:12} ₹{a.price:>8.2f} | {a.signal.value} ({a.confidence}%)")
    
    print(f"\nSell Signals: {len(sell_signals)}")
    for a in sell_signals[:5]:
        print(f"  🔴 {a.symbol:12} ₹{a.price:>8.2f} | {a.signal.value} ({a.confidence}%)")