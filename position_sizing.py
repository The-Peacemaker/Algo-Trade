#!/usr/bin/env python3
"""
Adaptive Position Sizing Engine
=========================================
Budget-aware position sizing with dynamic risk adjustment
Supports budget range: ₹100 - ₹5,00,000

Key Features:
- Budget-based lot sizing
- Volatility-adjusted position sizing
- Kelly Criterion integration
- Optimal position calculator
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum
import math


class RiskProfile(Enum):
    ULTRASAFE = "ultrasafe"      # < ₹500 budget
    CONSERVATIVE = "conservative"  # ₹500-5000
    MODERATE = "moderate"       # ₹5000-50000
    AGGRESSIVE = "aggressive"    # > ₹50000


@dataclass
class PositionConfig:
    """Position configuration"""
    budget: float
    max_risk_percent: float = 2.0
    max_daily_risk_percent: float = 6.0
    max_position_size: int = 10
    min_trade_size: int = 1
    
    def __post_init__(self):
        if self.budget < 500:
            self.max_position_size = 1
        elif self.budget < 2000:
            self.max_position_size = 3
        elif self.budget < 10000:
            self.max_position_size = 5


class AdaptiveSizingEngine:
    """
    Adaptive Position Sizing Engine
    
    Calculates optimal position size based on:
    - Available budget (₹100 - ₹5,00,000)
    - Stock price and volatility
    - Account performance history
    - Market conditions
    """
    
    def __init__(self, config: PositionConfig):
        self.config = config
        self.risk_profile = self._determine_risk_profile()
        self.trade_history = []
        self.win_rate = 0.5
        self.avg_win = 0
        self.avg_loss = 0
        
    def _determine_risk_profile(self) -> RiskProfile:
        """Determine risk profile based on budget"""
        b = self.config.budget
        if b < 500:
            return RiskProfile.ULTRASAFE
        elif b < 5000:
            return RiskProfile.CONSERVATIVE
        elif b < 50000:
            return RiskProfile.MODERATE
        else:
            return RiskProfile.AGGRESSIVE
    
    def _get_base_risk_percent(self) -> float:
        """Get base risk percent based on profile"""
        limits = {
            RiskProfile.ULTRASAFE: 1.0,
            RiskProfile.CONSERVATIVE: 1.5,
            RiskProfile.MODERATE: 2.0,
            RiskProfile.AGGRESSIVE: 2.0
        }
        return limits[self.risk_profile]
    
    def _calculate_kelly_fraction(self) -> float:
        """
        Calculate Kelly Criterion for optimal position sizing
        
        K% = W - (1-W)/R
        Where:
            W = Win rate
            R = Win/Loss ratio
        """
        if len(self.trade_history) < 20:
            return self._get_base_risk_percent() / 100
        
        if self.avg_loss == 0:
            return self._get_base_risk_percent() / 100
        
        win_ratio = self.avg_win / abs(self.avg_loss) if self.avg_loss != 0 else 1
        kelly = self.win_rate - ((1 - self.win_rate) / win_ratio)
        
        # Use fractional Kelly (half) for safety
        kelly = max(0, min(kelly * 0.5, 0.25))
        return kelly
    
    def _get_max_leverage(self) -> float:
        """Get maximum leverage based on risk profile"""
        limits = {
            RiskProfile.ULTRASAFE: 1.0,      # No leverage
            RiskProfile.CONSERVATIVE: 1.0,   # No leverage
            RiskProfile.MODERATE: 2.0,      # 2x leverage
            RiskProfile.AGGRESSIVE: 3.0      # 3x leverage
        }
        return limits[self.risk_profile]
    
    def _get_max_leverage(self) -> float:
        """Get maximum leverage based on risk profile"""
        limits = {
            RiskProfile.ULTRASAFE: 1.0,
            RiskProfile.CONSERVATIVE: 1.0,
            RiskProfile.MODERATE: 2.0,
            RiskProfile.AGGRESSIVE: 3.0
        }
        return limits[self.risk_profile]
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        volatility: float = 0.02
    ) -> Dict:
        """
        Calculate optimal position size
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            volatility: Stock volatility (ATR/price)
            
        Returns:
            dict with quantity, risk_amount, risk_percent
        """
        max_leverage = self._get_max_leverage()
        max_affordable = self.config.budget * max_leverage
        
        if entry_price > max_affordable:
            return {
                "quantity": 0,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "risk_amount": 0,
                "risk_percent": 0,
                "target_price": entry_price,
                "kelly_fraction": 0,
                "budget_used": entry_price,
                "budget_utilization": 100,
                "error": f"Stock ₹{entry_price} exceeds max affordable ₹{max_affordable}"
            }
        
        # Risk per share
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share == 0:
            risk_per_share = entry_price * 0.01  # Default 1%
        
        # Base risk amount from budget
        base_risk = self.config.budget * (self._get_base_risk_percent() / 100)
        
        # Kelly-adjusted risk
        kelly = self._calculate_kelly_fraction()
        adjusted_risk = self.config.budget * kelly
        
        # Use minimum of base risk and adjusted risk
        risk_amount = min(base_risk, adjusted_risk)
        
        # Calculate raw quantity
        raw_quantity = risk_amount / risk_per_share
        
        # Volatility-adjusted quantity
        vol_adjustment = min(volatility / 0.02, 2.0)  # Cap at 2x
        adjusted_quantity = raw_quantity / vol_adjustment
        
        # Final quantity (integer, within limits)
        quantity = max(
            self.config.min_trade_size,
            min(
                int(adjusted_quantity),
                self.config.max_position_size
            )
        )
        
        # Ensure we can afford this quantity
        while (quantity * entry_price) > max_affordable and quantity > 1:
            quantity -= 1
        
        if quantity < self.config.min_trade_size:
            return {
                "quantity": 0,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "risk_amount": 0,
                "risk_percent": 0,
                "target_price": entry_price,
                "kelly_fraction": 0,
                "budget_used": entry_price,
                "budget_utilization": 100,
                "error": f"Cannot afford any lot at ₹{entry_price} with ₹{self.config.budget}"
            }
        
        # Actual risk
        actual_risk = quantity * risk_per_share
        actual_risk_percent = (actual_risk / self.config.budget) * 100
        
        return {
            "quantity": quantity,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "risk_amount": round(actual_risk, 2),
            "risk_percent": round(actual_risk_percent, 2),
            "target_price": entry_price * (1 + 0.02),
            "kelly_fraction": round(kelly * 100, 1),
            "budget_used": round((quantity * entry_price), 2),
            "budget_utilization": round((quantity * entry_price / self.config.budget) * 100, 1)
        }
    
    def calculate_max_positions(self, current_capital: float) -> int:
        """Calculate maximum concurrent positions"""
        # Conservative: don't risk more than 6% total per day
        daily_limit = 0.06
        
        base_risk = current_capital * (self._get_base_risk_percent() / 100)
        
        # Number of positions based on risk
        max_pos = int((current_capital * daily_limit) / (base_risk * 2))
        
        # Profile-based limits
        limits = {
            RiskProfile.ULTRASAFE: 1,
            RiskProfile.CONSERVATIVE: 2,
            RiskProfile.MODERATE: 3,
            RiskProfile.AGGRESSIVE: 5
        }
        
        return min(max_pos, limits[self.risk_profile])
    
    def update_performance(self, pnl: float, was_win: bool):
        """Update trade history for adaptive sizing"""
        self.trade_history.append({"pnl": pnl, "win": was_win})
        
        if len(self.trade_history) > 100:
            self.trade_history = self.trade_history[-100:]
        
        # Recalculate stats
        if self.trade_history:
            wins = sum(1 for t in self.trade_history if t["win"])
            self.win_rate = wins / len(self.trade_history)
            
            if was_win:
                self.avg_win = (self.avg_win * (wins - 1) + pnl) / wins if wins > 0 else pnl
            else:
                losses = len(self.trade_history) - wins
                self.avg_loss = (self.avg_loss * (losses - 1) + abs(pnl)) / losses if losses > 0 else abs(pnl)


# =========== TEST ===========
def test_adaptive_sizing():
    """Test the adaptive sizing engine"""
    
    print("=" * 60)
    print("ADAPTIVE POSITION SIZING ENGINE TEST")
    print("=" * 60)
    
    test_budgets = [200, 1000, 5000, 10000, 50000]
    
    for budget in test_budgets:
        config = PositionConfig(budget=budget)
        engine = AdaptiveSizingEngine(config)
        
        print(f"\n{'='*50}")
        print(f"Budget: ₹{budget}")
        print(f"Risk Profile: {engine.risk_profile.value}")
        
        # Test with different price points
        for price, stop in [(2500, 2475), (150, 148), (800, 792)]:
            result = engine.calculate_position_size(price, stop)
            print(f"  {price} | SL:{stop} → Qty:{result['quantity']} | Risk:₹{result['risk_amount']} ({result['risk_percent']}%)")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_adaptive_sizing()