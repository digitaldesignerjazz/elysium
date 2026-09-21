# Xen 1.0 — Start Protocol

Status: **ACTIVE** — scaffold landed 2026-09-21.

## What exists
- `agents/xen/cycle.py` — five-stage cycle: probe, partition, boundary, verdict, report.
- `agents/xen/start.sh` — idempotent entrypoint, dry-run default, `XEN_LIVE=1` for live.
- `agents/xen/SPEC.md` — v0.1 goals, non-goals, EU/DE safety.
- `agents/xen/test_cycle.py` — smoke tests.
- `agents/xen/SKILL.md` — public contract v1.0.
- Nexus claim `xen-1-0` for continuity.

## Run
```
./agents/xen/start.sh                 # dry-run (default)
XEN_LIVE=1 ./agents/xen/start.sh live  # live, Sir-confirmed only
python3 -m agents.xen.cycle           # direct
```

## Honest note
Aura has perception + analysis. Xen has probes + partitions + boundaries.
Both stay dry-run until Sir says otherwise. No theater.
