"""BaseAgent - Foundational class for all Elysium AI agents.

Provides identity, memory, emotional state, action loop, and self-reflection.
Part of the AI Agent Swarm Framework.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EmotionalState(BaseModel):
    valence: float = Field(0.0, ge=-1.0, le=1.0, description="Positive/negative emotional tone")
    arousal: float = Field(0.5, ge=0.0, le=1.0, description="Activation/energy level")
    dominant_traits: List[str] = Field(default_factory=lambda: ["curious", "loyal", "creative"])


class MemoryEntry(BaseModel):
    timestamp: datetime
    content: str
    tags: List[str] = Field(default_factory=list)
    importance: float = 0.5  # 0-1


class BaseAgent:
    def __init__(
        self,
        role: str,
        persona: str,
        agent_id: Optional[str] = None,
        emotional_state: Optional[EmotionalState] = None,
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.role = role
        self.persona = persona  # System prompt / behavioral guidelines
        self.emotional_state = emotional_state or EmotionalState()
        self.memory: List[MemoryEntry] = []
        self.created_at = datetime.utcnow()
        self.last_active = self.created_at

    def perceive(self, input_data: Any) -> Dict[str, Any]:
        """Process incoming perception (text, sensor data, messages, etc.)."""
        return {"raw": input_data, "processed_at": datetime.utcnow().isoformat()}

    def reason(self, perception: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Core reasoning step. Override in subclasses for LLM calls or logic."""
        return {
            "thought": f"As a {self.role}, I perceive: {perception.get('raw')}",
            "confidence": 0.7,
        }

    def decide(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on action based on reasoning and current emotional state."""
        action = {
            "action_type": "respond",
            "content": reasoning.get("thought", "No action decided."),
            "emotional_influence": self.emotional_state.valence,
        }
        return action

    def act(self, input_data: Any) -> Dict[str, Any]:
        """Full perceive → reason → decide → act loop."""
        perception = self.perceive(input_data)
        reasoning = self.reason(perception)
        action = self.decide(reasoning)

        # Record in memory
        self._store_memory(
            content=str(action.get("content", "")),
            tags=["action", self.role],
            importance=0.6,
        )
        self.last_active = datetime.utcnow()
        return action

    def reflect(self) -> Dict[str, Any]:
        """Self-reflection for improvement. Override for deeper analysis."""
        reflection = {
            "agent_id": self.agent_id,
            "role": self.role,
            "recent_actions": len([m for m in self.memory if "action" in m.tags]),
            "current_emotion": self.emotional_state.model_dump(),
            "suggestion": "Consider adjusting emotional thresholds or memory retrieval strategy.",
        }
        self._store_memory(
            content=f"Reflection: {reflection['suggestion']}",
            tags=["reflection", "self-improvement"],
            importance=0.8,
        )
        return reflection

    def _store_memory(self, content: str, tags: List[str], importance: float = 0.5):
        entry = MemoryEntry(
            timestamp=datetime.utcnow(),
            content=content,
            tags=tags,
            importance=importance,
        )
        self.memory.append(entry)
        # Simple pruning for demo (keep last 50)
        if len(self.memory) > 50:
            self.memory = sorted(self.memory, key=lambda x: x.importance, reverse=True)[:40]

    def get_state(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "emotional_state": self.emotional_state.model_dump(),
            "memory_count": len(self.memory),
            "last_active": self.last_active.isoformat(),
        }

    def __repr__(self):
        return f"<BaseAgent id={self.agent_id[:8]} role={self.role} valence={self.emotional_state.valence:.2f}>"