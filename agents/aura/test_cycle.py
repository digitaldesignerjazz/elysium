"""Smoke tests for Aura Prototype 1.0."""
from agents.aura.cycle import Aura


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
