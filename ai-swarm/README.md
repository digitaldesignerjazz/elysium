# AI Agent Swarm Framework

**Elysium AI Agent Swarm Framework** — Self-improving, tool-using agents with automatic schema inference.

## Custom Tool Registration (Now Even Easier)

You no longer need to write full JSON schemas. The framework automatically infers them from your function signature and type hints:

```python
agent = BaseAgent(role="Researcher", llm_client=llm)

def analyze_decentralized_system(topic: str, depth: int = 3) -> str:
    """Analyze a topic in decentralized systems."""
    return f"Analysis of {topic} at depth {depth}"

# Just register the function — schema is inferred automatically!
agent.register_function(
    name="analyze_decentralized_system",
    description="Analyzes topics related to mesh, blockchain, and AI swarms.",
    func=analyze_decentralized_system
)

# You can still provide a manual schema if you want full control
agent.register_function(
    name="advanced_tool",
    description="...",
    func=some_func,
    parameters={...}   # Optional override
)
```

Supported type hints: `str`, `int`, `float`, `bool`, `List`, `Dict` (falls back to string for complex types).

## Full Capabilities

- Automatic JSON schema inference for tools
- Native function calling with Grok/xAI
- Persistent Vector Memory + Swarm Memory
- Self-Improvement (individual + swarm level)
- Specialized agents + easy custom tools

Ready for production-grade autonomous agent systems.