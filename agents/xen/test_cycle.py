"""Smoke tests for Xen 1.0."""
from agents.xen.cycle import (
    Xen, Probe, PartitionTest, BoundaryCase, Verdict, Report,
)


def test_probe_hostname_returns_string():
    p = Xen().probe()
    names = {x.name for x in p}
    assert "hostname" in names
    assert "python" in names


def test_partition_tests_are_intact():
    x = Xen()
    parts = x.partition()
    assert all(p.intact for p in parts)
    assert len(parts) >= 3


def test_boundaries_have_jurisdiction():
    x = Xen()
    b = x.boundaries()
    assert all(b.jurisdiction for b in b)
    assert any("EU" in b.jurisdiction or "DE" in b.jurisdiction for b in b)


def test_full_run_returns_report():
    r = Xen().run()
    assert isinstance(r, Report)
    assert r.dry_run is True
    assert r.summary
    assert r.verdict.confidence >= 0


def test_report_json_roundtrip():
    r = Xen().run()
    import json
    parsed = json.loads(r.to_json())
    assert parsed["dry_run"] is True
    assert "probes" in parsed


def test_missing_binary_partition_honest():
    from agents.xen.cycle import test_missing_binary
    t = test_missing_binary("tailscale")
    assert t.intact is True
    assert "not installed" in t.failure_mode


def test_empty_input_partition():
    from agents.xen.cycle import test_empty_input
    t = test_empty_input()
    assert t.intact is True
    assert "no signals" in t.failure_mode
