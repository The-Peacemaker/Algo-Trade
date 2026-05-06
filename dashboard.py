#!/usr/bin/env python3
"""
Trading Dashboard - Neo-Brutalism Futuristic Theme
Real-time monitoring with WebSocket
"""

import asyncio
import json
import time
import threading
import random
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# ============ DASHBOARD STATE ============
class DashboardState:
    def __init__(self):
        self.running = False
        self.capital = 5000.0
        self.current_capital = 5000.0
        self.trades_today = 0
        self.wins = 0
        self.losses = 0
        self.positions = []
        self.market_data = {}
        self.signals = []
        self.trade_history = []
        self.logs = []
        self.last_update = time.time()
    
    def add_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{ts}] {msg}")
        if len(self.logs) > 50:
            self.logs = self.logs[-50:]
        socketio.emit('log_update', {'message': f"[{ts}] {msg}"})
    
    def update_market(self, symbol: str, data: dict):
        self.market_data[symbol] = data
        self.last_update = time.time()
        socketio.emit('market_update', {'symbol': symbol, 'data': data})
    
    def update_signal(self, signal: dict):
        signal['timestamp'] = datetime.now().strftime("%H:%M:%S")
        self.signals.append(signal)
        if len(self.signals) > 30:
            self.signals = self.signals[-30:]
        socketio.emit('signal_update', signal)
    
    def trade_executed(self, trade: dict):
        self.trade_history.append(trade)
        self.trades_today += 1
        pnl = trade.get('pnl', 0)
        if pnl > 0:
            self.wins += 1
        else:
            self.losses += 1
        self.current_capital += pnl
        socketio.emit('trade_update', trade)
    
    def to_dict(self) -> dict:
        return {
            'running': self.running,
            'capital': self.capital,
            'current_capital': round(self.current_capital, 2),
            'pnl': round(self.current_capital - self.capital, 2),
            'trades_today': self.trades_today,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': round(self.wins / self.trades_today * 100, 1) if self.trades_today else 0,
            'positions': self.positions,
            'market_data': self.market_data[-15:] if len(self.market_data) > 15 else self.market_data,
            'signals': self.signals[-15:],
            'trade_history': self.trade_history[-20:],
            'logs': self.logs[-20:],
            'last_update': self.last_update
        }


state = DashboardState()


# ============ ROUTES ============
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    return jsonify(state.to_dict())


@app.route('/api/start', methods=['POST'])
def api_start():
    state.running = True
    state.add_log("▶ TRADING BOT STARTED")
    return jsonify({'status': 'ok', 'running': True})


@app.route('/api/stop', methods=['POST'])
def api_stop():
    state.running = False
    state.add_log("⏹ TRADING BOT STOPPED")
    return jsonify({'status': 'ok', 'running': False})


# ============ BACKGROUND SIMULATION ============
def background_sim():
    """Simulate market data"""
    import random
    
    symbols = {"RELIANCE": 2500, "TCS": 3200, "INFY": 1400, "HDFCBANK": 800}
    volumes = {"RELIANCE": 120000, "TCS": 80000, "INFY": 95000, "HDFCBANK": 60000}
    
    while True:
        if state.running:
            for sym, price in symbols.items():
                change = random.uniform(-8, 8)
                new_price = round(price + change, 2)
                symbols[sym] = new_price
                
                data = {
                    'price': new_price,
                    'change': round(change, 2),
                    'change_pct': round(change / price * 100, 2),
                    'volume': volumes[sym] + random.randint(-10000, 10000),
                    'vwap': round(new_price * random.uniform(0.98, 1.02), 2),
                    'rsi': random.randint(25, 75),
                    'ema_9': round(new_price * random.uniform(0.98, 1.02), 2),
                    'ema_21': round(new_price * random.uniform(0.97, 1.03), 2),
                }
                state.update_market(sym, data)
                
                # Random signals
                if random.random() < 0.03 and state.trades_today < 3:
                    direction = random.choice(['LONG', 'SELL', 'NO_TRADE'])
                    if direction != 'NO_TRADE':
                        signal = {
                            'symbol': sym,
                            'direction': direction,
                            'confidence': random.randint(70, 95),
                            'price': new_price,
                            'stop_loss': round(new_price * 0.985, 2),
                            'target': round(new_price * 1.035, 2),
                            'reasoning': random.choice([
                                '✓ Price above VWAP | ✓ EMA bullish crossover',
                                '✓ Volume spike | ✓ RSI momentum'
                            ])
                        }
                        state.update_signal(signal)
                        
                        # Execute trade
                        pnl = random.uniform(-80, 180)
                        trade = {
                            'symbol': sym,
                            'direction': direction,
                            'entry': new_price,
                            'exit': round(new_price + random.uniform(-30, 50), 2),
                            'pnl': round(pnl, 2),
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        }
                        state.trade_executed(trade)
                        state.add_log(f"💰 TRADE: {sym} {direction} | P&L: ₹{pnl:+.0f}")
        
        time.sleep(2.5)


# Start background
thread = threading.Thread(target=background_sim, daemon=True)
thread.start()


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║     🤖 ALGO TRADING DASHBOARD - NEO-FUTURE                    ║
╠══════════════════════════════════════════════════════════════╣
║  → http://localhost:5000                                    ║
║  → WebSocket enabled                                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)