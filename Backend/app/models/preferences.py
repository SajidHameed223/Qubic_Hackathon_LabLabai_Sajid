# app/models/preferences.py

"""
User Preferences Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class RiskTolerance(str, Enum):
    """Investment risk tolerance levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class InvestmentGoal(str, Enum):
    """Investment goals"""
    CAPITAL_PRESERVATION = "capital_preservation"
    INCOME_GENERATION = "income_generation"
    GROWTH = "growth"
    AGGRESSIVE_GROWTH = "aggressive_growth"
    SPECULATION = "speculation"


class FeeSensitivity(str, Enum):
    """Sensitivity to transaction fees"""
    VERY_SENSITIVE = "very_sensitive"  # Minimize all fees
    SENSITIVE = "sensitive"  # Keep fees low
    MODERATE = "moderate"  # Balance fees and benefits
    INSENSITIVE = "insensitive"  # Fees not a concern


class UserPreferences(BaseModel):
    """Complete user investment preferences"""
    
    # Risk & Goals
    risk_tolerance: RiskTolerance = Field(
        default=RiskTolerance.MEDIUM,
        description="Investment risk tolerance level"
    )
    investment_goals: List[InvestmentGoal] = Field(
        default=[InvestmentGoal.GROWTH],
        description="Primary investment goals"
    )
    
    # Fees & Costs
    fee_sensitivity: FeeSensitivity = Field(
        default=FeeSensitivity.SENSITIVE,
        description="How sensitive to transaction fees"
    )
    max_acceptable_fee_percent: Optional[float] = Field(
        default=0.5,
        description="Maximum acceptable fee percentage"
    )
    
    # Portfolio Settings
    min_balance_reserve: Optional[int] = Field(
        default=1000,
        description="Minimum QU balance to always maintain"
    )
    max_single_transaction_percent: Optional[float] = Field(
        default=20.0,
        description="Max % of balance in single transaction"
    )
    
    # Time Horizon
    investment_horizon: Optional[str] = Field(
        default="medium_term",
        description="short_term, medium_term, or long_term"
    )
    
    # DeFi Preferences
    prefer_staking: bool = Field(
        default=True,
        description="Interest in staking for passive income"
    )
    prefer_liquidity_pools: bool = Field(
        default=False,
        description="Interest in providing liquidity"
    )
    prefer_yield_farming: bool = Field(
        default=False,
        description="Interest in yield farming strategies"
    )
    avoid_leverage: bool = Field(
        default=True,
        description="Avoid leveraged positions"
    )
    
    # Automation Preferences
    auto_rebalance: bool = Field(
        default=False,
        description="Enable automatic portfolio rebalancing"
    )
    alert_on_large_movements: bool = Field(
        default=True,
        description="Get alerts on significant price movements"
    )
    
    # Additional Notes
    notes: Optional[str] = Field(
        default="",
        description="Any additional preferences or constraints"
    )


class PreferencesUpdate(BaseModel):
    """Update user preferences (all fields optional)"""
    risk_tolerance: Optional[RiskTolerance] = None
    investment_goals: Optional[List[InvestmentGoal]] = None
    fee_sensitivity: Optional[FeeSensitivity] = None
    max_acceptable_fee_percent: Optional[float] = None
    min_balance_reserve: Optional[int] = None
    max_single_transaction_percent: Optional[float] = None
    investment_horizon: Optional[str] = None
    prefer_staking: Optional[bool] = None
    prefer_liquidity_pools: Optional[bool] = None
    prefer_yield_farming: Optional[bool] = None
    avoid_leverage: Optional[bool] = None
    auto_rebalance: Optional[bool] = None
    alert_on_large_movements: Optional[bool] = None
    notes: Optional[str] = None
