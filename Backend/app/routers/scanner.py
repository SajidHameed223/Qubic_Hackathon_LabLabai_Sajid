from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.market_scanner import scanner

router = APIRouter(prefix="/scanner", tags=["Market Scanner"])

class TargetRequest(BaseModel):
    asset: str
    price: float



@router.post("/target")
async def set_target(req: TargetRequest):
    """Set a price target for an asset"""
    scanner.set_target(req.asset, req.price)
    return {"status": "Target Set", "asset": req.asset.upper(), "price": req.price}

@router.get("/alerts")
async def get_alerts():
    """Get all triggered alerts"""
    return scanner.alerts

@router.get("/status")
async def get_status():
    """Get scanner status"""
    return {
        "running": scanner.running,
        "watched_assets": scanner.assets_to_watch,
        "active_targets": scanner.targets
    }
