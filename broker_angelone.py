#!/usr/bin/env python3
"""
Angel One SmartAPI Integration
=====================================
SETUP INSTRUCTIONS:
1. Go to https://smartapi.angelbroking.com
2. Sign Up for SmartAPI
3. Create an App → Get API Key + Secret
4. Copy them below

API DOCUMENTATION:
https://www.angelone.in/knowledge-center/smartapi-detailed-introduction-to-smartapi

RATE LIMITS:
- Orders: 200/sec
- Market Data: 100/sec
"""

import json
import hashlib
import hmac
import base64
import time
import requests
from datetime import datetime
from typing import Dict, Optional, List


class AngelOneAPI:
    """Angel One SmartAPI Client"""
    
    BASE_URL = "https://api.angelone.in/smartapi"
    
    def __init__(self, api_key: str, client_code: str = "", pin: str = ""):
        self.api_key = api_key
        self.client_code = client_code
        self.pin = pin
        self.access_token = None
        self.feed_token = None
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Version": "1.0"
        })
    
    # ============ AUTHENTICATION ============
    
    def generate_pin_hash(self, pin: str, api_key: str) -> str:
        """Generate hash for PIN"""
        return hashlib.sha256(f"{pin}{api_key}".encode()).hexdigest()
    
    def login(self, password: str, totp: str) -> Dict:
        """Login with credentials"""
        url = f"{self.BASE_URL}/session/login"
        
        payload = {
            "clientcode": self.client_code,
            "password": password,
            "pin": self.generate_pin_hash(self.pin, self.api_key),
            "api_key": self.api_key,
            "totp": totp
        }
        
        try:
            resp = self.session.post(url, json=payload, timeout=30)
            data = resp.json()
            
            if data.get("status"):
                self.access_token = data.get("data", {}).get("accessToken")
                self.feed_token = data.get("data", {}).get("feedToken")
                self.session.headers["Authorization"] = f"Bearer {self.access_token}"
                return {"status": True, "message": "Logged in"}
            
            return {"status": False, "message": data.get("message", "Login failed")}
        
        except Exception as e:
            return {"status": False, "message": str(e)}
    
    def logout(self) -> Dict:
        """Logout"""
        url = f"{self.BASE_URL}/session/logout"
        
        try:
            resp = self.session.post(url, json={"clientcode": self.client_code})
            data = resp.json()
            self.access_token = None
            return data
        except Exception as e:
            return {"status": False, "message": str(e)}
    
    # ============ MARKET DATA ============
    
    def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """Get live quote"""
        url = f"{self.BASE_URL}/marketdata/ltpc"
        params = {"exchange": exchange, "scripcode": symbol}
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("status"):
                return data.get("data", {})
        except Exception as e:
            print(f"Quote error: {e}")
        return None
    
    def get_ohlc(self, symbol: str, exchange: str = "NSE", interval: str = "ONE_DAY", days: int = 30) -> List[Dict]:
        """Get historical OHLC"""
        url = f"{self.BASE_URL}/historical/ candles"
        params = {
            "exchange": exchange,
            "scripcode": symbol,
            "intervaltype": interval,
            "fromdate": f"2025-01-01",
            "todate": datetime.now().strftime("%Y-%m-%d")
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=30)
            data = resp.json()
            if data.get("status"):
                return data.get("data", {}).get("candles", [])
        except Exception as e:
            print(f"OHLC error: {e}")
        return []
    
    # ============ ORDERS ============
    
    def place_order(
        self,
        trading_symbol: str,
        quantity: int,
        transaction_type: str,  # BUY or SELL
        order_type: str = "LIMIT",  # LIMIT, MARKET, SL, SLM
        price: float = 0,
        exchange: str = "NSE",
        product: str = "CNC",  # CNC, MIS, NRML
        validity: str = "DAY"
    ) -> Dict:
        """Place order"""
        url = f"{self.BASE_URL}/order/place"
        
        payload = {
            "exchange": exchange,
            "scripcode": trading_symbol,
            "transactiontype": transaction_type,
            "quantity": quantity,
            "producttype": product,
            "ordertype": order_type,
            "price": price,
            "validity": validity,
            "discquantity": 0
        }
        
        try:
            resp = self.session.post(url, json=payload, timeout=30)
            return resp.json()
        except Exception as e:
            return {"status": False, "message": str(e)}
    
    def modify_order(self, order_id: str, quantity: int = 0, price: float = 0) -> Dict:
        """Modify order"""
        url = f"{self.BASE_URL}/order/modify"
        
        payload = {
            "orderid": order_id,
            "quantity": quantity,
            "price": price
        }
        
        try:
            resp = self.session.post(url, json=payload, timeout=30)
            return resp.json()
        except Exception as e:
            return {"status": False, "message": str(e)}
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel order"""
        url = f"{self.BASE_URL}/order/cancel"
        
        try:
            resp = self.session.post(url, json={"orderid": order_id})
            return resp.json()
        except Exception as e:
            return {"status": False, "message": str(e)}
    
    def get_order_book(self) -> List[Dict]:
        """Get order book"""
        url = f"{self.BASE_URL}/orderbook"
        
        try:
            resp = self.session.get(url, timeout=30)
            data = resp.json()
            if data.get("status"):
                return data.get("data", [])
        except Exception as e:
            print(f"Order book error: {e}")
        return []
    
    def get_trade_book(self) -> List[Dict]:
        """Get trade book"""
        url = f"{self.BASE_URL}/tradebook"
        
        try:
            resp = self.session.get(url, timeout=30)
            data = resp.json()
            if data.get("status"):
                return data.get("data", [])
        except Exception as e:
            print(f"Trade book error: {e}")
        return []
    
    # ============ POSITIONS ============
    
    def get_positions(self) -> List[Dict]:
        """Get positions"""
        url = f"{self.BASE_URL}/positionbook"
        
        try:
            resp = self.session.get(url, timeout=30)
            data = resp.json()
            if data.get("status"):
                return data.get("data", [])
        except Exception as e:
            print(f"Position error: {e}")
        return []
    
    def get_holdings(self) -> List[Dict]:
        """Get holdings"""
        url = f"{self.BASE_URL}/holdings"
        
        try:
            resp = self.session.get(url, timeout=30)
            data = resp.json()
            if data.get("status"):
                return data.get("data", [])
        except Exception as e:
            print(f"Holdings error: {e}")
        return []
    
    def get_margin(self) -> Dict:
        """Get account margin"""
        url = f"{self.BASE_URL}/limits"
        
        try:
            resp = self.session.get(url, timeout=30)
            data = resp.json()
            if data.get("status"):
                return data.get("data", {})
        except Exception as e:
            print(f"Margin error: {e}")
        return {}


# ============ CONFIGURATION ============
# TODO: Replace with your actual credentials
CONFIG = {
    "api_key": "YOUR_API_KEY_HERE",        # From SmartAPI dashboard
    "client_code": "YOUR_CLIENT_ID",        # Your Angel One client ID
    "pin": "YOUR_PIN",                   # Your trading PIN
    "password": "YOUR_PASSWORD",         # Your Angel One password
    "totp": "YOUR_TOTP_SECRET"         # TOTP from app
}


# ============ TEST ============
def test_connection():
    """Test API connection"""
    print("Testing Angel One SmartAPI...")
    
    # Initialize with config
    api = AngelOneAPI(
        api_key=CONFIG["api_key"],
        client_code=CONFIG["client_code"],
        pin=CONFIG["pin"]
    )
    
    # Try to get quote
    quote = api.get_quote("RELIANCE")
    
    if quote:
        print(f"✓ Connection successful!")
        print(f"RELIANCE: ₹{quote}")
    else:
        print("✗ Connection failed (check credentials)")
    
    return api


if __name__ == "__main__":
    # Test without credentials
    print("=" * 50)
    print("ANGEL ONE SMARTAPI CLIENT")
    print("=" * 50)
    print("""
Setup:
1. Go to https://smartapi.angelbroking.com
2. Sign Up → Create App → Get API Key
3. Update CONFIG in this file with your credentials

Usage:
    from broker_integration import AngelOneAPI
    
    api = AngelOneAPI("your_api_key", "client_code", "pin")
    api.login(password, totp)
    
    # Get quote
    quote = api.get_quote("RELIANCE")
    print(quote)
    
    # Place order
    api.place_order("RELIANCE", 1, "BUY", "LIMIT", 2500)
    """)
    print("=" * 50)