"""Self-Improvement Loop Demo

Demonstrates agents running autonomous self-improvement cycles using LLM analysis
of their own performance, reflections, and consolidated insights.
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
    print("Self-Improvement Loop Demo\n")

    memory_dir = "./memory_store"
    os.makedirs(memory_dir, exist_ok=True)

    llm = None
    if LLMClient and (os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")):
        try:
            llm = LLMClient(model="grok-beta", temperature=0.6, max_tokens=650)
            print("✓ LLM client ready — Self-improvement will use high-quality analysis.\n")
        except Exception:
            llm = None

    researcher = BaseAgent(
        role="Senior Researcher",
        persona="You are a meticulous researcher focused on decentralized systems and self-improving AI.",
        memory_persist_dir=memory_dir,
        llm_client=llm,
        use_llm_for_reasoning=True,
        use_llm_for_consolidation=True,
    )

    orchestrator = SwarmOrchestrator(swarm_name="ElysiumSelfImprovingSwarm")
    orchestrator.register_agent(researcher)

    print("Running several tasks to build experience...\n")

    tasks = [
        "Analyze how mesh networks can support persistent agent memory.",
        "Evaluate incentive models for long-running autonomous agents.",
        "Propose ways agents can improve their own reasoning over time.",
        "Reflect on the role of emotional awareness in decentralized AI systems.",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"  Task {i}...")
        await orchestrator.run_task(task, broadcast=True)

    print("\n--- Running explicit Self-Improvement Cycle ---")
    improvement_result = researcher.run_self_improvement_cycle(
        focus_area="improving long-term coherence and use of consolidated memory"
    )

    print(f"\nImprovement cycle result:")
    print(f"  Summary: {improvement_result.get('analysis_summary', improvement_result)[:200]}...")
    print(f"  Proposals generated: {improvement_result.get('proposals_generated', 0)}")
    print(f"  Improvements applied/recorded: {improvement_result.get('improvements_applied', 0)}")

    print("\n--- Final LLM Reflection ---")
    final_reflection = researcher.reflect()
    print(f"Method: {final_reflection.get('method')}")
    print(f"Insight: {final_reflection.get('content', '')[:250]}...")

    print("\n=== Self-Improvement Loop Demo Complete ===")
    print("Agents can now autonomously analyze and evolve their own behavior over time.")


if __name__ == "__main__":
    asyncio.run(main())