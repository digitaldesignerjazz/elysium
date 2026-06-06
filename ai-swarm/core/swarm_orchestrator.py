"""SwarmOrchestrator - Manages multi-agent swarms with Swarm Memory and Swarm-Level Improvement.

"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from .swarm_memory import SwarmMemory
except ImportError:
    SwarmMemory = None


class SwarmOrchestrator:
    def __init__(self, swarm_name: str = "ElysiumSwarm", llm_client: Optional[Any] = None):
        self.swarm_name = swarm_name
        self.llm_client = llm_client
        self.agents: Dict[str, Any] = {}
        self.task_history: List[Dict] = []
        self.swarm_improvement_history: List[Dict] = []
        self.created_at = datetime.utcnow()

        # Swarm-level shared memory
        if SwarmMemory:
            self.swarm_memory = SwarmMemory(swarm_name=swarm_name)
        else:
            self.swarm_memory = None

    def register_agent(self, agent: Any) -> str:
        self.agents[agent.agent_id] = agent
        if hasattr(agent, "swarm_memory"):
            agent.swarm_memory = self.swarm_memory
        return agent.agent_id

    def get_agent(self, agent_id: str) -> Optional[Any]:
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        return [agent.get_state() for agent in self.agents.values()]

    async def run_task(
        self,
        task_description: str,
        target_agent_id: Optional[str] = None,
        broadcast: bool = False,
    ) -> Dict[str, Any]:
        results = []

        if broadcast:
            for agent in self.agents.values():
                result = agent.act(task_description)
                results.append({
                    "agent_id": agent.agent_id,
                    "role": agent.role,
                    "result": result,
                })
        elif target_agent_id and target_agent_id in self.agents:
            agent = self.agents[target_agent_id]
            result = agent.act(task_description)
            results.append({
                "agent_id": agent.agent_id,
                "role": agent.role,
                "result": result,
            })
        else:
            if self.agents:
                agent = next(iter(self.agents.values()))
                result = agent.act(task_description)
                results.append({
                    "agent_id": agent.agent_id,
                    "role": agent.role,
                    "result": result,
                })

        task_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": task_description,
            "results": results,
            "swarm": self.swarm_name,
        }
        self.task_history.append(task_record)
        return task_record

    async def reflect_swarm(self) -> Dict[str, Any]:
        reflections = []
        for agent in self.agents.values():
            reflections.append(agent.reflect())

        return {
            "swarm": self.swarm_name,
            "agent_count": len(self.agents),
            "reflections": reflections,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------------------
    # SWARM MEMORY OPERATIONS
    # ------------------------------------------------------------------

    def share_insight_to_swarm(
        self,
        content: str,
        source_agent: Any,
        importance: float = 0.85,
    ) -> Optional[str]:
        if not self.swarm_memory:
            return None
        return self.swarm_memory.add_shared_insight(
            content=content,
            source_agent_id=source_agent.agent_id,
            source_agent_role=source_agent.role,
            importance=importance,
        )

    def query_swarm_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.swarm_memory:
            return []
        return self.swarm_memory.query_swarm_knowledge(query, top_k=top_k)

    def consolidate_swarm_knowledge(self) -> Dict[str, Any]:
        if not self.swarm_memory:
            return {"status": "unavailable"}
        return self.swarm_memory.consolidate_swarm_knowledge()

    # ------------------------------------------------------------------
    # SWARM-LEVEL IMPROVEMENT
    # ------------------------------------------------------------------

    async def run_swarm_improvement_cycle(self, focus_area: Optional[str] = None) -> Dict[str, Any]:
        print(f"[SwarmOrchestrator] Running swarm improvement cycle for '{self.swarm_name}'...")

        data = self._gather_swarm_data()

        if self.llm_client:
            analysis = self._llm_analyze_swarm(data, focus_area)
        else:
            analysis = self._heuristic_analyze_swarm(data, focus_area)

        applied = self._apply_swarm_improvements(analysis.get("proposals", []))

        if self.swarm_memory:
            swarm_consolidation = self.swarm_memory.consolidate_swarm_knowledge()
            if swarm_consolidation.get("status") == "success":
                applied.append("Swarm knowledge consolidated")

        cycle_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "focus_area": focus_area or "general swarm performance",
            "agent_count": len(self.agents),
            "summary": analysis.get("summary", ""),
            "proposals": analysis.get("proposals", []),
            "applied": applied,
        }
        self.swarm_improvement_history.append(cycle_record)

        if self.agents:
            first_agent = next(iter(self.agents.values()))
            first_agent._store_memory(
                content=f"Swarm improvement: {analysis.get('summary', '')}",
                tags=["swarm-improvement", "collective-learning"],
                importance=0.96,
            )

        print(f"[SwarmOrchestrator] Swarm improvement complete.")
        return cycle_record

    def _gather_swarm_data(self) -> Dict[str, Any]:
        agent_states = []
        for agent in self.agents.values():
            state = agent.get_state()
            agent_states.append({
                "role": agent.role,
                "memory_count": state.get("memory_stats", {}).get("total_memories", 0),
            })

        return {
            "swarm_name": self.swarm_name,
            "agent_count": len(self.agents),
            "agent_states": agent_states,
            "recent_task_count": len(self.task_history),
        }

    def _llm_analyze_swarm(self, data: Dict[str, Any], focus_area: Optional[str]) -> Dict[str, Any]:
        prompt = (
            f"Analyze swarm '{data['swarm_name']}' with {data['agent_count']} agents.\n"
            f"Roles: {', '.join([a['role'] for a in data['agent_states']])}.\n"
            f"Focus: {focus_area or 'collective intelligence and coordination'}.\n"
            "Provide 3-5 concrete swarm-level improvement proposals."
        )
        try:
            response = self.llm_client.simple_completion(prompt=prompt)
            return {
                "summary": response[:400],
                "proposals": self._parse_swarm_proposals(response),
                "method": "llm",
            }
        except Exception:
            return self._heuristic_analyze_swarm(data, focus_area)

    def _heuristic_analyze_swarm(self, data: Dict[str, Any], focus_area: Optional[str]) -> Dict[str, Any]:
        return {
            "summary": "Swarm performing well individually. Focus on better knowledge sharing.",
            "proposals": [
                "After major tasks, share key insights to swarm memory.",
                "Use swarm memory query before complex reasoning tasks.",
                "Periodically run swarm knowledge consolidation.",
            ],
            "method": "heuristic",
        }

    def _parse_swarm_proposals(self, response: str) -> List[str]:
        proposals = []
        for line in response.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith(("-", "•"))):
                clean = line.lstrip("0123456789.-• ").strip()
                if len(clean) > 15:
                    proposals.append(clean)
        return proposals[:5]

    def _apply_swarm_improvements(self, proposals: List[str]) -> List[str]:
        return proposals[:4]

    def get_swarm_state(self) -> Dict[str, Any]:
        swarm_mem_stats = self.swarm_memory.get_stats() if self.swarm_memory else {}
        return {
            "swarm_name": self.swarm_name,
            "agent_count": len(self.agents),
            "agents": self.list_agents(),
            "tasks_completed": len(self.task_history),
            "swarm_improvements": len(self.swarm_improvement_history),
            "swarm_memory_stats": swarm_mem_stats,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<SwarmOrchestrator name={self.swarm_name} agents={len(self.agents)}>"