from fastapi import APIRouter
from pydantic import BaseModel
from app.services.strategy_engine import strategy_engine

router = APIRouter(prefix="/strategy", tags=["Strategy"])

class StrategyConfig(BaseModel):
    enabled: bool
    amount_usd: float

@router.get("/")
def get_strategies():
    """Get all active strategies and their status"""
    return strategy_engine.active_strategies

@router.post("/rsi_buy")
def configure_rsi_buy(config: StrategyConfig):
    """Configure the RSI Buy Strategy"""
    strategy_engine.active_strategies["RSI_BUY"]["enabled"] = config.enabled
    strategy_engine.active_strategies["RSI_BUY"]["amount_usd"] = config.amount_usd
    return {"status": "Updated", "config": strategy_engine.active_strategies["RSI_BUY"]}
