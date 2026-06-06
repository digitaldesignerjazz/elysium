# AI Agent Swarm Framework

**Elysium AI Agent Swarm Framework** — Self-improving, tool-using, swarm-intelligent agents.

## Core Capabilities

- LLM-powered reasoning (Grok/xAI) with memory context
- Persistent individual + **Swarm Memory**
- Memory Consolidation (heuristic + LLM)
- Individual & Swarm-Level Self-Improvement
- **Tool Use via Function Calling**
- Specialized Agents + easy custom tool registration

## Custom Tool Registration

Easily add your own tools:

```python
agent = BaseAgent(role="Researcher", llm_client=llm)

def my_tool(query: str):
    return f"Result for {query}"

agent.register_function(
    name="my_custom_tool",
    description="My custom capability.",
    func=my_tool
)

# Or pass at init
agent = BaseAgent(..., tools=[custom_tool1, custom_tool2])
```

The agent will automatically use registered tools via function calling when appropriate.

## Quick Start

```bash
pip install -r requirements.txt
python examples/basic_research_swarm.py
```

## Full Feature Set

- ToolRegistry + native function calling
- VectorMemory + SwarmMemory
- Self-Improvement (individual + swarm)
- Specialized agents (Researcher, Companion, Creative)
- SwarmOrchestrator

Ready for building advanced autonomous agent systems.