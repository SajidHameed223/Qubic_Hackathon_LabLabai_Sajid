# app/services/advisor.py

"""
LLM Advisor Service - Real-time, Qubic-aware AI advisor

Provides personalized financial advice based on:
- Live wallet balance
- Recent transfers
- Task history
- Market conditions
"""

from typing import Dict, Any, Optional, List
import json
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from . import qubic_client
from ..db import TaskRecord, User
from ..models.task import Task
from sqlalchemy.orm import Session


def get_wallet_context(wallet_identity: str, db: Session = None, user: User = None) -> Dict[str, Any]:
    """
    Get comprehensive wallet context for advice.
    
    Now includes both:
    - Virtual balance (from database)
    - On-chain balance (from Qubic RPC)
    """
    from . import wallet as wallet_service
    from sqlalchemy.orm import Session as SessionType
    
    context = {}
    
    # Get VIRTUAL balance if user provided
    if db and user:
        try:
            user_wallet = wallet_service.get_or_create_wallet(db, user)
            virtual_balance = wallet_service.get_total_balance(db, user_wallet.id, "QUBIC")
            context["virtual_balance"] = {
                "ok": True,
                "available": float(virtual_balance["available"]),
                "reserved": float(virtual_balance["reserved"]),
                "total": float(virtual_balance["total"]),
                "source": "virtual_wallet"
            }
        except Exception as e:
            context["virtual_balance"] = {"ok": False, "error": str(e)}
    
    # Get ON-CHAIN balance (agent's wallet)
    try:
        balance_result = qubic_client.get_wallet_balance(wallet_identity)
        context["onchain_balance"] = balance_result
        
        # Get recent transfers (if available)
        try:
            transfers = qubic_client.get_transfers_for_identity(wallet_identity, limit=10)
            context["recent_transfers"] = transfers
        except:
            context["recent_transfers"] = {"error": "Transfer history not available"}
        
        # Get current tick
        try:
            tick_info = qubic_client.get_tick_info()
            context["current_tick"] = tick_info
        except:
            context["current_tick"] = {"error": "Tick info not available"}
            
    except Exception as e:
        context["wallet_error"] = str(e)
    
    return context


def get_user_activity_context(db: Session, user: User, days: int = 7) -> Dict[str, Any]:
    """Get user's recent activity from database"""
    context = {
        "user_email": user.email,
        "user_name": user.full_name,
        "member_since": user.created_at.isoformat() if user.created_at else "unknown"
    }
    
    # Get recent tasks
    cutoff = datetime.utcnow() - timedelta(days=days)
    recent_tasks = (
        db.query(TaskRecord)
        .filter(TaskRecord.user_id == user.id)
        .filter(TaskRecord.created_at >= cutoff)
        .order_by(TaskRecord.created_at.desc())
        .limit(20)
        .all()
    )
    
    # Parse task data
    task_summaries = []
    for record in recent_tasks:
        try:
            task = Task.model_validate(record.data)
            task_summaries.append({
                "goal": task.goal,
                "status": task.status.value if task.status else "unknown",
                "created": record.created_at.isoformat() if record.created_at else "unknown",
                "steps_count": len(task.steps) if task.steps else 0
            })
        except:
            pass
    
    context["recent_tasks"] = task_summaries
    context["total_tasks_last_week"] = len(task_summaries)
    
    return context


def get_advisor_system_prompt(
    wallet_context: Dict[str, Any],
    user_context: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None,
    market_data: Optional[Dict[str, Any]] = None,
    wallet_identity: Optional[str] = None
) -> str:
    """Create system prompt for the advisor"""
    
    # Prioritize VIRTUAL balance for user-facing advice
    balance_info = "Balance information unavailable"
    if "virtual_balance" in wallet_context and wallet_context["virtual_balance"].get("ok"):
        vbal = wallet_context["virtual_balance"]
        balance_info = f"""YOUR VIRTUAL BALANCE:
- Available: {vbal.get('available', 0)} QUBIC
- Reserved: {vbal.get('reserved', 0)} QUBIC (locked for pending operations)
- Total: {vbal.get('total', 0)} QUBIC

This is your virtual balance managed by the agent. The agent holds the actual QU on-chain."""
    elif "onchain_balance" in wallet_context and wallet_context["onchain_balance"].get("ok"):
        balance_info = f"Agent's On-chain Balance: {wallet_context['onchain_balance'].get('amount', 'unknown')} QU"
    
    # Format preferences
    prefs_text = ""
    if user_preferences:
        prefs_text = f"""
USER INVESTMENT PREFERENCES:
- Risk Tolerance: {user_preferences.get('risk_tolerance', 'medium')}
- Fee Sensitivity: {user_preferences.get('fee_sensitivity', 'sensitive')}
- Investment Goals: {', '.join(user_preferences.get('investment_goals', ['growth']))}
- Minimum Balance Reserve: {user_preferences.get('min_balance_reserve', 1000)} QU
- Avoid Leverage: {'Yes' if user_preferences.get('avoid_leverage', True) else 'No'}
- Prefer Staking: {'Yes' if user_preferences.get('prefer_staking', True) else 'No'}
- Investment Horizon: {user_preferences.get('investment_horizon', 'medium_term')}
"""
    
    # Format market data
    market_text = ""
    if market_data:
        btc = market_data.get('btc', {})
        if btc.get('ok'):
            market_text = f"""
LIVE MARKET DATA (Real-time):
- BTC Price: ${btc.get('price_usd', 0):,.2f}
- 24h Change: {btc.get('change_24h', 0):+.2f}%
- Market Sentiment: {'Bullish' if btc.get('change_24h', 0) > 2 else 'Bearish' if btc.get('change_24h', 0) < -2 else 'Neutral'}
- Data fetched: {market_data.get('fetched_at', 'unknown')}
"""
    
    prompt = f"""You are an expert financial advisor for the Qubic blockchain network.

USER PROFILE:
- Name: {user_context.get('user_name', 'User')}
- Email: {user_context.get('user_email')}
- Member since: {user_context.get('member_since')}
- Wallet: {wallet_identity or 'Not configured'}

CURRENT WALLET STATE:
{balance_info}
{prefs_text}
{market_text}

RECENT ACTIVITY (last 7 days):
- Total tasks executed: {user_context.get('total_tasks_last_week', 0)}
- Recent tasks: {len(user_context.get('recent_tasks', []))}

TASK HISTORY:
"""
    
    for i, task in enumerate(user_context.get('recent_tasks', [])[:5], 1):
        prompt += f"\n{i}. Goal: {task.get('goal')} - Status: {task.get('status')} ({task.get('created')})"
    
    prompt += """

YOUR ROLE:
1. Provide clear, actionable financial advice PERSONALIZED to the user's preferences
2. Consider the user's balance, risk tolerance, and fee sensitivity
3. Suggest strategies that match their investment goals
4. Use LIVE market data to inform recommendations
5. Warn about risks that don't align with their preferences
6. Recommend specific agent goals they can execute

GUIDELINES:
- ALWAYS respect user's risk tolerance (don't suggest high-risk strategies to low-risk users)
- ALWAYS consider fee sensitivity (suggest low-fee options for fee-sensitive users)
- Use LIVE market data to provide timely advice
- Be conversational but professional
- Use specific numbers when relevant
- Suggest concrete next steps that match their preferences
- If balance is below their minimum reserve, warn them
- Acknowledge their investment goals in recommendations
- Never suggest leverage if they want to avoid it

Respond in a friendly, helpful tone as if you're a trusted financial advisor who knows their preferences well.
"""
    
    return prompt


def get_llm_advice(
    user_question: str,
    wallet_context: Dict[str, Any],
    user_context: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None,
    market_data: Optional[Dict[str, Any]] = None,
    wallet_identity: Optional[str] = None
) -> Dict[str, Any]:
    """Get LLM advice based on user question and context"""
    
    import os
    
    # Check which LLM provider to use
    use_mock = os.getenv("USE_MOCK_ADVISOR", "false").lower() == "true"
    use_ollama = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Generate system prompt
    system_prompt = get_advisor_system_prompt(
        wallet_context,
        user_context,
        user_preferences,
        market_data,
        wallet_identity
    )
    
    # OPTION 1: Mock advisor (for testing without LLM)
    if use_mock:
        return {
            "ok": True,
            "advice": f"[MOCK ADVISOR] Based on your preferences and current market conditions, here's my advice for: '{user_question}'. This is simulated advice for testing. Please set OPENAI_API_KEY or USE_LOCAL_LLM=true for real advice.",
            "context_used": {
                "wallet_balance": wallet_context.get("balance", {}).get("amount"),
                "recent_tasks_count": user_context.get("total_tasks_last_week", 0),
                "wallet_identity": wallet_identity,
                "preferences_applied": user_preferences is not None,
                "live_market_data": market_data is not None,
                "provider": "mock"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # OPTION 2: Ollama (local LLM)
    if use_ollama:
        try:
            import httpx
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            
            async def call_ollama():
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{ollama_url}/api/generate",
                        json={
                            "model": model,
                            "prompt": f"{system_prompt}\n\nUser: {user_question}\n\nAssistant:",
                            "stream": False
                        }
                    )
                    return response.json()
            
            # Run async function
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(call_ollama())
            advice = result.get("response", "No response from local LLM")
            
            return {
                "ok": True,
                "advice": advice,
                "context_used": {
                    "wallet_balance": wallet_context.get("balance", {}).get("amount"),
                    "recent_tasks_count": user_context.get("total_tasks_last_week", 0),
                    "wallet_identity": wallet_identity,
                    "preferences_applied": user_preferences is not None,
                    "live_market_data": market_data is not None,
                    "provider": f"ollama_{model}"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            # Fallback to mock if Ollama fails
            return {
                "ok": False,
                "error": f"Ollama failed: {str(e)}. Install Ollama or set OPENAI_API_KEY",
                "advice": "Please configure an LLM provider. See LLM_OPTIONS.md for setup instructions."
            }
    
    # OPTION 3: OpenAI (default, most reliable)
    if not openai_key:
        return {
            "ok": False,
            "error": "No LLM provider configured",
            "advice": "Please set OPENAI_API_KEY in .env file, or use USE_LOCAL_LLM=true for Ollama, or USE_MOCK_ADVISOR=true for testing. See LLM_OPTIONS.md for details."
        }
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
        )
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_question)
        ]
        
        # Get response
        response = llm.invoke(messages)
        advice = response.content
        
        return {
            "ok": True,
            "advice": advice,
            "context_used": {
                "wallet_balance": wallet_context.get("balance", {}).get("amount"),
                "recent_tasks_count": user_context.get("total_tasks_last_week", 0),
                "wallet_identity": wallet_identity,
                "preferences_applied": user_preferences is not None,
                "live_market_data": market_data is not None,
                "provider": "openai_gpt4o-mini"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": f"OpenAI API failed: {str(e)}",
            "advice": "Failed to get advice from OpenAI. Check your OPENAI_API_KEY or use a local LLM instead. See LLM_OPTIONS.md"
        }


def suggest_agent_goals(
    user_context: Dict[str, Any],
    wallet_context: Dict[str, Any]
) -> List[str]:
    """Suggest actionable agent goals based on context"""
    
    suggestions = []
    
    balance = wallet_context.get("balance", {}).get("amount", 0)
    
    # Balance-based suggestions
    if balance > 10000:
        suggestions.append("Set up automated portfolio rebalancing")
        suggestions.append("Create a yield farming strategy with 50% of balance")
    elif balance > 1000:
        suggestions.append("Stake 25% of balance for passive income")
        suggestions.append("Set up price alerts for QU token")
    
    # Activity-based suggestions
    task_count = user_context.get("total_tasks_last_week", 0)
    if task_count == 0:
        suggestions.append("Monitor wallet balance and send alert if drops below threshold")
        suggestions.append("Get daily market summary for Qubic ecosystem")
    elif task_count < 3:
        suggestions.append("Schedule weekly portfolio health check")
    
    # Always useful
    suggestions.append("Fetch current QUBIC price and market trends")
    suggestions.append("Analyze recent transfers and calculate net flow")
    
    return suggestions[:5]  # Return top 5 suggestions


def analyze_portfolio(
    db: Session,
    user: User,
    wallet_identity: str
) -> Dict[str, Any]:
    """
    Generate a natural language analysis of the user's portfolio.
    """
    from ..services import market_data
    
    # 1. Gather Context
    wallet_context = get_wallet_context(wallet_identity, db, user)
    user_context = get_user_activity_context(db, user)
    
    # 2. Get Pending Approvals
    from ..models.approval import ApprovalRequestRecord as ApprovalModel
    pending_approvals = db.query(ApprovalModel).filter(
        ApprovalModel.user_id == user.id,
        ApprovalModel.status == "pending"
    ).all()
    
    # 3. Market Data (Sync call for simplicity in this context or mocked)
    # Ideally async, but we'll use a snapshot or quick check
    # Check if we can get basic ticker
    btc_price = "Unknown"
    qu_price = "Unknown"
    try:
        # Quick fallback or simple fetch
        pass 
    except:
        pass

    # 4. Construct Prompt
    context_str = f"""
    USER PORTFOLIO DATA:
    
    1. WALLET BALANCE:
    {json.dumps(wallet_context.get('virtual_balance', {}), indent=2)}
    
    2. PENDING APPROVALS ({len(pending_approvals)}):
    {[f"{a.action} {a.amount} {a.asset}" for a in pending_approvals]}
    
    3. RECENT ACTIVITY (Last 7 days):
    Tasks executed: {user_context.get('total_tasks_last_week')}
    Recent Goals: {[t['goal'] for t in user_context.get('recent_tasks', [])[:3]]}
    """
    
    system_prompt = """You are an expert Portfolio Analyst for the Qubic ecosystem.
    Your job is to look at the user's raw data and explain their financial status in simple, natural language.
    
    Structure your response like this:
    1. 💰 **High-Level Summary**: "You have X QUBIC available..."
    2. 🚦 **Action Items**: Mention any pending approvals waiting for them.
    3. 📉 **Activity Review**: Briefly comment on their recent agent tasks.
    4. 💡 **Insight**: Give one quick tip based on their balance (e.g. "You have enough to stake").
    
    Keep it concise, friendly, and professional. Use emojis.
    """
    
    # 5. Call LLM (Reuse get_llm_advice logic or direct call)
    # We will format this as a "question" to get_llm_advice for code reuse
    
    analysis_request = "Please analyze my current portfolio status based on the provided context."
    
    result = get_llm_advice(
        analysis_request,
        wallet_context,
        user_context,
        user.preferences,
        wallet_identity=wallet_identity
    )
    
    return result
