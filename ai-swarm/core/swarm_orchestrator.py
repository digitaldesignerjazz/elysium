"""SwarmOrchestrator - Manages multiple agents, task distribution, and coordination.

Core of the AI Agent Swarm Framework in Elysium.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime

import asyncio

from .base_agent import BaseAgent


class SwarmOrchestrator:
    def __init__(self, swarm_name: str = "ElysiumSwarm"):
        self.swarm_name = swarm_name
        self.agents: Dict[str, BaseAgent] = {}
        self.task_history: List[Dict] = []
        self.created_at = datetime.utcnow()

    def register_agent(self, agent: BaseAgent) -> str:
        """Add an agent to the swarm."""
        self.agents[agent.agent_id] = agent
        return agent.agent_id

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        return [agent.get_state() for agent in self.agents.values()]

    async def run_task(
        self,
        task_description: str,
        target_agent_id: Optional[str] = None,
        broadcast: bool = False,
    ) -> Dict[str, Any]:
        """Execute a task across one or more agents."""
        results = []

        if broadcast:
            # Simple broadcast to all agents
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
            # Default: pick first agent or create ad-hoc behavior
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
        """Trigger reflection across all agents and aggregate insights."""
        reflections = []
        for agent in self.agents.values():
            reflections.append(agent.reflect())

        return {
            "swarm": self.swarm_name,
            "agent_count": len(self.agents),
            "reflections": reflections,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_swarm_state(self) -> Dict[str, Any]:
        return {
            "swarm_name": self.swarm_name,
            "agent_count": len(self.agents),
            "agents": self.list_agents(),
            "tasks_completed": len(self.task_history),
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<SwarmOrchestrator name={self.swarm_name} agents={len(self.agents)}>"