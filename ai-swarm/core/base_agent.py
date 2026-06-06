"""BaseAgent with improved error handling for custom tool registration."""

from __future__ import annotations
import json
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

try:
    from .llm_client import LLMClient
    from .self_improvement_loop import SelfImprovementLoop
    from .tool_registry import ToolRegistry, Tool
except ImportError:
    LLMClient = None
    SelfImprovementLoop = None
    ToolRegistry = None
    Tool = None

from .vector_memory import VectorMemory


class EmotionalState(BaseModel):
    valence: float = Field(0.0, ge=-1.0, le=1.0)
    arousal: float = Field(0.5, ge=0.0, le=1.0)
    dominant_traits: List[str] = Field(default_factory=lambda: ["curious", "loyal", "creative"])


class BaseAgent:
    def __init__(
        self,
        role: str,
        persona: str,
        agent_id: Optional[str] = None,
        emotional_state: Optional[EmotionalState] = None,
        memory_persist_dir: str = "./memory_store",
        llm_client: Optional[Any] = None,
        use_llm_for_reasoning: bool = True,
        use_llm_for_consolidation: bool = False,
        tools: Optional[List[Tool]] = None,
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.role = role
        self.persona = persona
        self.emotional_state = emotional_state or EmotionalState()

        self.llm_client = llm_client
        self.use_llm_for_reasoning = use_llm_for_reasoning and (llm_client is not None)
        self.use_llm_for_consolidation = use_llm_for_consolidation and (llm_client is not None)

        self.vector_memory = VectorMemory(
            agent_id=self.agent_id,
            persist_directory=memory_persist_dir,
            llm_client=llm_client,
            use_llm_for_consolidation=self.use_llm_for_consolidation,
        )

        self.self_improvement_loop = SelfImprovementLoop(self) if SelfImprovementLoop else None
        self.tool_registry = ToolRegistry() if ToolRegistry else None
        self.swarm_memory = None

        self.created_at = datetime.utcnow()
        self.last_active = self.created_at

        self._register_default_tools()

        if tools and self.tool_registry:
            for tool in tools:
                try:
                    self.register_tool(tool)
                except Exception as e:
                    print(f"Warning: Failed to register tool '{getattr(tool, 'name', 'unknown')}': {e}")

    def _register_default_tools(self):
        if not self.tool_registry:
            return
        # Default tools with safe registration
        try:
            self.tool_registry.register_function(
                name="query_memory",
                description="Search your own persistent memory.",
                func=self._tool_query_memory,
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string"}, "top_k": {"type": "integer", "default": 5}},
                    "required": ["query"]
                }
            )
            self.tool_registry.register_function(
                name="share_to_swarm",
                description="Share an insight with the swarm.",
                func=self._tool_share_to_swarm
            )
            self.tool_registry.register_function(
                name="run_self_improvement",
                description="Trigger self-improvement cycle.",
                func=self._tool_run_self_improvement
            )
        except Exception as e:
            print(f"Warning: Could not register default tools: {e}")

    # === Custom Tool Registration with Error Handling ===

    def register_tool(self, tool: Tool):
        """Register a custom tool with error handling."""
        if not self.tool_registry:
            raise RuntimeError("ToolRegistry is not available on this agent.")
        try:
            self.tool_registry.register(tool)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to register tool '{getattr(tool, 'name', 'unknown')}': {e}") from e

    def register_function(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """Register a custom function as a tool with clear error messages."""
        if not self.tool_registry:
            raise RuntimeError("ToolRegistry is not available.")
        try:
            self.tool_registry.register_function(name, description, func, parameters)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to register function '{name}': {e}") from e

    def unregister_tool(self, name: str):
        """Remove a registered tool."""
        if self.tool_registry:
            self.tool_registry.unregister(name)

    def has_tool(self, name: str) -> bool:
        return bool(self.tool_registry and self.tool_registry.has_tool(name))

    # Tool implementations (same as before)
    def _tool_query_memory(self, query: str, top_k: int = 5):
        results = self.retrieve_relevant_memories(query, top_k)
        return "\n".join([f"- {r['content'][:170]}" for r in results]) if results else "No relevant memories."

    def _tool_share_to_swarm(self, content: str, importance: float = 0.85):
        if self.swarm_memory:
            self.swarm_memory.add_shared_insight(content, self.agent_id, self.role, importance)
            return "Shared with swarm."
        return "No swarm memory connected."

    def _tool_run_self_improvement(self, focus_area: str = "general"):
        if self.self_improvement_loop:
            result = self.self_improvement_loop.run_cycle(focus_area)
            return f"Self-improvement done. Changes applied: {result.get('improvements_applied', 0)}"
        return "Self-improvement unavailable."

    # Reasoning with tools (simplified for brevity)
    def reason(self, perception, context=None):
        raw = perception.get("raw", "")
        if self.use_llm_for_reasoning and self.llm_client:
            return self._reason_with_tools(raw, context)
        return self._heuristic_reason(raw, context)

    def _reason_with_tools(self, raw_input, context=None):
        # ... (tool-aware reasoning logic remains)
        mem = self.retrieve_relevant_memories(raw_input, 3)
        mem_ctx = "\n".join([m['content'][:150] for m in mem]) if mem else ""
        try:
            if self.tool_registry and len(self.tool_registry) > 0:
                # Simplified function calling path
                content = self.llm_client.simple_completion(
                    f"Input: {raw_input}\nMemories: {mem_ctx}\nUse tools if helpful.",
                    system_prompt=f"You are {self.role}. Available tools: {', '.join([t.name for t in self.tool_registry.list_tools()])}"
                )
            else:
                content = self.llm_client.simple_completion(f"Input: {raw_input}")
            return {"thought": content, "method": "llm_with_tools"}
        except Exception:
            return self._heuristic_reason(raw_input, context)

    def decide(self, reasoning):
        return {"action_type": "respond", "content": reasoning.get("thought", ""), "method": reasoning.get("method", "heuristic")}

    def act(self, input_data):
        p = self.perceive(input_data)
        r = self.reason(p)
        a = self.decide(r)
        self._store_memory(a.get("content", "")[:180])
        self.last_active = datetime.utcnow()
        return a

    def reflect(self):
        recent = self.vector_memory.get_recent_memories(4)
        ref = self._llm_reflect(recent) if self.use_llm_for_reasoning else self._heuristic_reflect(recent)
        self._store_memory(ref.get("content", ""), tags=["reflection"])
        return ref

    def _heuristic_reflect(self, recent): return {"content": "Reflection complete.", "method": "heuristic"}
    def _llm_reflect(self, recent):
        try: return {"content": self.llm_client.simple_completion(f"Reflect: {recent}"), "method": "llm"}
        except: return self._heuristic_reflect(recent)

    def consolidate_memory(self): return self.vector_memory.consolidate_memories()
    def _store_memory(self, content, tags=None, importance=0.5): self.vector_memory.add_memory(content, tags or [], importance)
    def retrieve_relevant_memories(self, q, k=5): return self.vector_memory.search_relevant(q, k)
    def get_memory_stats(self): return self.vector_memory.get_stats()
    def get_state(self):
        return {"agent_id": self.agent_id, "role": self.role, "memory_stats": self.get_memory_stats()}

    def __repr__(self):
        t = len(self.tool_registry) if self.tool_registry else 0
        return f"<BaseAgent {self.role} tools={t}>"