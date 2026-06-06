"""Basic Research Swarm Example - With Memory Consolidation

Shows automatic + manual consolidation of experiences into higher-level insights.
"""

import asyncio
import os
from ai_swarm.core.base_agent import BaseAgent
from ai_swarm.core.swarm_orchestrator import SwarmOrchestrator


async def main():
    print("=== Elysium AI Agent Swarm Framework ===")
    print("Memory Consolidation Demo\n")

    memory_dir = "./memory_store"
    os.makedirs(memory_dir, exist_ok=True)

    researcher = BaseAgent(
        role="Senior Researcher",
        persona="You are a meticulous researcher focused on decentralized systems.",
        memory_persist_dir=memory_dir,
    )

    analyst = BaseAgent(
        role="Systems Analyst",
        persona="You analyze connections between technology layers.",
        memory_persist_dir=memory_dir,
    )

    orchestrator = SwarmOrchestrator(swarm_name="ElysiumResearchSwarm")
    orchestrator.register_agent(researcher)
    orchestrator.register_agent(analyst)

    print("Running multiple tasks to build up memory...\n")

    tasks = [
        "Research xMesh and NovaNet integration with AI swarms.",
        "Analyze how QCoin incentives could motivate agent behavior.",
        "Evaluate self-improvement loops for long-running agents.",
        "Propose architecture for emotional memory in roleplay scenarios.",
        "Summarize risks and opportunities in decentralized AI systems.",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"Task {i}: {task[:60]}...")
        await orchestrator.run_task(task, broadcast=True)

    print("\n--- Memory stats before consolidation ---")
    for agent in [researcher, analyst]:
        stats = agent.get_memory_stats()
        print(f"  {agent.role}: {stats['total_memories']} memories")

    # Manual consolidation
    print("\n--- Triggering manual memory consolidation ---")
    result = researcher.consolidate_memory()
    print(f"Consolidation result: {result}")

    # Check consolidated summaries
    print("\n--- Consolidated insights created ---")
    consolidated = researcher.vector_memory.get_consolidated_memories(limit=5)
    for mem in consolidated:
        print(f"\n  {mem['content'][:200]}...")

    # Reflection (also triggers consolidation automatically if many memories)
    print("\n--- Running reflection (may trigger auto-consolidation) ---")
    reflection = await orchestrator.reflect_swarm()

    print("\n=== Memory Consolidation Demo Complete ===")
    print("Higher-level semantic summaries are now stored alongside raw experiences.")
    print("This enables better long-term reasoning and self-improvement.")


if __name__ == "__main__":
    asyncio.run(main())