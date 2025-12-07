# app/services/tool_handler.py

"""
Tool Execution Handler

Handles execution of registered tools from the tool registry.
"""

from typing import Dict, Any
from ..models.task import Task, Step


def handle_tool_execution(task: Task, step: Step) -> Dict[str, Any]:
    """
    Execute a registered tool based on step parameters.
    
    Expected step.params:
      {
        "tool_name": "<name of tool from registry>",
        "tool_params": { <parameters for the tool> }
      }
    """
    from ..tools import registry
    
    tool_name = step.params.get("tool_name")
    tool_params = step.params.get("tool_params", {})
    
    if not tool_name:
        return {
            "ok": False,
            "error": "No tool_name specified in step params"
        }
    
    # Get the tool from registry
    tool = registry.get(tool_name)
    
    if not tool:
        available_tools = [t.name for t in registry.list_all()]
        return {
            "ok": False,
            "error": f"Tool '{tool_name}' not found in registry",
            "available_tools": available_tools
        }
    
    # Execute the tool
    result = tool.execute(tool_params)
    
    return result
