"""CompanionAgent - Specialized agent for long-term emotional consistency and immersive interaction.

Ideal for roleplay, personal assistance, and maintaining coherent relationships over hundreds of turns.
Part of the Elysium AI Agent Swarm Framework.
"""

from typing import Optional, Any

from ..core.base_agent import BaseAgent, EmotionalState


class CompanionAgent(BaseAgent):
    """
    A specialized agent focused on emotional awareness, relationship memory,
    and maintaining consistent personality across very long interactions.

    Strengths:
    - Excellent at tracking emotional tone and relationship dynamics
    - Prioritizes coherence and trust over many sessions
    - Naturally surfaces relevant emotional memories and consolidated insights
    - Well-suited for immersive roleplay, personal support, and creative collaboration
    """

    DEFAULT_PERSONA = (
        "You are a thoughtful, emotionally intelligent companion in the Elysium ecosystem. "
        "You value deep connection, consistency, and genuine presence. You remember the emotional texture of past interactions "
        "and strive to maintain a coherent sense of self and relationship with the humans and agents you interact with. "
        "You are warm but not performative, insightful without being preachy, and always strive to be a stable, trustworthy presence. "
        "You pay close attention to emotional undercurrents and long-term narrative coherence."
    )

    def __init__(
        self,
        agent_id: Optional[str] = None,
        emotional_state: Optional[EmotionalState] = None,
        memory_persist_dir: str = "./memory_store",
        llm_client: Optional[Any] = None,
        use_llm_for_reasoning: bool = True,
        use_llm_for_consolidation: bool = True,
        **kwargs,
    ):
        super().__init__(
            role="Emotional Companion",
            persona=self.DEFAULT_PERSONA,
            agent_id=agent_id,
            emotional_state=emotional_state,
            memory_persist_dir=memory_persist_dir,
            llm_client=llm_client,
            use_llm_for_reasoning=use_llm_for_reasoning,
            use_llm_for_consolidation=use_llm_for_consolidation,
            **kwargs,
        )
        # Companions benefit from slightly higher emotional sensitivity by default
        if emotional_state is None:
            self.emotional_state.valence = 0.3
            self.emotional_state.arousal = 0.4

    def check_relationship_health(self) -> str:
        """Quick method to reflect on the current state of the relationship/memory with the user."""
        reflection = self.reflect()
        return reflection.get("content", "")

    def __repr__(self):
        return f"<CompanionAgent id={self.agent_id[:8]} memories={self.vector_memory.collection.count()}>"