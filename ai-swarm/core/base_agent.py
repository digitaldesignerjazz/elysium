"""BaseAgent with full Tool Use / Function Calling support.

Agents can now use tools via LLM function calling (Grok/xAI compatible).
"""

from __future__ import annotations
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

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

        # Tool support
        self.tool_registry = ToolRegistry() if ToolRegistry else None
        self.swarm_memory = None  # Can be set by SwarmOrchestrator

        self.created_at = datetime.utcnow()
        self.last_active = self.created_at

        # Register default tools
        self._register_default_tools()

    def _register_default_tools(self):
        if not self.tool_registry:
            return

        # Core memory tools
        self.tool_registry.register_function(
            name="query_memory",
            description="Search the agent's own persistent memory for relevant past experiences or insights.",
            func=self._tool_query_memory,
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for in memory"},
                    "top_k": {"type": "integer", "description": "Number of results", "default": 5}
                },
                "required": ["query"]
            }
        )

        self.tool_registry.register_function(
            name="share_to_swarm",
            description="Share an important insight with the entire swarm's shared memory.",
            func=self._tool_share_to_swarm,
            parameters={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The insight to share"},
                    "importance": {"type": "number", "description": "How important is this insight?", "default": 0.85}
                },
                "required": ["content"]
            }
        )

        self.tool_registry.register_function(
            name="run_self_improvement",
            description="Trigger a self-improvement cycle for this agent.",
            func=self._tool_run_self_improvement,
            parameters={
                "type": "object",
                "properties": {
                    "focus_area": {"type": "string", "description": "What area to focus improvement on"}
                }
            }
        )

    def _tool_query_memory(self, query: str, top_k: int = 5) -> str:
        results = self.retrieve_relevant_memories(query, top_k=top_k)
        if not results:
            return "No relevant memories found."
        return "\n".join([f"- {r['content'][:200]}" for r in results])

    def _tool_share_to_swarm(self, content: str, importance: float = 0.85) -> str:
        if self.swarm_memory:
            self.swarm_memory.add_shared_insight(
                content=content,
                source_agent_id=self.agent_id,
                source_agent_role=self.role,
                importance=importance,
            )
            return "Insight shared with swarm successfully."
        return "No swarm memory available. Insight stored only locally."

    def _tool_run_self_improvement(self, focus_area: str = "general performance") -> str:
        if self.self_improvement_loop:
            result = self.self_improvement_loop.run_cycle(focus_area=focus_area)
            return f"Self-improvement cycle completed. Applied {result.get('improvements_applied', 0)} changes."
        return "Self-improvement not available."

    # ------------------------------------------------------------------
    # REASONING WITH TOOL USE
    # ------------------------------------------------------------------

    def reason(self, perception: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        raw_input = perception.get("raw", "")

        if self.use_llm_for_reasoning and self.llm_client:
            return self._reason_with_tools(raw_input, context)
        else:
            return self._heuristic_reason(raw_input, context)

    def _reason_with_tools(self, raw_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """LLM reasoning with native function calling support."""
        relevant_memories = self.retrieve_relevant_memories(raw_input, top_k=4)
        memory_context = "\n".join([f"- {m['content'][:180]}" for m in relevant_memories]) if relevant_memories else "No specific memories."

        consolidated = self.vector_memory.get_consolidated_memories(limit=2)
        consolidated_context = "\n".join([f"- {c['content'][:180]}" for c in consolidated]) if consolidated else ""

        system_prompt = (
            f"You are {self.role}. {self.persona}\n\n"
            f"Current emotional state: valence={self.emotional_state.valence:.2f}.\n\n"
            f"You have access to tools via function calls. Use them when they would help solve the task or gather information.\n"
            f"Available tools: {', '.join([t.name for t in (self.tool_registry.list_tools() if self.tool_registry else [])]) or 'none'}.\n\n"
            f"Think step by step. Use tools if needed, then provide your final response."
        )

        user_prompt = (
            f"Current input: {raw_input}\n\n"
            f"Relevant memories:\n{memory_context}\n\n"
            f"Consolidated insights:\n{consolidated_context}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # Use OpenAI-compatible function calling
            if self.tool_registry and len(self.tool_registry) > 0:
                response = self.llm_client.client.chat.completions.create(
                    model=self.llm_client.model,
                    messages=messages,
                    tools=self.tool_registry.get_openai_tools(),
                    tool_choice="auto",
                    temperature=self.llm_client.temperature,
                    max_tokens=self.llm_client.max_tokens,
                )

                message = response.choices[0].message

                # Handle tool calls
                if message.tool_calls:
                    tool_results = []
                    for tool_call in message.tool_calls:
                        name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        try:
                            result = self.tool_registry.execute(name, arguments)
                            tool_results.append(f"Tool '{name}' result: {result}")
                        except Exception as e:
                            tool_results.append(f"Tool '{name}' error: {str(e)}")

                    # Feed tool results back for final answer
                    messages.append(message)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": message.tool_calls[0].id,
                        "content": "\n".join(tool_results)
                    })

                    final_response = self.llm_client.client.chat.completions.create(
                        model=self.llm_client.model,
                        messages=messages,
                        temperature=0.6,
                        max_tokens=600,
                    )
                    final_content = final_response.choices[0].message.content
                else:
                    final_content = message.content
            else:
                # No tools available
                final_content = self.llm_client.simple_completion(
                    prompt=user_prompt, system_prompt=system_prompt
                )

            return {
                "thought": final_content,
                "method": "llm_with_tools" if self.tool_registry and len(self.tool_registry) > 0 else "llm",
                "relevant_memories": memory_context,
            }
        except Exception as e:
            print(f"[BaseAgent] Tool reasoning failed: {e}. Falling back.")
            return self._heuristic_reason(raw_input, context)

    def decide(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action_type": "respond",
            "content": reasoning.get("thought", "No decision made."),
            "emotional_influence": self.emotional_state.valence,
            "method": reasoning.get("method", "heuristic"),
        }

    def act(self, input_data: Any) -> Dict[str, Any]:
        perception = self.perceive(input_data)
        reasoning = self.reason(perception)
        action = self.decide(reasoning)

        self._store_memory(
            content=f"Action: {action.get('content', '')[:200]}",
            tags=["action", self.role],
            importance=0.7,
        )
        self.last_active = datetime.utcnow()
        return action

    # ... (rest of methods like reflect, consolidate, memory helpers remain similar)

    def reflect(self) -> Dict[str, Any]:
        recent = self.vector_memory.get_recent_memories(limit=5)
        if self.use_llm_for_reasoning and self.llm_client:
            reflection = self._llm_reflect(recent)
        else:
            reflection = self._heuristic_reflect(recent)

        self._store_memory(
            content=reflection.get("content", ""),
            tags=["reflection", "self-improvement"],
            importance=0.9,
        )
        return reflection

    def _heuristic_reflect(self, recent_memories):
        return {"content": f"Processed {len(recent_memories)} experiences.", "method": "heuristic"}

    def _llm_reflect(self, recent_memories):
        memory_summary = "\n".join([f"- {m['content'][:140]}" for m in recent_memories])
        prompt = f"Reflect on these experiences and suggest one improvement: {memory_summary}"
        try:
            text = self.llm_client.simple_completion(prompt=prompt)
            return {"content": text, "method": "llm"}
        except:
            return self._heuristic_reflect(recent_memories)

    def consolidate_memory(self):
        return self.vector_memory.consolidate_memories()

    def _store_memory(self, content, tags=None, importance=0.5, emotional_valence=0.0):
        self.vector_memory.add_memory(content=content, tags=tags or [], importance=importance, emotional_valence=emotional_valence)

    def retrieve_relevant_memories(self, query, top_k=5, min_importance=0.2):
        return self.vector_memory.search_relevant(query=query, top_k=top_k, min_importance=min_importance)

    def get_memory_stats(self):
        return self.vector_memory.get_stats()

    def get_state(self):
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "emotional_state": self.emotional_state.model_dump(),
            "memory_stats": self.get_memory_stats(),
            "last_active": self.last_active.isoformat(),
        }

    def __repr__(self):
        tool_count = len(self.tool_registry) if self.tool_registry else 0
        return f"<BaseAgent role={self.role} tools={tool_count} memories={self.vector_memory.collection.count()}>"