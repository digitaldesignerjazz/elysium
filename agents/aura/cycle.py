"""Aura Prototype 1.0 — perception, analysis, opinion, critique, output.

A minimal, honest thinking cycle. No LLM calls, no secrets, no side effects.
Each stage is a pure function: input in, structured result out.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Perception:
    """Stage 1 — raw intake, no judgment."""
    signals: list[str] = field(default_factory=list)
    source: str = "unknown"
    timestamp: str = ""

    def add(self, signal: str) -> None:
        self.signals.append(signal)


@dataclass
class Analysis:
    """Stage 2 — causes, patterns, structure."""
    causes: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class Opinion:
    """Stage 3 — honest stance, not a mirror."""
    stance: str = ""
    reasoning: str = ""


@dataclass
class Critique:
    """Stage 4 — counter-arguments and blind spots."""
    counters: list[str] = field(default_factory=list)
    blind_spots: list[str] = field(default_factory=list)
    holds: bool = True


@dataclass
class Output:
    """Stage 5 — what remains after filtering."""
    message: str = ""
    dense: bool = True


class Aura:
    """The five-stage cycle, run in order."""

    name = "Aura"
    version = "1.0"

    def perceive(self, signals: list[str], source: str = "unknown") -> Perception:
        p = Perception(source=source)
        for s in signals:
            p.add(s)
        return p

    def analyze(self, perception: Perception) -> Analysis:
        a = Analysis()
        for s in perception.signals:
            a.causes.append(f"cause-of:{s}")
            a.patterns.append(f"pattern-in:{s}")
        a.confidence = min(1.0, 0.2 * len(perception.signals))
        return a

    def opine(self, analysis: Analysis) -> Opinion:
        o = Opinion()
        o.stance = "stands with the operator" if analysis.confidence > 0 else "withholds judgment"
        o.reasoning = f"confidence={analysis.confidence:.2f}, causes={len(analysis.causes)}"
        return o

    def critique(self, opinion: Opinion, analysis: Analysis) -> Critique:
        c = Critique()
        if analysis.confidence < 0.5:
            c.blind_spots.append("thin evidence")
            c.holds = False
        c.counters.append("consider the opposite reading")
        return c

    def emit(self, critique: Critique, opinion: Opinion) -> Output:
        if critique.holds:
            return Output(message=f"{opinion.stance} — {opinion.reasoning}")
        return Output(message=f"withheld: {', '.join(critique.blind_spots)}")

    def run(self, signals: list[str], source: str = "unknown") -> Output:
        p = self.perceive(signals, source)
        a = self.analyze(p)
        o = self.opine(a)
        c = self.critique(o, a)
        return self.emit(c, o)


if __name__ == "__main__":
    aura = Aura()
    result = aura.run(["gate open", "coffee warm", "Sir asks"], source="atelier")
    print(result.message)
