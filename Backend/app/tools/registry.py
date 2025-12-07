# app/tools/registry.py

from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass
from enum import Enum


class ToolCategory(str, Enum):
    """Categories of tools available to the agent"""
    DEFI = "defi"
    RWA = "rwa"
    INFRASTRUCTURE = "infrastructure"
    ORACLE = "oracle"
    GOVERNANCE = "governance"


@dataclass
class Tool:
    """
    Represents a single executable tool/primitive.
    
    The AI planner can discover these tools and include them in execution plans.
    """
    name: str
    category: ToolCategory
    description: str
    parameters: Dict[str, Any]  # JSON schema for parameters
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    examples: List[str] = None
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        try:
            result = self.handler(params)
            return {
                "ok": True,
                "tool": self.name,
                "result": result
            }
        except Exception as e:
            return {
                "ok": False,
                "tool": self.name,
                "error": str(e)
            }


class ToolRegistry:
    """
    Central registry of all available tools.
    
    The AI planner queries this registry to discover what actions it can take.
    """
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_all(self) -> List[Tool]:
        """List all registered tools"""
        return list(self.tools.values())
    
    def list_by_category(self, category: ToolCategory) -> List[Tool]:
        """List tools in a specific category"""
        return [t for t in self.tools.values() if t.category == category]
    
    def get_tool_descriptions(self) -> str:
        """
        Get a formatted string describing all tools.
        This is used by the AI planner to understand available actions.
        """
        lines = ["Available Tools:\n"]
        
        for category in ToolCategory:
            tools_in_cat = self.list_by_category(category)
            if tools_in_cat:
                lines.append(f"\n{category.value.upper()}:")
                for tool in tools_in_cat:
                    lines.append(f"  - {tool.name}: {tool.description}")
        
        return "\n".join(lines)
    
    def get_all_tools(self) -> Dict[ToolCategory, List[Tool]]:
        """
        Get all tools organized by category.
        Returns dict of category -> list of tools.
        """
        result = {}
        for category in ToolCategory:
            tools = self.list_by_category(category)
            if tools:
                result[category] = tools
        return result
