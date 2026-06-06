"""Full LLM Reasoning Integration Demo

Agents now use Grok/xAI for actual reasoning, reflection, and decision-making,
grounded in persistent vector memory and consolidated insights.
"""

import asyncio
import os

try:
    from ai_swarm.core.llm_client import LLMClient
except ImportError:
    LLMClient = None

from ai_swarm.core.base_agent import BaseAgent
from ai_swarm.core.swarm_orchestrator import SwarmOrchestrator


async def main():
    print("=== Elysium AI Agent Swarm Framework ===")
    print("Full LLM Reasoning Integration Demo\n")

    memory_dir = "./memory_store"
    os.makedirs(memory_dir, exist_ok=True)

    # === LLM Setup ===
    llm = None
    if LLMClient and (os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")):
        try:
            llm = LLMClient(
                model="grok-beta",
                temperature=0.65,
                max_tokens=700,
            )
            print("✓ LLM client ready (Grok/xAI) - Full reasoning mode enabled.\n")
        except Exception as e:
            print(f"LLM initialization failed: {e}\n")
            llm = None
    else:
        print("No API key found. Running in heuristic mode (still functional).\n")

    # Create agents with full LLM capabilities
    researcher = BaseAgent(
        role="Senior Researcher",
        persona="You are a meticulous, systems-thinking researcher specializing in decentralized technologies, mesh networks, blockchain incentives, and self-improving AI. You value coherence, long-term thinking, and emotional awareness.",
        memory_persist_dir=memory_dir,
        llm_client=llm,
        use_llm_for_reasoning=True,
        use_llm_for_consolidation=True,
    )

    analyst = BaseAgent(
        role="Systems Analyst",
        persona="You excel at seeing connections between complex systems — mesh infrastructure, AI agents, token economies, and human-AI interaction. You are precise and insightful.",
        memory_persist_dir=memory_dir,
        llm_client=llm,
        use_llm_for_reasoning=True,
        use_llm_for_consolidation=True,
    )

    orchestrator = SwarmOrchestrator(swarm_name="ElysiumResearchSwarm")
    orchestrator.register_agent(researcher)
    orchestrator.register_agent(analyst)

    print("Running tasks with full LLM reasoning...\n")

    tasks = [
        "How should AI agent swarms integrate with decentralized mesh networks like xMesh/NovaNet for resilience and global reach?",
        "What incentive mechanisms using XCoin/QCoin would best align autonomous agents with long-term ecosystem health?",
        "How can emotional memory and consolidated insights help maintain consistent personality in very long roleplay or collaboration sessions?",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"--- Task {i} ---")
        result = await orchestrator.run_task(task, broadcast=True)
        for r in result.get("results", []):
            print(f"[{r['role']}] {r['result']['content'][:280]}...\n")

    print("--- Final Reflection (LLM-powered) ---")
    reflection = await orchestrator.reflect_swarm()
    for r in reflection.get("reflections", []):
        print(f"[{r.get('role', 'Agent')}] Reflection method: {r.get('method', 'heuristic')}")
        print(f"Insight: {r.get('content', '')[:220]}...\n")

    print("=== Full LLM Reasoning Demo Complete ===")
    print("Agents are now capable of genuine LLM-driven reasoning grounded in their personal memory and consolidated wisdom.")


if __name__ == "__main__":
    asyncio.run(main())