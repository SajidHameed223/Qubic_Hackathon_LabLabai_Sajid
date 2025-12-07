# app/routers/tools.py

"""
Tools API Router

Provides endpoints to discover and interact with registered tools.
"""

from fastapi import APIRouter
from typing import List, Dict, Any
from ..tools import registry
from ..tools.registry import ToolCategory

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/list")
def list_all_tools() -> List[Dict[str, Any]]:
    """
    List all available tools in the registry.
    
    Returns tool metadata including name, category, description, and parameters.
    """
    tools = registry.list_all()
    return [
        {
            "name": tool.name,
            "category": tool.category.value,
            "description": tool.description,
            "parameters": tool.parameters,
            "examples": tool.examples or []
        }
        for tool in tools
    ]


@router.get("/categories")
def list_categories() -> List[str]:
    """List all tool categories"""
    return [cat.value for cat in ToolCategory]


@router.get("/category/{category}")
def list_tools_by_category(category: str) -> List[Dict[str, Any]]:
    """
    List tools in a specific category.
    
    Categories: defi, rwa, infrastructure, oracle, governance
    """
    try:
        cat = ToolCategory(category)
        tools = registry.list_by_category(cat)
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "examples": tool.examples or []
            }
            for tool in tools
        ]
    except ValueError:
        return {"error": f"Invalid category: {category}"}


@router.get("/descriptions")
def get_tool_descriptions() -> Dict[str, str]:
    """
    Get formatted tool descriptions for AI planner.
    
    This is what the AI sees when planning tasks.
    """
    return {
        "descriptions": registry.get_tool_descriptions()
    }


@router.post("/execute/{tool_name}")
def execute_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Directly execute a tool by name.
    
    Useful for testing tools individually.
    """
    tool = registry.get(tool_name)
    
    if not tool:
        available = [t.name for t in registry.list_all()]
        return {
            "ok": False,
            "error": f"Tool '{tool_name}' not found",
            "available_tools": available
        }
    
    result = tool.execute(params)
    return result


@router.get("/stats")
def get_tool_stats() -> Dict[str, Any]:
    """Get statistics about registered tools"""
    all_tools = registry.list_all()
    
    stats_by_category = {}
    for cat in ToolCategory:
        count = len(registry.list_by_category(cat))
        if count > 0:
            stats_by_category[cat.value] = count
    
    return {
        "total_tools": len(all_tools),
        "by_category": stats_by_category,
        "categories": [cat.value for cat in ToolCategory]
    }
