"""Basic Research Swarm Example - LLM-Powered Memory Consolidation

Demonstrates high-quality LLM-based consolidation using Grok/xAI (or any OpenAI-compatible model).
"""

import asyncio
import os

# Optional: import LLMClient for high-quality consolidation
try:
    from ai_swarm.core.llm_client import LLMClient
except ImportError:
    LLMClient = None

from ai_swarm.core.base_agent import BaseAgent
from ai_swarm.core.swarm_orchestrator import SwarmOrchestrator


async def main():
    print("=== Elysium AI Agent Swarm Framework ===")
    print("LLM-Powered Memory Consolidation Demo\n")

    memory_dir = "./memory_store"
    os.makedirs(memory_dir, exist_ok=True)

    # === LLM Client Setup (optional but recommended for best results) ===
    # Set your API key: export XAI_API_KEY=your_key   or   OPENAI_API_KEY=your_key
    llm = None
    if LLMClient and (os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")):
        try:
            llm = LLMClient(
                # For xAI Grok:
                # base_url="https://api.x.ai/v1",
                # model="grok-beta" or "grok-3-latest"
                model="grok-beta",
                temperature=0.6,
                max_tokens=600,
            )
            print("LLM client initialized - using high-quality LLM consolidation.\n")
        except Exception as e:
            print(f"Could not initialize LLM client: {e}\nFalling back to heuristic consolidation.\n")
            llm = None
    else:
        print("No LLM API key found. Using heuristic consolidation (still functional).\n")

    researcher = BaseAgent(
        role="Senior Researcher",
        persona="You are a meticulous researcher focused on decentralized systems and self-improving AI.",
        memory_persist_dir=memory_dir,
        llm_client=llm,
        use_llm_for_consolidation=bool(llm),
    )

    analyst = BaseAgent(
        role="Systems Analyst",
        persona="You analyze connections between mesh, blockchain, and AI layers.",
        memory_persist_dir=memory_dir,
        llm_client=llm,
        use_llm_for_consolidation=bool(llm),
    )

    orchestrator = SwarmOrchestrator(swarm_name="ElysiumResearchSwarm")
    orchestrator.register_agent(researcher)
    orchestrator.register_agent(analyst)

    print("Running tasks to generate rich memory...\n")

    tasks = [
        "Research integration patterns between xMesh/NovaNet and AI agent swarms.",
        "Analyze incentive mechanisms using XCoin/QCoin for autonomous agents.",
        "Evaluate emotional memory models for long-term roleplay consistency.",
        "Propose self-improvement mechanisms based on consolidated experience.",
        "Identify risks in decentralized AI governance and propose mitigations.",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"  Task {i}...")
        await orchestrator.run_task(task, broadcast=True)

    print("\n--- Triggering consolidation (LLM or heuristic) ---")
    result = researcher.consolidate_memory()
    print(f"Result: {result}")

    print("\n--- Consolidated insights ---")
    consolidated = researcher.vector_memory.get_consolidated_memories(limit=5)
    for mem in consolidated:
        print(f"\n{mem['content'][:350]}...\n")

    print("=== LLM Consolidation Demo Complete ===")
    print("When using Grok/xAI, consolidated insights are significantly more nuanced and actionable.")


if __name__ == "__main__":
    asyncio.run(main())