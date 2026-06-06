"""BaseAgent - Foundational class for all Elysium AI agents.

Now upgraded with persistent VectorMemory (ChromaDB + semantic retrieval).
Part of the AI Agent Swarm Framework.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .vector_memory import VectorMemory


class EmotionalState(BaseModel):
    valence: float = Field(0.0, ge=-1.0, le=1.0, description="Positive/negative emotional tone")
    arousal: float = Field(0.5, ge=0.0, le=1.0, description="Activation/energy level")
    dominant_traits: List[str] = Field(default_factory=lambda: ["curious", "loyal", "creative"])


class BaseAgent:
    def __init__(
        self,
        role: str,
        persona: str,
        agent_id: Optional[str] = None,
        emotional_state: Optional[EmotionalState] = None,
        memory_persist_dir: str = "./memory_store",
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.role = role
        self.persona = persona
        self.emotional_state = emotional_state or EmotionalState()

        # Persistent vector memory (replaces simple in-memory list)
        self.vector_memory = VectorMemory(
            agent_id=self.agent_id,
            persist_directory=memory_persist_dir
        )

        self.created_at = datetime.utcnow()
        self.last_active = self.created_at

    # ------------------------------------------------------------------
    # Core cognitive loop
    # ------------------------------------------------------------------
    def perceive(self, input_data: Any) -> Dict[str, Any]:
        """Process incoming perception."""
        return {"raw": input_data, "processed_at": datetime.utcnow().isoformat()}

    def reason(self, perception: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Core reasoning. Subclasses should override to call LLMs."""
        # Retrieve relevant memories for context
        relevant = self.retrieve_relevant_memories(
            str(perception.get("raw", "")), top_k=3
        )
        memory_context = "\n".join([m["content"][:200] for m in relevant])

        return {
            "thought": f"As a {self.role}, I perceive: {perception.get('raw')}",
            "relevant_memories": memory_context,
            "confidence": 0.7,
        }

    def decide(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        action = {
            "action_type": "respond",
            "content": reasoning.get("thought", "No action decided."),
            "emotional_influence": self.emotional_state.valence,
            "used_memories": len(reasoning.get("relevant_memories", "")),
        }
        return action

    def act(self, input_data: Any) -> Dict[str, Any]:
        perception = self.perceive(input_data)
        reasoning = self.reason(perception)
        action = self.decide(reasoning)

        # Store in persistent vector memory with rich metadata
        self._store_memory(
            content=str(action.get("content", "")),
            tags=["action", self.role],
            importance=0.6,
            emotional_valence=self.emotional_state.valence,
        )
        self.last_active = datetime.utcnow()
        return action

    def reflect(self) -> Dict[str, Any]:
        """Self-reflection using vector memory."""
        recent = self.vector_memory.get_recent_memories(limit=5)
        reflection_text = (
            f"I have {len(recent)} recent memories. "
            f"My current emotional state is valence={self.emotional_state.valence:.2f}. "
            "I should consider how past experiences influence future decisions."
        )

        self._store_memory(
            content=reflection_text,
            tags=["reflection", "self-improvement"],
            importance=0.85,
            emotional_valence=self.emotional_state.valence,
        )

        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "recent_memories_count": len(recent),
            "current_emotion": self.emotional_state.model_dump(),
            "suggestion": "Review retrieved memories for patterns and evolve prompts or behavior.",
        }

    # ------------------------------------------------------------------
    # Memory helpers (now powered by VectorMemory)
    # ------------------------------------------------------------------
    def _store_memory(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
    ):
        self.vector_memory.add_memory(
            content=content,
            tags=tags or [],
            importance=importance,
            emotional_valence=emotional_valence,
            source=self.role,
        )

    def retrieve_relevant_memories(
        self, query: str, top_k: int = 5, min_importance: float = 0.2
    ) -> List[Dict[str, Any]]:
        """Semantic search across persistent memory."""
        return self.vector_memory.search_relevant(
            query=query, top_k=top_k, min_importance=min_importance
        )

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
        mem_count = self.vector_memory.collection.count() if hasattr(self, 'vector_memory') else 0
        return f"<BaseAgent id={self.agent_id[:8]} role={self.role} memories={mem_count} valence={self.emotional_state.valence:.2f}>"