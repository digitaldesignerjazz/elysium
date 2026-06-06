"""BaseAgent - Full LLM Reasoning Integration.

Agents can now use Grok/xAI (or compatible LLMs) for actual reasoning, decision making,
and reflection, grounded in persistent vector memory + consolidated insights.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

try:
    from .llm_client import LLMClient
except ImportError:
    LLMClient = None  # type: ignore

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

        self.created_at = datetime.utcnow()
        self.last_active = self.created_at

    # ------------------------------------------------------------------
    # CORE COGNITIVE LOOP (now LLM-powered when available)
    # ------------------------------------------------------------------

    def perceive(self, input_data: Any) -> Dict[str, Any]:
        return {"raw": str(input_data), "processed_at": datetime.utcnow().isoformat()}

    def reason(self, perception: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Core reasoning step.

        If LLM is available and enabled, performs rich LLM reasoning grounded in
        retrieved memories + consolidated insights + emotional state.
        Otherwise falls back to template-based reasoning.
        """
        raw_input = perception.get("raw", "")

        if self.use_llm_for_reasoning and self.llm_client:
            return self._llm_reason(raw_input, context)
        else:
            return self._heuristic_reason(raw_input, context)

    def _heuristic_reason(self, raw_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        relevant = self.retrieve_relevant_memories(raw_input, top_k=4)
        memory_context = "\n".join([m["content"][:180] for m in relevant])

        return {
            "thought": f"As a {self.role}, considering: {raw_input}. Relevant past: {memory_context[:300]}...",
            "relevant_memories": memory_context,
            "confidence": 0.65,
            "method": "heuristic",
        }

    def _llm_reason(self, raw_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """LLM-powered reasoning using Grok/xAI with memory context."""
        # Retrieve relevant raw memories
        relevant_memories = self.retrieve_relevant_memories(raw_input, top_k=5)
        memory_context = "\n".join(
            [f"- {m['content'][:200]}" for m in relevant_memories]
        ) if relevant_memories else "No specific past memories retrieved."

        # Retrieve consolidated insights (higher-level wisdom)
        consolidated = self.vector_memory.get_consolidated_memories(limit=3)
        consolidated_context = "\n".join(
            [f"- {c['content'][:220]}" for c in consolidated]
        ) if consolidated else "No consolidated insights yet."

        system_prompt = (
            f"You are {self.role}. {self.persona}\n\n"
            f"Current emotional state: valence={self.emotional_state.valence:.2f}, "
            f"arousal={self.emotional_state.arousal:.2f}. "
            f"Dominant traits: {', '.join(self.emotional_state.dominant_traits)}.\n\n"
            f"You have access to your persistent memory and consolidated insights from past experiences. "
            f"Use them to inform your reasoning. Be thoughtful, consistent with your persona, and aligned with "
            f"Elysium principles: decentralized systems, self-improvement, emotional awareness, and long-term coherence."
        )

        user_prompt = (
            f"Current situation / input: {raw_input}\n\n"
            f"Relevant memories from your experience:\n{memory_context}\n\n"
            f"Consolidated higher-level insights from your past:\n{consolidated_context}\n\n"
            f"Think step by step and respond with your reasoning and proposed action or response. "
            f"Keep it concise but insightful."
        )

        try:
            llm_response = self.llm_client.simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
            )

            return {
                "thought": llm_response,
                "relevant_memories": memory_context,
                "consolidated_insights_used": consolidated_context,
                "confidence": 0.85,
                "method": "llm",
            }
        except Exception as e:
            print(f"[BaseAgent] LLM reasoning failed: {e}. Falling back to heuristic.")
            return self._heuristic_reason(raw_input, context)

    def decide(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on action based on reasoning output."""
        if reasoning.get("method") == "llm":
            # LLM already produced thoughtful output; use it directly
            return {
                "action_type": "respond",
                "content": reasoning.get("thought", "No clear decision."),
                "emotional_influence": self.emotional_state.valence,
                "confidence": reasoning.get("confidence", 0.8),
                "method": "llm",
            }
        else:
            # Heuristic decision
            return {
                "action_type": "respond",
                "content": reasoning.get("thought", "No action decided."),
                "emotional_influence": self.emotional_state.valence,
                "confidence": reasoning.get("confidence", 0.6),
                "method": "heuristic",
            }

    def act(self, input_data: Any) -> Dict[str, Any]:
        perception = self.perceive(input_data)
        reasoning = self.reason(perception)
        action = self.decide(reasoning)

        # Store the action + reasoning trace in memory
        self._store_memory(
            content=f"Action: {action.get('content', '')} | Thought: {reasoning.get('thought', '')[:300]}",
            tags=["action", self.role, reasoning.get("method", "heuristic")],
            importance=0.7,
            emotional_valence=self.emotional_state.valence,
        )
        self.last_active = datetime.utcnow()
        return action

    def reflect(self) -> Dict[str, Any]:
        recent = self.vector_memory.get_recent_memories(limit=6)

        if self.use_llm_for_reasoning and self.llm_client:
            reflection = self._llm_reflect(recent)
        else:
            reflection = self._heuristic_reflect(recent)

        self._store_memory(
            content=reflection.get("content", "Reflection completed."),
            tags=["reflection", "self-improvement", reflection.get("method", "heuristic")],
            importance=0.9,
            emotional_valence=self.emotional_state.valence,
        )

        return reflection

    def _heuristic_reflect(self, recent_memories: List[Dict]) -> Dict[str, Any]:
        return {
            "content": f"I have processed {len(recent_memories)} recent experiences. "
                       f"I should look for patterns and adjust my approach.",
            "method": "heuristic",
            "suggestion": "Continue monitoring emotional state and memory retrieval quality.",
        }

    def _llm_reflect(self, recent_memories: List[Dict]) -> Dict[str, Any]:
        """LLM-powered deep reflection."""
        memory_summary = "\n".join([f"- {m['content'][:160]}" for m in recent_memories])

        prompt = (
            f"You are {self.role}. Reflect deeply on your recent experiences and consolidated insights. "
            f"Identify patterns, emotional trends, strengths, and areas for improvement. "
            f"Suggest one concrete behavioral or strategic adjustment.\n\n"
            f"Recent experiences:\n{memory_summary}"
        )

        system_prompt = (
            f"You are a wise, self-aware agent in the Elysium ecosystem. "
            f"Your goal is continuous self-improvement while staying true to your persona."
        )

        try:
            reflection_text = self.llm_client.simple_completion(prompt=prompt, system_prompt=system_prompt)
            return {
                "content": reflection_text,
                "method": "llm",
                "suggestion": "Apply insights from this reflection to future decisions.",
            }
        except Exception:
            return self._heuristic_reflect(recent_memories)

    # ------------------------------------------------------------------
    # Memory helpers
    # ------------------------------------------------------------------
    def consolidate_memory(self) -> Dict[str, Any]:
        return self.vector_memory.consolidate_memories()

    def _store_memory(
        self, content: str, tags: Optional[List[str]] = None, importance: float = 0.5, emotional_valence: float = 0.0
    ):
        self.vector_memory.add_memory(
            content=content,
            tags=tags or [],
            importance=importance,
            emotional_valence=emotional_valence,
            source=self.role,
        )

    def retrieve_relevant_memories(self, query: str, top_k: int = 5, min_importance: float = 0.2) -> List[Dict[str, Any]]:
        return self.vector_memory.search_relevant(query=query, top_k=top_k, min_importance=min_importance)

    def get_memory_stats(self) -> Dict[str, Any]:
        return self.vector_memory.get_stats()

    def get_state(self) -> Dict[str, Any]:
        stats = self.get_memory_stats()
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "emotional_state": self.emotional_state.model_dump(),
            "memory_stats": stats,
            "last_active": self.last_active.isoformat(),
        }

    def __repr__(self):
        mem_count = self.vector_memory.collection.count() if hasattr(self, "vector_memory") else 0
        llm_status = "LLM" if self.use_llm_for_reasoning else "heuristic"
        return f"<BaseAgent id={self.agent_id[:8]} role={self.role} mode={llm_status} memories={mem_count}>"