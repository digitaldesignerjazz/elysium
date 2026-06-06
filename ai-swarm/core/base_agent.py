"""BaseAgent with easy Custom Tool Registration support.

Users can now easily register their own custom tools.
"""

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
        tools: Optional[List[Tool]] = None,           # Custom tools at init
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

        # Register default tools first
        self._register_default_tools()

        # Register any custom tools passed at initialization
        if tools and self.tool_registry:
            for tool in tools:
                self.tool_registry.register(tool)

    def _register_default_tools(self):
        if not self.tool_registry:
            return

        self.tool_registry.register_function(
            name="query_memory",
            description="Search your own persistent memory for relevant experiences or insights.",
            func=self._tool_query_memory,
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        )

        self.tool_registry.register_function(
            name="share_to_swarm",
            description="Share an important insight with the entire swarm.",
            func=self._tool_share_to_swarm,
            parameters={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "importance": {"type": "number", "default": 0.85}
                },
                "required": ["content"]
            }
        )

        self.tool_registry.register_function(
            name="run_self_improvement",
            description="Run a self-improvement cycle focused on a specific area.",
            func=self._tool_run_self_improvement,
            parameters={
                "type": "object",
                "properties": {
                    "focus_area": {"type": "string"}
                }
            }
        )

    # --- Easy Custom Tool Registration Methods ---

    def register_tool(self, tool: Tool):
        """Register a custom Tool object."""
        if self.tool_registry:
            self.tool_registry.register(tool)

    def register_function(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """Convenient way to register a custom function as a tool."""
        if self.tool_registry:
            self.tool_registry.register_function(
                name=name,
                description=description,
                func=func,
                parameters=parameters
            )

    # Default tool implementations
    def _tool_query_memory(self, query: str, top_k: int = 5) -> str:
        results = self.retrieve_relevant_memories(query, top_k=top_k)
        return "\n".join([f"- {r['content'][:180]}" for r in results]) if results else "No relevant memories found."

    def _tool_share_to_swarm(self, content: str, importance: float = 0.85) -> str:
        if self.swarm_memory:
            self.swarm_memory.add_shared_insight(
                content=content, source_agent_id=self.agent_id, source_agent_role=self.role, importance=importance
            )
            return "Shared with swarm successfully."
        return "No swarm memory connected."

    def _tool_run_self_improvement(self, focus_area: str = "general") -> str:
        if self.self_improvement_loop:
            result = self.self_improvement_loop.run_cycle(focus_area=focus_area)
            return f"Self-improvement completed. Applied changes: {result.get('improvements_applied', 0)}"
        return "Self-improvement not available."

    # ------------------------------------------------------------------
    # REASONING WITH TOOLS
    # ------------------------------------------------------------------

    def reason(self, perception: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        raw_input = perception.get("raw", "")
        if self.use_llm_for_reasoning and self.llm_client:
            return self._reason_with_tools(raw_input, context)
        return self._heuristic_reason(raw_input, context)

    def _reason_with_tools(self, raw_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        relevant = self.retrieve_relevant_memories(raw_input, top_k=4)
        mem_ctx = "\n".join([f"- {m['content'][:170]}" for m in relevant]) if relevant else "No memories."

        system = (
            f"You are {self.role}. {self.persona}\n"
            f"You can use tools via function calls when helpful. "
            f"Available tools: {', '.join([t.name for t in self.tool_registry.list_tools()]) if self.tool_registry else 'none'}."
        )

        user = f"Input: {raw_input}\nRelevant memories:\n{mem_ctx}"

        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]

        try:
            if self.tool_registry and len(self.tool_registry) > 0:
                resp = self.llm_client.client.chat.completions.create(
                    model=self.llm_client.model,
                    messages=messages,
                    tools=self.tool_registry.get_openai_tools(),
                    tool_choice="auto",
                    temperature=0.6,
                )
                msg = resp.choices[0].message

                if msg.tool_calls:
                    results = []
                    for tc in msg.tool_calls:
                        args = json.loads(tc.function.arguments)
                        try:
                            res = self.tool_registry.execute(tc.function.name, args)
                            results.append(f"{tc.function.name}: {res}")
                        except Exception as e:
                            results.append(f"{tc.function.name} error: {e}")

                    messages.append(msg)
                    messages.append({"role": "tool", "tool_call_id": msg.tool_calls[0].id, "content": "\n".join(results)})

                    final = self.llm_client.client.chat.completions.create(
                        model=self.llm_client.model, messages=messages, temperature=0.6, max_tokens=600
                    )
                    content = final.choices[0].message.content
                else:
                    content = msg.content
            else:
                content = self.llm_client.simple_completion(prompt=user, system_prompt=system)

            return {"thought": content, "method": "llm_with_tools"}
        except Exception as e:
            print(f"Tool reasoning error: {e}")
            return self._heuristic_reason(raw_input, context)

    def decide(self, reasoning):
        return {"action_type": "respond", "content": reasoning.get("thought", ""), "method": reasoning.get("method", "heuristic")}

    def act(self, input_data):
        perception = self.perceive(input_data)
        reasoning = self.reason(perception)
        action = self.decide(reasoning)
        self._store_memory(content=action.get("content", "")[:200], tags=["action"])
        self.last_active = datetime.utcnow()
        return action

    def reflect(self):
        recent = self.vector_memory.get_recent_memories(5)
        ref = self._llm_reflect(recent) if self.use_llm_for_reasoning else self._heuristic_reflect(recent)
        self._store_memory(ref.get("content", ""), tags=["reflection"])
        return ref

    def _heuristic_reflect(self, recent):
        return {"content": f"Processed {len(recent)} experiences.", "method": "heuristic"}

    def _llm_reflect(self, recent):
        try:
            text = self.llm_client.simple_completion(f"Reflect and suggest one improvement based on: {recent}")
            return {"content": text, "method": "llm"}
        except:
            return self._heuristic_reflect(recent)

    def consolidate_memory(self):
        return self.vector_memory.consolidate_memories()

    def _store_memory(self, content, tags=None, importance=0.5):
        self.vector_memory.add_memory(content=content, tags=tags or [], importance=importance)

    def retrieve_relevant_memories(self, query, top_k=5):
        return self.vector_memory.search_relevant(query, top_k)

    def get_memory_stats(self):
        return self.vector_memory.get_stats()

    def get_state(self):
        return {
            "agent_id": self.agent_id, "role": self.role,
            "memory_stats": self.get_memory_stats(), "last_active": self.last_active.isoformat()
        }

    def __repr__(self):
        tools = len(self.tool_registry) if self.tool_registry else 0
        return f"<BaseAgent {self.role} | tools={tools} | memories={self.vector_memory.collection.count()}>"