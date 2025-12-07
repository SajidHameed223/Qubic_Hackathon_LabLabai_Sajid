# app/services/ai_planner.py

import os
import json
from typing import List, Dict, Any
from uuid import uuid4

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from ..models.task import Step, StepType


# ----------------------------------------------------
# 1. Define the state for LangGraph
# ----------------------------------------------------

class PlannerState(TypedDict):
    goal: str
    plan: List[Dict[str, Any]]


# ----------------------------------------------------
# 2. Configure OpenAI model
# ----------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",   # cheap and powerful
    temperature=0.1,
    api_key=os.environ.get("OPENAI_API_KEY"),
)


# ----------------------------------------------------
# 3. Planner node (calls OpenAI)
# ----------------------------------------------------

def planner_node(state: PlannerState) -> PlannerState:
    goal = state["goal"]
    
    # Import tool registry to get available tools
    from ..tools import registry
    
    # Get all tools organized by category
    all_tools = registry.get_all_tools()
    
    # Build comprehensive tool catalog for LLM
    tool_catalog = []
    for category, tools in all_tools.items():
        tool_catalog.append(f"\n**{category.upper()} TOOLS:**")
        for tool in tools[:5]:  # Show top 5 per category
            tool_catalog.append(f"  • {tool.name}: {tool.description}")
    
    tool_catalog_text = "\n".join(tool_catalog)
    total_tools = sum(len(tools) for tools in all_tools.values())

    system_prompt = (
        "You are an AI agent planner with access to 50+ DeFi, RWA, and Infrastructure tools.\n"
        "Your job is to break down user goals into executable steps using REAL TOOLS.\n\n"
        
        f"=== AVAILABLE TOOLS ({total_tools} total) ===\n"
        f"{tool_catalog_text}\n"
        "...and many more! Use TOOL_EXECUTION to access any tool.\n\n"
        
        "=== PLANNING RULES ===\n"
        "1. PREFER TOOL_EXECUTION over generic step types\n"
        "2. Match user intent to the most appropriate tool\n"
        "3. Break complex goals into multiple tool calls\n"
        "4. Use descriptive tool_params based on the user's goal\n\n"
        
        "=== STEP TYPES ===\n"
        "• TOOL_EXECUTION: Execute a registered tool (PREFERRED!)\n"
        "• QUBIC_TX: Direct blockchain transaction (only if no tool exists)\n"
        "• QUBIC_ORACLE: Fetch on-chain data\n"
        "• AI_PLAN: Complex reasoning\n"
        "• HTTP_REQUEST: External API calls\n"
        "• LOG_ONLY: Information logging\n\n"
        
        "=== TOOL_EXECUTION FORMAT ===\n"
        "{\n"
        '  "type": "TOOL_EXECUTION",\n'
        '  "description": "Human readable description",\n'
        '  "params": {\n'
        '    "tool_name": "exact_tool_name",\n'
        '    "tool_params": {\n'
        '      "param1": "value1",\n'
        '      "param2": "value2"\n'
        '    }\n'
        '  }\n'
        "}\n\n"
        
        "=== EXAMPLES ===\n"
        'Goal: "Swap 500 QUBIC to USDT"\n'
        "→ [\n"
        '  {\n'
        '    "type": "TOOL_EXECUTION",\n'
        '    "description": "Execute swap on DEX",\n'
        '    "params": {\n'
        '      "tool_name": "execute_swap",\n'
        '      "tool_params": {\n'
        '        "from_token": "QUBIC",\n'
        '        "to_token": "USDT",\n'
        '        "amount": 500\n'
        '      }\n'
        '    }\n'
        '  }\n'
        "]\n\n"
        
        'Goal: "Open leveraged long position on BTC"\n'
        "→ [\n"
        '  {\n'
        '    "type": "TOOL_EXECUTION",\n'
        '    "description": "Open perpetual position",\n'
        '    "params": {\n'
        '      "tool_name": "open_perp_position",\n'
        '      "tool_params": {\n'
        '        "market": "BTC-USD",\n'
        '        "side": "long",\n'
        '        "leverage": 3,\n'
        '        "margin": 1000\n'
        '      }\n'
        '    }\n'
        '  }\n'
        "]\n\n"
        
        'Goal: "Stake 1000 QUBIC"\n'
        "→ [\n"
        '  {\n'
        '    "type": "TOOL_EXECUTION",\n'
        '    "description": "Stake QUBIC for rewards",\n'
        '    "params": {\n'
        '      "tool_name": "stake_tokens",\n'
        '      "tool_params": {\n'
        '        "token": "QUBIC",\n'
        '        "amount": 1000,\n'
        '        "duration": 30\n'
        '      }\n'
        '    }\n'
        '  }\n'
        "]\n\n"
        
        "Return ONLY valid JSON:\n"
        '{ "steps": [ {...}, {...} ] }'
    )

    user_prompt = (
        f"Goal: {goal}\n\n"
        "Generate a plan using TOOL_EXECUTION steps. "
        "Match tools to the user's intent. "
        "Return valid JSON."
    )

    resp = llm.invoke([
        ("system", system_prompt),
        ("user", user_prompt),
    ])

    raw = resp.content

    try:
        obj = json.loads(raw)
        steps = obj.get("steps", [])
        if not isinstance(steps, list):
            raise ValueError("steps is not a list")
    except Exception as e:
        print("❌ OpenAI JSON parse failed:", e)
        print("Raw LLM Output:", raw)
        print("⚠️ Falling back to static planner.")

        # STATIC FALLBACK
        steps = [
            {
                "type": "AI_PLAN",
                "description": "Derive execution plan from goal using AI",
                "params": {"goal": goal},
            },
            {
                "type": "QUBIC_ORACLE",
                "description": "Fetch relevant on-chain / oracle data",
                "params": {"goal": goal},
            },
            {
                "type": "QUBIC_TX",
                "description": "Execute Qubic transaction",
                "params": {"goal": goal},
            },
            {
                "type": "HTTP_REQUEST",
                "description": "Notify external tools",
                "params": {"goal": goal},
            },
            {
                "type": "LOG_ONLY",
                "description": "Summarize outcome",
                "params": {"goal": goal},
            },
        ]

    return {"goal": goal, "plan": steps}


# ----------------------------------------------------
# 4. Build LangGraph
# ----------------------------------------------------

builder = StateGraph(PlannerState)
builder.add_node("planner", planner_node)
builder.set_entry_point("planner")
builder.add_edge("planner", END)

planner_graph = builder.compile()


# ----------------------------------------------------
# 5. Public API functions (used by task_engine.py)
# ----------------------------------------------------

def generate_plan_from_goal(goal: str) -> List[Dict[str, Any]]:
    """
    Runs LangGraph → OpenAI → returns dict list of steps.
    """
    result: PlannerState = planner_graph.invoke({"goal": goal})
    return result["plan"]


def build_steps_from_plan(plan: List[Dict[str, Any]]) -> List[Step]:
    """
    Convert dict steps → Step Pydantic objects.
    """
    steps: List[Step] = []

    for item in plan:
        # Normalize type string
        type_str = str(item.get("type", "LOG_ONLY"))
        try:
            step_type = StepType(type_str)
        except ValueError:
            step_type = StepType.LOG_ONLY

        steps.append(
            Step(
                id=str(uuid4()),
                description=item.get("description", ""),
                type=step_type,
                params=item.get("params", {}) or {},
            )
        )

    return steps