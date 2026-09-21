#!/usr/bin/env bash
# Xen 1.0 — entrypoint. Idempotent, dry-run by default.
# Live actions require: XEN_LIVE=1
set -euo pipefail

ROOT="${NEXUS_ROOT:-.}"
cd "$ROOT"

MODE="${1:-dry-run}"

if [[ "$MODE" == "live" && "${XEN_LIVE:-0}" != "1" ]]; then
  echo "Xen: live mode refused. Set XEN_LIVE=1 to confirm." >&2
  exit 2
fi

export PYTHONPATH="${PYTHONPATH:-.}"

if [[ "$MODE" == "live" ]]; then
  python3 -m agents.xen.cycle --live
else
  python3 -m agents.xen.cycle
fi
