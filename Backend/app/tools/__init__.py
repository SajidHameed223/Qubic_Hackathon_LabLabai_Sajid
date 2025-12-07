# app/tools/__init__.py

"""
Tool Registry for Qubic Autopilot Agent

This module provides a registry of executable tools that the AI planner
can discover and use to accomplish complex DeFi, RWA, and infrastructure tasks.
"""

from .registry import ToolRegistry, Tool
from . import defi_tools
from . import rwa_tools
from . import infrastructure_tools

# Initialize the global registry
registry = ToolRegistry()

# Register all tools
defi_tools.register_tools(registry)
rwa_tools.register_tools(registry)
infrastructure_tools.register_tools(registry)

__all__ = ["registry", "Tool", "ToolRegistry"]
