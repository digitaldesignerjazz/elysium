"""ToolRegistry with Automatic JSON Schema Inference.

Functions can now be registered without manually writing the full parameters schema.
"""

from __future__ import annotations
import inspect
from typing import Any, Callable, Dict, List, Optional, get_type_hints


class Tool:
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
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        if not isinstance(tool, Tool):
            raise TypeError(f"Expected Tool instance, got {type(tool).__name__}")
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered. "
                f"Use unregister('{tool.name}') first."
            )
        self._tools[tool.name] = tool

    def register_function(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """Register a function as a tool.

        If `parameters` is not provided, automatically infers a JSON schema
        from the function signature and type hints.
        """
        if parameters is None:
            parameters = self._infer_json_schema(func)

        try:
            tool = Tool(name=name, description=description, func=func, parameters=parameters)
            self.register(tool)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to register function '{name}': {e}") from e

    def _infer_json_schema(self, func: Callable) -> Dict[str, Any]:
        """Automatically generate a basic JSON schema from function signature."""
        try:
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
        except Exception:
            # Fallback if inspection fails
            return {"type": "object", "properties": {}, "required": []}

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            # Determine type
            annotation = type_hints.get(param_name, str)
            json_type = self._python_type_to_json_type(annotation)

            prop_schema = {"type": json_type}

            # Add description if possible (future improvement)
            if param.default != inspect.Parameter.empty:
                prop_schema["description"] = f"Default: {param.default}"
            else:
                required.append(param_name)

            properties[param_name] = prop_schema

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    def _python_type_to_json_type(self, py_type: Any) -> str:
        """Map common Python types to JSON Schema types."""
        origin = getattr(py_type, "__origin__", None)

        if py_type is str or origin is str:
            return "string"
        elif py_type is int or origin is int:
            return "integer"
        elif py_type is float or origin is float:
            return "number"
        elif py_type is bool or origin is bool:
            return "boolean"
        elif origin in (list, List):
            return "array"
        elif origin in (dict, Dict):
            return "object"
        else:
            return "string"  # Safe default

    def unregister(self, name: str):
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
            raise ValueError(f"Tool '{name}' not found.")
        try:
            return tool(**arguments)
        except Exception as e:
            raise RuntimeError(f"Error executing tool '{name}': {e}") from e

    def __len__(self):
        return len(self._tools)

    def __repr__(self):
        return f"<ToolRegistry tools={list(self._tools.keys())}>"