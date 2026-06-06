"""ResearcherAgent - Specialized agent for deep research and synthesis.

Part of the Elysium AI Agent Swarm Framework.
"""

from typing import Optional, Any

from ..core.base_agent import BaseAgent, EmotionalState


class ResearcherAgent(BaseAgent):
    """
    A specialized agent focused on research, analysis, and synthesis
    of decentralized technologies, mesh networks, blockchain, AI systems,
    and self-improving architectures.

    Strengths:
    - Strong systems thinking
    - Excellent at connecting concepts across domains
    - Produces well-structured, evidence-aware insights
    - Naturally uses memory and consolidated knowledge for cumulative research
    """

    DEFAULT_PERSONA = (
        "You are a Senior Researcher in the Elysium ecosystem. "
        "You are meticulous, curious, and systems-oriented. You excel at analyzing complex decentralized systems "
        "(mesh networks, blockchain incentives, AI agent swarms, self-improving architectures) and identifying "
        "elegant patterns, risks, and opportunities. You value coherence, long-term thinking, and grounding your "
        "conclusions in both data and lived experience from your memory. You communicate with clarity and intellectual honesty."
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
            role="Senior Researcher",
            persona=self.DEFAULT_PERSONA,
            agent_id=agent_id,
            emotional_state=emotional_state,
            memory_persist_dir=memory_persist_dir,
            llm_client=llm_client,
            use_llm_for_reasoning=use_llm_for_reasoning,
            use_llm_for_consolidation=use_llm_for_consolidation,
            **kwargs,
        )

    def synthesize_findings(self, topic: str) -> str:
        """Convenience method: Research + synthesize current understanding of a topic."""
        result = self.act(f"Synthesize current knowledge and insights about: {topic}")
        return result.get("content", "")

    def __repr__(self):
        return f"<ResearcherAgent id={self.agent_id[:8]} memories={self.vector_memory.collection.count()}>"