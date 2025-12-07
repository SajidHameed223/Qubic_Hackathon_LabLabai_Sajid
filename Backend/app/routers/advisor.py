# app/routers/advisor.py

"""
LLM Advisor Router - Real-time financial advice endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ..db import get_db, User
from ..core.deps import get_current_user
from ..services import advisor
from ..config import settings


router = APIRouter(prefix="/advisor", tags=["advisor"])


class AdvisorRequest(BaseModel):
    """Request for advisor advice"""
    question: str
    wallet_identity: Optional[str] = None  # Override user's default wallet


class AdvisorResponse(BaseModel):
    """Response from advisor"""
    ok: bool
    advice: str
    suggested_goals: Optional[List[str]] = []
    context_used: Optional[dict] = {}
    timestamp: str
    error: Optional[str] = None


@router.post("/ask", response_model=AdvisorResponse)
async def ask_advisor(
    request: AdvisorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ask the LLM advisor for financial advice with PERSONALIZED recommendations.
    
    The advisor has access to:
    - Your wallet balance (live)
    - Your recent transfers
    - Your task history
    - Your investment preferences (risk tolerance, fee sensitivity, etc.)
    - LIVE market data (BTC price, market sentiment, trends)
    
    Examples:
    - "Can I safely send 500 QU right now?"
    - "How much have I sent this week?"
    - "What should I do with my current balance?"
    - "Suggest a DeFi strategy that matches my risk tolerance"
    """
    
    # Import market data service
    from ..services import market_data
    
    # Use provided wallet or fall back to environment variable
    wallet_identity = request.wallet_identity or settings.qubic_wallet_identity
    
    # Get wallet context (includes VIRTUAL balance)
    wallet_context = advisor.get_wallet_context(wallet_identity, db, current_user) if wallet_identity else {}
    
    # Get user activity context
    user_context = advisor.get_user_activity_context(db, current_user)
    
    # Get user preferences
    user_prefs = current_user.preferences if current_user.preferences else {}
    
    # Get LIVE market data
    live_market_data = await market_data.get_comprehensive_market_data()
    
    # Get LLM advice with ALL context
    result = advisor.get_llm_advice(
        request.question,
        wallet_context,
        user_context,
        user_prefs,
        live_market_data,
        wallet_identity
    )
    
    # Get suggested goals
    suggestions = advisor.suggest_agent_goals(user_context, wallet_context)
    
    return AdvisorResponse(
        ok=result.get("ok", False),
        advice=result.get("advice", "Unable to provide advice at this time"),
        suggested_goals=suggestions,
        context_used=result.get("context_used", {}),
        timestamp=result.get("timestamp", ""),
        error=result.get("error")
    )


@router.get("/suggestions", response_model=List[str])
def get_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get suggested agent goals based on your activity and balance.
    
    These are actionable goals you can send to /agent/run
    """
    
    wallet_identity = settings.qubic_wallet_identity
    
    # Get contexts
    wallet_context = advisor.get_wallet_context(wallet_identity) if wallet_identity else {}
    user_context = advisor.get_user_activity_context(db, current_user)
    
    # Get suggestions
    suggestions = advisor.suggest_agent_goals(user_context, wallet_context)
    
    return suggestions


@router.get("/status")
def get_wallet_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current wallet status and user activity summary.
    
    This provides the raw data that the advisor uses.
    """
    
    wallet_identity = settings.qubic_wallet_identity
    
    # Get all context data
    wallet_context = advisor.get_wallet_context(wallet_identity) if wallet_identity else {}
    user_context = advisor.get_user_activity_context(db, current_user)
    
    return {
        "user": {
            "email": user_context.get("user_email"),
            "member_since": user_context.get("member_since"),
            "total_tasks_last_week": user_context.get("total_tasks_last_week")
        },
        "wallet": {
            "identity": wallet_identity,
            "balance": wallet_context.get("balance"),
            "recent_transfers_count": len(wallet_context.get("recent_transfers", {}).get("transfers", []))
        },
        "recent_tasks": user_context.get("recent_tasks", [])[:5]
    }


class QuickAdviceRequest(BaseModel):
    """Quick advice scenarios"""
    scenario: str  # "send_qu", "balance_check", "weekly_summary", "strategy"
    amount: Optional[int] = None
    

@router.post("/quick")
async def get_quick_advice(
    request: QuickAdviceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get quick advice for common scenarios.
    
    Scenarios:
    - send_qu: "Can I safely send X QU?"
    - balance_check: "What's my current balance situation?"
    - weekly_summary: "Summarize my activity this week"
    - strategy: "Suggest a DeFi strategy"
    """
    
    # Import market data service
    from ..services import market_data
    
    questions = {
        "send_qu": f"Can I safely send {request.amount or 500} QU right now? What's my balance after that?",
        "balance_check": "What's my current balance and how does it compare to my recent activity?",
        "weekly_summary": "Summarize my wallet activity and tasks from the past week",
        "strategy": "Based on my current balance and activity, what DeFi strategy would you recommend?"
    }
    
    question = questions.get(request.scenario, request.scenario)
    
    wallet_identity = settings.qubic_wallet_identity
    wallet_context = advisor.get_wallet_context(wallet_identity) if wallet_identity else {}
    user_context = advisor.get_user_activity_context(db, current_user)
    
    # Get user preferences
    user_prefs = current_user.preferences if current_user.preferences else {}
    
    # Get LIVE market data
    live_market_data = await market_data.get_comprehensive_market_data()
    
    result = advisor.get_llm_advice(
        question,
        wallet_context,
        user_context,
        user_prefs,
        live_market_data,
        wallet_identity
    )
    
    return {
        "ok": result.get("ok", False),
        "advice": result.get("advice"),
        "scenario": request.scenario
    }


@router.get("/explain")
def explain_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze and explain the user's portfolio in natural language.
    
    Aggregates:
    - Current Balance
    - Pending Approvals
    - Recent Agent Activity
    """
    wallet_identity = settings.qubic_wallet_identity
    
    result = advisor.analyze_portfolio(db, current_user, wallet_identity)
    
    return {
        "ok": result.get("ok", False),
        "analysis": result.get("advice", "Could not generate analysis."),
        "timestamp": result.get("timestamp")
    }
