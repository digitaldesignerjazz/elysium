"""ToolRegistry and base Tool support for function calling in the Elysium AI Agent Swarm Framework.

Enables agents to use tools via LLM function calling (Grok/xAI compatible).
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional


class Tool:
    """Represents a callable tool that agents can use."""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {
            "type": "object",
            "properties": {},
            "required": []
        }

    def to_openai_tool(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }

    def __call__(self, **kwargs) -> Any:
        return self.func(**kwargs)


class ToolRegistry:
    """Registry of tools available to an agent or swarm."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def register_function(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        tool = Tool(name=name, description=description, func=func, parameters=parameters)
        self.register(tool)
        return tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_tool() for tool in self._tools.values()]

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        tool = self.get_tool(name)
        if tool:
            return tool(**arguments)
        raise ValueError(f"Tool '{name}' not found")

    def __len__(self):
        return len(self._tools)

    def __repr__(self):
        return f"<ToolRegistry tools={list(self._tools.keys())}>"