"""Provider-Delegationstests fuer Aura Prototype 2.0."""
from agents.aura.cycle import Aura, Perception, AnalysisProvider


class FakeXen(AnalysisProvider):
    name = "xen"

    def analyze(self, perception):
        return {
            "causes": [f"xen-cause:{s}" for s in perception.signals],
            "patterns": [f"xen-pattern:{s}" for s in perception.signals],
            "confidence": 0.5,
        }


class FakeSwarm(AnalysisProvider):
    name = "swarm"

    def analyze(self, perception):
        return {
            "causes": [f"swarm-cause:{s}" for s in perception.signals] * 2,
            "patterns": [f"swarm-pattern:{s}" for s in perception.signals] * 2,
            "confidence": 0.6,
        }


def test_fallback_provider_default():
    aura = Aura()
    out = aura.run(Perception(signals=["tor offen", "kaffee warm", "sir fragt"]))
    assert "provider=fallback" in out
    assert "confidence=0.60" in out
    assert "withheld" not in out


def test_xen_provider_delegation():
    aura = Aura(provider=FakeXen())
    out = aura.run(Perception(signals=["rand", "kante"]))
    assert "provider=xen" in out
    assert "confidence=0.50" in out
    assert "causes=2" in out


def test_swarm_provider_merge():
    aura = Aura(provider=FakeSwarm())
    out = aura.run(Perception(signals=["a", "b"]))
    assert "provider=swarm" in out
    assert "confidence=0.60" in out
    assert "causes=4" in out


def test_empty_input_withheld():
    aura = Aura(provider=FakeXen())
    out = aura.run(Perception(signals=[]))
    assert out.startswith("withheld:")
    assert "thin evidence" in out
