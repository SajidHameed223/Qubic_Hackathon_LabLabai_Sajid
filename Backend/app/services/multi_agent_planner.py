from typing import TypedDict, List, Dict, Any, Annotated, Optional
import operator
import json
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.config import settings
from app.tools import registry
from app.tools.infrastructure_tools import fetch_price_feed

# --- 1. Define the State ---
class AgentState(TypedDict):
    goal: str
    user_risk_profile: str  # "conservative", "moderate", "aggressive"
    market_data: str        # Output from Market Data Node
    research_data: str      # Output from Researcher Node
    analysis: str           # Output from Analyst
    risk_assessment: str    # Output from Risk Manager
    plan: List[Dict[str, Any]] # Final steps
    review_status: str      # "APPROVED" or "REJECTED"
    review_feedback: str    # Feedback from Reviewer
    retry_count: int        # Number of retries
    messages: Annotated[List[BaseMessage], operator.add]

# --- 2. Initialize LLM ---
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=settings.openai_api_key
)

# --- 3. Define Agent Nodes ---

def market_data_node(state: AgentState):
    """
    Fetches real-time market data for assets mentioned in the goal.
    """
    goal = state["goal"]
    print(f"📊 Market Data Node fetching data for: {goal}")
    
    # Simple keyword extraction (could be LLM-based)
    assets = []
    for asset in ["QUBIC", "BTC", "ETH", "USDT", "SOL"]:
        if asset in goal.upper():
            assets.append(asset)
    
    if not assets:
        assets = ["QUBIC"] # Default
        
    data = []
    for asset in assets:
        # Call the actual tool
        feed = fetch_price_feed({"asset": asset})
        data.append(f"{asset}: ${feed['price']} (Source: {feed['source']})")
        
    return {"market_data": "\n".join(data)}

def researcher_node(state: AgentState):
    """
    Simulates researching web news and sentiment.
    """
    goal = state["goal"]
    print(f"🌍 Researcher Node searching news for: {goal}")
    
    # In a real app, use Tavily or Google Search API here
    # For now, we simulate based on the goal context
    
    system_prompt = (
        "You are a Crypto Researcher. Simulate a web search for the assets in the goal.\n"
        "Provide a brief summary of recent news and market sentiment (Bullish/Bearish/Neutral).\n"
        "Be realistic based on current market trends."
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=goal)
    ])
    
    return {"research_data": response.content}

def analyst_node(state: AgentState):
    """
    The Analyst looks at the goal, market data, and research to determine strategy.
    """
    goal = state["goal"]
    market_data = state.get("market_data", "No data")
    research_data = state.get("research_data", "No news")
    
    print(f"🕵️ Analyst processing with data...")
    
    system_prompt = (
        "You are a Senior DeFi Analyst. Analyze the user's goal.\n"
        f"=== MARKET DATA ===\n{market_data}\n\n"
        f"=== NEWS & SENTIMENT ===\n{research_data}\n\n"
        "Identify the financial intent and recommend a strategy.\n"
        "Consider the market conditions in your analysis."
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=goal)
    ])
    
    return {"analysis": response.content}

def risk_manager_node(state: AgentState):
    """
    The Risk Manager evaluates the strategy against the user's risk profile.
    """
    analysis = state["analysis"]
    risk_profile = state.get("user_risk_profile", "moderate")
    print(f"🛡️ Risk Manager evaluating for {risk_profile} profile...")
    
    system_prompt = (
        f"You are a Risk Manager. The user has a '{risk_profile}' risk profile.\n"
        "Review the Analyst's strategy:\n"
        f"{analysis}\n\n"
        "Identify any risks (impermanent loss, liquidation, smart contract risk).\n"
        "If the strategy is too risky for the profile, suggest modifications.\n"
        "Output your risk assessment and any required constraints."
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Assess this strategy.")
    ])
    
    return {"risk_assessment": response.content}

def planner_node(state: AgentState):
    """
    The Planner converts the approved strategy into executable tool steps.
    """
    goal = state["goal"]
    analysis = state["analysis"]
    risk_assessment = state["risk_assessment"]
    review_feedback = state.get("review_feedback", "")
    current_retries = state.get("retry_count", 0)
    
    print(f"🏗️ Planner generating tool steps (Attempt {current_retries + 1})...")
    
    # Get tools
    all_tools = registry.get_all_tools()
    tool_catalog = []
    for category, tools in all_tools.items():
        tool_catalog.append(f"\n**{category.upper()} TOOLS:**")
        for tool in tools[:5]:
            tool_catalog.append(f"  • {tool.name}: {tool.description}")
    tool_text = "\n".join(tool_catalog)

    system_prompt = (
        "You are the Lead Architect. Create an execution plan based on the analysis and risk constraints.\n"
        "You MUST use the available tools.\n\n"
        f"=== ANALYSIS ===\n{analysis}\n\n"
        f"=== RISK ASSESSMENT ===\n{risk_assessment}\n\n"
        f"=== AVAILABLE TOOLS ===\n{tool_text}\n\n"
    )
    
    if review_feedback:
        system_prompt += f"=== PREVIOUS REVIEW FEEDBACK (FIX THESE ISSUES) ===\n{review_feedback}\n\n"

    system_prompt += (
        "Generate a JSON object with a 'steps' key. Do not include markdown formatting.\n"
        "Example:\n"
        '{ "steps": [ { "type": "TOOL_EXECUTION", "params": { "tool_name": "stake_tokens", "tool_params": {"amount": 10} } } ] }'
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Goal: {goal}")
    ])
    
    # Parse JSON
    try:
        content = response.content
        # Clean markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        content = content.strip()
        
        data = json.loads(content)
        return {"plan": data.get("steps", []), "retry_count": current_retries + 1}
    except Exception as e:
        print(f"❌ Planner JSON error: {e}")
        print(f"Raw content: {response.content}")
        return {"plan": [], "retry_count": current_retries + 1}

def reviewer_node(state: AgentState):
    """
    The Reviewer checks the plan for safety and correctness.
    """
    plan = state["plan"]
    risk_profile = state.get("user_risk_profile", "moderate")
    print("🧐 Reviewer checking plan...")
    
    if not plan:
        return {"review_status": "REJECTED", "review_feedback": "Plan is empty."}

    system_prompt = (
        f"You are a Senior Code Reviewer. The user has a '{risk_profile}' risk profile.\n"
        "Review the following execution plan JSON.\n"
        "Check for:\n"
        "1. Logical errors (e.g., using a tool with wrong params)\n"
        "2. Safety violations (e.g., leverage too high for profile)\n"
        "3. Missing steps (e.g., borrowing without collateral)\n\n"
        "If the plan is good, output ONLY 'APPROVED'.\n"
        "If there are issues, output 'REJECTED: [Reason]'."
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=json.dumps(plan, indent=2))
    ])
    
    content = response.content.strip()
    if "APPROVED" in content.upper():
        return {"review_status": "APPROVED", "review_feedback": ""}
    else:
        return {"review_status": "REJECTED", "review_feedback": content}

# --- 4. Build the Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("market_data", market_data_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("risk_manager", risk_manager_node)
workflow.add_node("planner", planner_node)
workflow.add_node("reviewer", reviewer_node)

# Define flow
# Parallel execution of data gathering
workflow.set_entry_point("market_data")
workflow.add_edge("market_data", "researcher") # Sequential for simplicity in this setup
workflow.add_edge("researcher", "analyst")

workflow.add_edge("analyst", "risk_manager")
workflow.add_edge("risk_manager", "planner")
workflow.add_edge("planner", "reviewer")

# Conditional edge for review
def check_review(state: AgentState):
    if state["review_status"] == "APPROVED":
        return END
    
    if state.get("retry_count", 0) > 3:
        print("⚠️ Max retries reached. Exiting with current plan.")
        return END
        
    return "planner" # Loop back to planner

workflow.add_conditional_edges(
    "reviewer",
    check_review,
    {END: END, "planner": "planner"}
)

# Compile
app = workflow.compile()

def run_multi_agent_plan(goal: str, user_risk_profile: str = "moderate") -> List[Dict[str, Any]]:
    """
    Entry point to run the multi-agent system.
    """
    initial_state = {
        "goal": goal,
        "user_risk_profile": user_risk_profile,
        "messages": [],
        "review_feedback": "",
        "retry_count": 0
    }
    
    # Increase recursion limit for loops
    config = {"recursion_limit": 20}
    
    result = app.invoke(initial_state, config=config)
    return result.get("plan", [])
