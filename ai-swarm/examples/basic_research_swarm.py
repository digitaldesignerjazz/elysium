"""Basic Research Swarm Example

Demonstrates a simple multi-agent research swarm using the Elysium AI Agent Swarm Framework.
Run this to verify the core is working.
"""

import asyncio
from ai_swarm.core.base_agent import BaseAgent
from ai_swarm.core.swarm_orchestrator import SwarmOrchestrator


async def main():
    print("=== Elysium AI Agent Swarm Framework - Basic Research Swarm ===\n")

    # Create specialized agents
    researcher = BaseAgent(
        role="Senior Researcher",
        persona="You are a meticulous, curious researcher focused on decentralized technologies, mesh networks, and self-improving AI. You always cite sources and think in systems.",
    )

    analyst = BaseAgent(
        role="Systems Analyst",
        persona="You analyze complex systems, identify connections between mesh, blockchain, and AI layers, and propose elegant architectures.",
    )

    synthesizer = BaseAgent(
        role="Knowledge Synthesizer",
        persona="You synthesize findings from multiple agents into clear, actionable insights and beautiful summaries.",
    )

    # Initialize orchestrator and register agents
    orchestrator = SwarmOrchestrator(swarm_name="ElysiumResearchSwarm_v0.1")
    orchestrator.register_agent(researcher)
    orchestrator.register_agent(analyst)
    orchestrator.register_agent(synthesizer)

    print("Agents registered:")
    for state in orchestrator.list_agents():
        print(f"  - {state['role']} (id={state['agent_id'][:8]})")

    # Run a research task (broadcast to all)
    print("\n--- Running broadcast research task ---\n")
    task = "Research and analyze the current state of decentralized mesh networks (xMesh/NovaNet/QNET) and their integration potential with AI agent swarms and blockchain (XCoin/QCoin)."

    result = await orchestrator.run_task(task, broadcast=True)

    print("Task results:")
    for r in result["results"]:
        print(f"\n[{r['role']}]\n{r['result']['content'][:300]}...\n")

    # Trigger swarm-wide reflection
    print("\n--- Swarm Reflection ---")
    reflection = await orchestrator.reflect_swarm()
    print(f"Swarm '{reflection['swarm']}' completed reflection with {reflection['agent_count']} agents.")

    print("\n=== Basic Research Swarm Complete ===")
    print("Next steps: Extend agents with real LLM calls, add memory persistence, integrate with xMesh and QCoin.")


if __name__ == "__main__":
    asyncio.run(main())