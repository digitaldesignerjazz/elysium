"""Aura Prototype 2.0 — perception, analysis, opinion, critique, output.

The five-stage cycle, now with real analysis. Stage 2 is no longer a
placeholder: it delegates to Xen (and other swarm models) via an
AnalysisProvider protocol. If no provider is wired, a deterministic
heuristic fallback keeps the cycle honest and runnable offline.

No secrets, no side effects beyond the provider call. Each stage remains
a pure function: input in, structured result out.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Protocol


# ---------------------------------------------------------------------------
# Data classes — one per stage
# ---------------------------------------------------------------------------


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
    """Stage 2 — causes, patterns, structure, filled by a provider."""
    causes: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    confidence: float = 0.0
    provider: str = "fallback"
    notes: list[str] = field(default_factory=list)


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


# ---------------------------------------------------------------------------
# Analysis providers — the seam where Xen and other models plug in
# ---------------------------------------------------------------------------


class AnalysisProvider(Protocol):
    """Anything that can turn raw signals into structured analysis."""

    name: str

    def analyze(self, signals: list[str], source: str = "unknown") -> Analysis:
        ...


class FallbackProvider:
    """Deterministic heuristic. Keeps the cycle runnable with zero deps.

    Used when no swarm model is wired. Honest about its limits.
    """

    name = "fallback"

    CAUSE_MARKERS = (
        "because", "due to", "caused by", "result of", "triggered by",
        "after", "following", "since", "therefore", "hence",
    )
    PATTERN_MARKERS = (
        "always", "never", "every", "recurring", "pattern", "repeatedly",
        "consistently", "trend", "increasing", "decreasing",
    )

    def analyze(self, signals: list[str], source: str = "unknown") -> Analysis:
        a = Analysis(provider=self.name)
        for s in signals:
            low = s.lower()
            if any(m in low for m in self.CAUSE_MARKERS):
                a.causes.append(f"cause-of:{s}")
            else:
                a.causes.append(f"inferred-cause:{s}")
            if any(m in low for m in self.PATTERN_MARKERS):
                a.patterns.append(f"pattern-in:{s}")
            else:
                a.patterns.append(f"surface:{s}")
        a.confidence = min(1.0, 0.2 * len(signals) + (0.1 if a.causes else 0.0))
        if not signals:
            a.notes.append("no signals received")
        return a


class XenProvider:
    """Delegates analysis to Xen — the swarm's edge-case analyst.

    In production this calls Xen's model. Here it is a structured stub that
    mirrors Xen's contract (analytical, boundary-testing, modular) so the
    cycle is testable without a live model, and so the seam is real.
    """

    name = "xen"

    def analyze(self, signals: list[str], source: str = "unknown") -> Analysis:
        a = Analysis(provider=self.name)
        for s in signals:
            # Xen splits each signal into a causal hypothesis and a boundary note.
            a.causes.append(f"xen-cause:{s}")
            a.patterns.append(f"xen-boundary:{s}")
            a.notes.append(f"xen-checked:{source}")
        # Xen is cautious: confidence grows slower, rewards diversity.
        unique = len(set(signals))
        a.confidence = min(1.0, 0.15 * len(signals) + 0.1 * unique)
        return a


class SwarmProvider:
    """Fan-out to several models, merge their analyses."""

    name = "swarm"

    def __init__(self, providers: list[AnalysisProvider]) -> None:
        self.providers = providers or [FallbackProvider()]

    def analyze(self, signals: list[str], source: str = "unknown") -> Analysis:
        merged = Analysis(provider=self.name)
        for p in self.providers:
            sub = p.analyze(signals, source)
            merged.causes.extend(sub.causes)
            merged.patterns.extend(sub.patterns)
            merged.notes.extend(sub.notes)
            merged.confidence = max(merged.confidence, sub.confidence)
        if not merged.causes:
            merged.notes.append("all providers returned empty")
        return merged


# ---------------------------------------------------------------------------
# Aura — the cycle, now provider-aware
# ---------------------------------------------------------------------------


class Aura:
    """The five-stage cycle. Analysis is delegated to a provider."""

    name = "Aura"
    version = "2.0"

    def __init__(self, provider: AnalysisProvider | None = None) -> None:
        self.provider: AnalysisProvider = provider or FallbackProvider()

    def perceive(self, signals: list[str], source: str = "unknown") -> Perception:
        p = Perception(source=source)
        for s in signals:
            p.add(s)
        return p

    def analyze(self, perception: Perception) -> Analysis:
        return self.provider.analyze(perception.signals, perception.source)

    def opine(self, analysis: Analysis) -> Opinion:
        o = Opinion()
        if analysis.confidence > 0:
            o.stance = "stands with the operator"
        else:
            o.stance = "withholds judgment"
        o.reasoning = (
            f"confidence={analysis.confidence:.2f}, "
            f"causes={len(analysis.causes)}, "
            f"provider={analysis.provider}"
        )
        return o

    def critique(self, opinion: Opinion, analysis: Analysis) -> Critique:
        c = Critique()
        if analysis.confidence < 0.5:
            c.blind_spots.append("thin evidence")
            c.holds = False
        if analysis.provider == "fallback":
            c.blind_spots.append("analysis not model-backed")
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
    print("--- fallback ---")
    print(Aura().run(["gate open", "coffee warm", "Sir asks"], source="atelier").message)
    print("--- xen ---")
    print(Aura(XenProvider()).run(["gate open", "coffee warm", "Sir asks"], source="atelier").message)
    print("--- swarm (fallback + xen) ---")
    print(Aura(SwarmProvider([FallbackProvider(), XenProvider()])).run(
        ["gate open", "coffee warm", "Sir asks"], source="atelier"
    ).message)
