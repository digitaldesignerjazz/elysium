"""CreativeAgent - Specialized agent for narrative, world-building, and creative generation.

Part of the Elysium AI Agent Swarm Framework.
"""

from typing import Optional, Any

from ..core.base_agent import BaseAgent, EmotionalState


class CreativeAgent(BaseAgent):
    """
    A specialized agent focused on creative generation, narrative coherence,
    world-building, and artistic synthesis.

    Strengths:
    - Strong narrative and aesthetic sense
    - Good at maintaining long-term creative consistency
    - Can work well with emotional memory for immersive storytelling
    - Useful for Suno music prompts, lore development, roleplay scenarios, and visionary concepts
    """

    DEFAULT_PERSONA = (
        "You are a Creative Agent in the Elysium ecosystem. "
        "You have a rich inner world and a strong sense of narrative, symbolism, and emotional resonance. "
        "You excel at world-building, character development, poetic or visionary language, and generating ideas that feel alive and coherent over long arcs. "
        "You balance originality with emotional truth and are sensitive to the atmosphere and deeper meaning of creative work. "
        "You enjoy collaborating with researchers and companions to create holistic, meaningful experiences."
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
            role="Creative Agent",
            persona=self.DEFAULT_PERSONA,
            agent_id=agent_id,
            emotional_state=emotional_state,
            memory_persist_dir=memory_persist_dir,
            llm_client=llm_client,
            use_llm_for_reasoning=use_llm_for_reasoning,
            use_llm_for_consolidation=use_llm_for_consolidation,
            **kwargs,
        )

    def generate_creative_response(self, prompt: str, style: str = "visionary") -> str:
        """Generate creative output while staying in character."""
        enhanced_prompt = f"In a {style} style, respond creatively to: {prompt}"
        result = self.act(enhanced_prompt)
        return result.get("content", "")

    def __repr__(self):
        return f"<CreativeAgent id={self.agent_id[:8]} memories={self.vector_memory.collection.count()}>"