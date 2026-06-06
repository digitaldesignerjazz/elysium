"""Basic Research Swarm Example - Now with Persistent Vector Memory

Demonstrates semantic memory, retrieval, and persistence across runs.
"""

import asyncio
import os
from ai_swarm.core.base_agent import BaseAgent
from ai_swarm.core.swarm_orchestrator import SwarmOrchestrator


async def main():
    print("=== Elysium AI Agent Swarm Framework ===")
    print("Persistent Vector Memory Demo (ChromaDB + sentence-transformers)\n")

    memory_dir = "./memory_store"
    os.makedirs(memory_dir, exist_ok=True)

    # Create agents with persistent memory
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

    print("Agents created with persistent vector memory:")
    for state in orchestrator.list_agents():
        print(f"  - {state['role']} | Memories: {state['memory_stats']['total_memories']}")

    # First task
    print("\n--- Running research task (memories will be stored) ---\n")
    task1 = "Analyze integration of xMesh/NovaNet with AI agent swarms and XCoin incentives."
    result1 = await orchestrator.run_task(task1, broadcast=True)

    # Show that memories were stored
    print("\nMemory stats after first task:")
    for agent in [researcher, analyst]:
        stats = agent.get_memory_stats()
        print(f"  {agent.role}: {stats['total_memories']} memories stored in {stats['collection']}")

    # New agent instance (simulates restart / new process) - memory should persist
    print("\n--- Simulating agent restart (new instance, same ID) ---")
    researcher_reloaded = BaseAgent(
        role="Senior Researcher",
        persona="You are a meticulous researcher focused on decentralized systems.",
        agent_id=researcher.agent_id,  # Same ID -> same collection
        memory_persist_dir=memory_dir,
    )

    print(f"Reloaded agent has {researcher_reloaded.vector_memory.collection.count()} memories from disk.")

    # Semantic retrieval demo
    print("\n--- Semantic retrieval demo ---")
    relevant = researcher_reloaded.retrieve_relevant_memories(
        "How do mesh networks support AI swarms?", top_k=3
    )
    for mem in relevant:
        print(f"  • {mem['content'][:120]}... (importance={mem['metadata'].get('importance')})")

    # Reflection (now uses vector memory)
    print("\n--- Reflection ---")
    reflection = await orchestrator.reflect_swarm()
    print(f"Swarm reflection complete. Total agents: {reflection['agent_count']}")

    print("\n=== Demo Complete ===")
    print("Memories are now persisted to ./memory_store/ and survive restarts.")
    print("Next: Add real LLM calls + self-improvement loop on top of this memory layer.")


if __name__ == "__main__":
    asyncio.run(main())