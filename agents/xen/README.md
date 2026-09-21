# Xen — Technical Exploratory Agent

Edge-case analyst of the Elysium swarm. Probes, partitions, boundaries.

- `cycle.py` — the five-stage cycle (probe → partition → boundary → verdict → report)
- `start.sh` — idempotent entrypoint, dry-run default
- `SPEC.md` — v0.1 goals, non-goals, safety
- `SKILL.md` — public contract
- `test_cycle.py` — smoke tests

Default: `./agents/xen/start.sh`. Live: `XEN_LIVE=1 ./agents/xen/start.sh live`.
