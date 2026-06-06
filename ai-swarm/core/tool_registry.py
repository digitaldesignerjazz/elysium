"""ToolRegistry with robust error handling for tool registration.

Provides clear errors for duplicate names, invalid tools, and missing fields.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional


class Tool:
    """Represents a callable tool that agents can use via function calling."""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        if not name or not isinstance(name, str):
            raise ValueError("Tool 'name' must be a non-empty string")
        if not description or not isinstance(description, str):
            raise ValueError("Tool 'description' must be a non-empty string")
        if not callable(func):
            raise ValueError("Tool 'func' must be callable")

        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {
            "type": "object",
            "properties": {},
            "required": []
        }

    def to_openai_tool(self) -> Dict[str, Any]:
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
    """Registry of tools available to agents. Includes validation and error handling."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a Tool object with validation and duplicate checking."""
        if not isinstance(tool, Tool):
            raise TypeError(f"Expected Tool instance, got {type(tool).__name__}")

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered. "
                f"Use a different name or call unregister('{tool.name}') first."
            )

        self._tools[tool.name] = tool

    def register_function(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """Register a function as a tool with validation."""
        try:
            tool = Tool(name=name, description=description, func=func, parameters=parameters)
            self.register(tool)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to register function '{name}': {e}") from e

    def unregister(self, name: str):
        """Remove a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered.")
        del self._tools[name]

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_tool() for tool in self._tools.values()]

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry.")
        try:
            return tool(**arguments)
        except Exception as e:
            raise RuntimeError(f"Error executing tool '{name}': {e}") from e

    def __len__(self):
        return len(self._tools)

    def __repr__(self):
        return f"<ToolRegistry tools={list(self._tools.keys())}>"