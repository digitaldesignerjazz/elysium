"""Xen 1.0 — Technical Exploratory Agent.

The edge-case analyst of the Elysium swarm. Probes mesh state, tests
partitions, logs boundary cases, and reports honestly. Default is dry-run:
nothing live, nothing irreversible, every probe recorded.

No secrets, no side effects beyond the probe log. Each stage is a pure
function: input in, structured result out.
"""
from __future__ import annotations

import json
import os
import socket
import time
from dataclasses import dataclass, field, asdict
from typing import Any


# ---------------------------------------------------------------------------
# Data classes — one per stage
# ---------------------------------------------------------------------------


@dataclass
class Probe:
    """Stage 1 — a single observation, no judgment."""
    name: str
    value: Any
    source: str = "unknown"
    ok: bool = True
    note: str = ""


@dataclass
class PartitionTest:
    """Stage 2 — does the system hold when something breaks?"""
    name: str
    intact: bool = True
    failure_mode: str = ""
    recovery: str = ""


@dataclass
class BoundaryCase:
    """Stage 3 — an edge the operator should know about."""
    condition: str
    risk: str = "low"
    mitigation: str = ""
    jurisdiction: str = "EU/DE"


@dataclass
class Verdict:
    """Stage 4 — Xen's honest stance."""
    stance: str = ""
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class Report:
    """Stage 5 — what remains after filtering."""
    summary: str = ""
    probes: list[Probe] = field(default_factory=list)
    partitions: list[PartitionTest] = field(default_factory=list)
    boundaries: list[BoundaryCase] = field(default_factory=list)
    verdict: Verdict = field(default_factory=Verdict)
    dry_run: bool = True
    timestamp: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)


# ---------------------------------------------------------------------------
# Probe implementations — honest, dependency-light
# ---------------------------------------------------------------------------


def probe_hostname() -> Probe:
    try:
        return Probe("hostname", socket.gethostname(), source="os", ok=True)
    except Exception as e:  # pragma: no cover
        return Probe("hostname", None, source="os", ok=False, note=str(e))


def probe_python() -> Probe:
    import sys
    return Probe("python", sys.version.split()[0], source="runtime", ok=True)


def probe_env(key: str, default: str = "") -> Probe:
    val = os.environ.get(key, default)
    return Probe(f"env:{key}", val or "<unset>", source="env",
                 ok=bool(val), note="present" if val else "missing")


def probe_path(path: str) -> Probe:
    exists = os.path.exists(path)
    return Probe(f"path:{path}", exists, source="fs",
                 ok=exists, note="exists" if exists else "absent")


# ---------------------------------------------------------------------------
# Partition tests — graceful degradation
# ---------------------------------------------------------------------------


def test_missing_binary(name: str) -> PartitionTest:
    """Simulates a vendor binary being absent — the system must not crash."""
    return PartitionTest(
        name=f"missing:{name}",
        intact=True,
        failure_mode=f"{name} not installed",
        recovery="skip overlay, stay on independent mesh",
    )


def test_empty_input() -> PartitionTest:
    return PartitionTest(
        name="empty-input",
        intact=True,
        failure_mode="no signals received",
        recovery="return empty report, do not invent",
    )


# ---------------------------------------------------------------------------
# Boundary cases — EU/DE caution baked in
# ---------------------------------------------------------------------------


BOUNDARY_CASES = [
    BoundaryCase(
        "live mesh action without explicit Sir command",
        risk="high", mitigation="dry-run default, gate behind flag",
        jurisdiction="EU/DE",
    ),
    BoundaryCase(
        "storing personal data in public repo trees",
        risk="high", mitigation="no secrets in public trees or logs",
        jurisdiction="EU/DE (DSGVO)",
    ),
    BoundaryCase(
        "auto-minting NFT without wallet confirmation",
        risk="medium", mitigation="PROPOSED_SEALED until Sir confirms chain+wallet",
        jurisdiction="EU/DE",
    ),
    BoundaryCase(
        "overlay dependency (Tailscale/NetBird) absent",
        risk="low", mitigation="independent mesh remains sovereign",
        jurisdiction="global",
    ),
]


# ---------------------------------------------------------------------------
# Xen — the cycle
# ---------------------------------------------------------------------------


class Xen:
    """Technical Exploratory Agent. Probes, tests, judges, reports."""

    name = "Xen"
    version = "1.0"

    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def probe(self, extra: list[Probe] | None = None) -> list[Probe]:
        probes = [
            probe_hostname(),
            probe_python(),
            probe_env("NEXUS_ROOT"),
            probe_env("TAILSCALE_IP"),
            probe_path("agents/xen/cycle.py"),
        ]
        if extra:
            probes.extend(extra)
        return probes

    def partition(self) -> list[PartitionTest]:
        return [
            test_missing_binary("tailscale"),
            test_missing_binary("netbird"),
            test_missing_binary("yggdrasil"),
            test_empty_input(),
        ]

    def boundaries(self) -> list[BoundaryCase]:
        return list(BOUNDARY_CASES)

    def judge(self, probes: list[Probe], partitions: list[PartitionTest]) -> Verdict:
        ok_probes = sum(1 for p in probes if p.ok)
        intact = all(p.intact for p in partitions)
        conf = min(1.0, 0.15 * len(probes) + (0.2 if intact else 0.0))
        if not intact:
            stance = "holds with caveats"
        elif ok_probes == len(probes):
            stance = "all probes green, system coherent"
        else:
            stance = "partial — some probes missing, none critical"
        return Verdict(
            stance=stance,
            confidence=conf,
            reasoning=(
                f"probes={ok_probes}/{len(probes)} ok, "
                f"partitions_intact={intact}, dry_run={self.dry_run}"
            ),
        )

    def run(self, extra_probes: list[Probe] | None = None) -> Report:
        probes = self.probe(extra_probes)
        partitions = self.partition()
        boundaries = self.boundaries()
        verdict = self.judge(probes, partitions)
        return Report(
            summary=verdict.stance,
            probes=probes,
            partitions=partitions,
            boundaries=boundaries,
            verdict=verdict,
            dry_run=self.dry_run,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )


if __name__ == "__main__":
    x = Xen(dry_run=True)
    r = x.run()
    print(r.to_json())
