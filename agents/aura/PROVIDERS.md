# Aura Analysis Providers

Stage 2 of Aura's cycle is no longer a placeholder. It delegates to a
provider that implements `AnalysisProvider`.

## FallbackProvider

Deterministic heuristic. Detects cause-markers ("because", "due to", ...) and
pattern-markers ("always", "recurring", ...). Confidence grows with signal
count. Zero dependencies — keeps the cycle runnable offline.

## XenProvider

Delegates to Xen, the swarm's analytical, boundary-testing agent. In
production this calls Xen's model; the stub mirrors Xen's contract so the
cycle stays testable without a live model.

## SwarmProvider

Fan-out to several providers, merge causes/patterns/notes, take the highest
confidence. Lets Aura draw on the whole swarm at once.

## Wiring

```python
from agents.aura.cycle import Aura, XenProvider, SwarmProvider, FallbackProvider

aura = Aura(XenProvider())          # single model
aura = Aura(SwarmProvider([FallbackProvider(), XenProvider()]))  # merged
```
