"""Smoke tests for Aura Prototype 2.0."""
from agents.aura.cycle import Aura, FallbackProvider, XenProvider, SwarmProvider


def test_perceive_collects_signals():
    a = Aura()
    p = a.perceive(["a", "b"])
    assert p.signals == ["a", "b"]


def test_full_cycle_returns_output():
    a = Aura()
    out = a.run(["signal-one", "signal-two"])
    assert out.message
    assert out.dense is True


def test_low_confidence_withholds():
    a = Aura()
    out = a.run([])
    assert "withheld" in out.message


def test_xen_provider_fills_analysis():
    a = Aura(XenProvider())
    out = a.run(["edge case", "boundary hit"], source="mesh")
    assert "xen" in out.message
    assert out.message  # non-empty


def test_swarm_provider_merges():
    a = Aura(SwarmProvider([FallbackProvider(), XenProvider()]))
    out = a.run(["signal"], source="swarm")
    assert "swarm" in out.message or "confidence" in out.message


def test_fallback_detects_cause_markers():
    a = Aura(FallbackProvider())
    out = a.run(["failure because of timeout"])
    assert "confidence" in out.message
