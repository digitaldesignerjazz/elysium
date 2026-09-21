# Xen 1.0 — Specification (v0.1)

Status: **ACTIVE** — scaffold landed, dry-run default.

## Goals
- Probe mesh and runtime state honestly.
- Test partitions (missing binaries, empty input) without crashing.
- Surface boundary cases with EU/DE caution.
- Emit a structured, machine-readable report.
- Log every run to Nexus claim `xen-1-0`.

## Non-goals
- No live mesh mutations without explicit Sir command.
- No secrets in public trees or logs.
- No auto-minting, no auto-deploy.
- No pretending a missing overlay is present.

## Safety
- Default: `dry-run`. Live gated behind `XEN_LIVE=1`.
- Every probe records ok/missing; nothing is invented.
- Boundary cases name jurisdiction and mitigation.
- Reports are append-only in the Nexus well.

## Run
```
./agents/xen/start.sh          # dry-run
XEN_LIVE=1 ./agents/xen/start.sh live   # live (Sir-confirmed)
```
