"""SelfImprovementLoop - Enables agents to analyze their own behavior and evolve over time.

Part of the Elysium AI Agent Swarm Framework.
This closes the loop on self-improving systems.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class SelfImprovementLoop:
    """
    A self-improvement engine that agents can use to analyze performance,
    generate actionable improvements, and evolve their behavior.

    Improvements can include:
    - Refinements to reasoning style or prompt elements
    - Adjustments to emotional response patterns
    - New memory retrieval or consolidation strategies
    - Suggestions for new capabilities or tools
    - Persona evolution while maintaining core identity
    """

    def __init__(self, agent: Any):
        self.agent = agent
        self.improvement_history: List[Dict] = []

    def run_cycle(self, focus_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute one full self-improvement cycle.

        Steps:
        1. Gather recent performance data (actions, reflections, consolidations)
        2. Analyze what is working and what could be improved
        3. Generate specific, actionable improvement proposals
        4. Apply high-confidence improvements (or store for review)
        5. Record the cycle in memory
        """
        print(f"[SelfImprovement] Starting improvement cycle for {self.agent.role}...")

        # Step 1: Gather data
        data = self._gather_performance_data()

        # Step 2 + 3: Analyze and generate improvements using LLM (if available)
        if self.agent.use_llm_for_reasoning and self.agent.llm_client:
            analysis = self._llm_analyze_and_propose(data, focus_area)
        else:
            analysis = self._heuristic_analyze_and_propose(data, focus_area)

        # Step 4: Apply improvements
        applied = self._apply_improvements(analysis.get("proposals", []))

        # Step 5: Record cycle
        cycle_record = {
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "focus_area": focus_area,
            "analysis_summary": analysis.get("summary", ""),
            "proposals_generated": len(analysis.get("proposals", [])),
            "improvements_applied": len(applied),
            "applied_changes": applied,
        }
        self.improvement_history.append(cycle_record)

        # Store significant cycles in agent's memory
        if len(applied) > 0 or analysis.get("summary"):
            self.agent._store_memory(
                content=f"Self-improvement cycle: {analysis.get('summary', '')} | Applied: {applied}",
                tags=["self-improvement", "reflection", "evolution"],
                importance=0.95,
            )

        print(f"[SelfImprovement] Cycle complete. Applied {len(applied)} improvements.")
        return cycle_record

    def _gather_performance_data(self) -> Dict[str, Any]:
        """Collect recent experiences, reflections, and consolidated insights."""
        recent_actions = self.agent.vector_memory.get_recent_memories(limit=8)
        recent_reflections = self.agent.vector_memory.search_relevant(
            "reflection self-improvement", top_k=5
        )
        consolidated = self.agent.vector_memory.get_consolidated_memories(limit=4)

        return {
            "recent_actions_count": len(recent_actions),
            "recent_reflections": [r["content"][:200] for r in recent_reflections],
            "consolidated_insights": [c["content"][:200] for c in consolidated],
            "current_emotional_state": self.agent.emotional_state.model_dump(),
            "role": self.agent.role,
        }

    def _llm_analyze_and_propose(self, data: Dict[str, Any], focus_area: Optional[str]) -> Dict[str, Any]:
        """Use LLM to analyze performance and propose concrete improvements."""
        prompt = (
            f"You are analyzing the performance of a {data['role']} agent in the Elysium ecosystem.\n\n"
            f"Current emotional state: {data['current_emotional_state']}\n\n"
            f"Recent consolidated insights:\n" + "\n".join(data.get("consolidated_insights", [])) + "\n\n"
            f"Recent reflections:\n" + "\n".join(data.get("recent_reflections", [])) + "\n\n"
            f"Focus area for improvement: {focus_area or 'general performance and coherence'}\n\n"
            "Based on this data, provide:\n"
            "1. A short summary of current strengths and weaknesses.\n"
            "2. 2-4 specific, actionable improvement proposals. Each proposal should be concrete (e.g., 'Add stronger emphasis on emotional tone tracking in reasoning', 'Prioritize consolidated insights more heavily when making strategic decisions').\n"
            "Format your response clearly with numbered proposals."
        )

        system_prompt = (
            "You are an expert self-improvement coach for autonomous AI agents. "
            "Your suggestions should be practical, specific, and aligned with long-term coherence and self-improvement goals."
        )

        try:
            response = self.agent.llm_client.simple_completion(prompt=prompt, system_prompt=system_prompt)
            return {
                "summary": response[:400],
                "proposals": self._parse_proposals(response),
                "method": "llm",
            }
        except Exception as e:
            print(f"[SelfImprovement] LLM analysis failed: {e}")
            return self._heuristic_analyze_and_propose(data, focus_area)

    def _heuristic_analyze_and_propose(self, data: Dict[str, Any], focus_area: Optional[str]) -> Dict[str, Any]:
        """Fallback heuristic analysis."""
        proposals = [
            "Increase weight given to consolidated insights during reasoning.",
            "Pay closer attention to emotional valence when deciding on actions.",
            "After every major task, explicitly compare outcome to original intention.",
        ]
        return {
            "summary": "General performance is stable. Focus on better use of memory and emotional awareness.",
            "proposals": proposals,
            "method": "heuristic",
        }

    def _parse_proposals(self, llm_response: str) -> List[str]:
        """Simple parser to extract numbered proposals from LLM output."""
        proposals = []
        for line in llm_response.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or "proposal" in line.lower()):
                clean = line.lstrip("0123456789.- ").strip()
                if len(clean) > 15:
                    proposals.append(clean)
        return proposals[:5]  # Limit to top proposals

    def _apply_improvements(self, proposals: List[str]) -> List[str]:
        """Apply or record improvements. Currently stores them as high-value memories.
        In future versions this can modify agent state, prompts, or parameters directly.
        """
        applied = []
        for proposal in proposals[:3]:  # Apply top 3
            # For safety, we primarily record the improvement rather than auto-mutate core logic
            self.agent._store_memory(
                content=f"Improvement applied: {proposal}",
                tags=["self-improvement", "applied_change"],
                importance=0.98,
            )
            applied.append(proposal)

        # Future enhancement: dynamically adjust emotional_state, add to persona, etc.
        return applied

    def get_improvement_history(self) -> List[Dict]:
        return self.improvement_history