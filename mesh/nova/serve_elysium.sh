#!/usr/bin/env bash
# Advertise the elysium Tailscale Service from this host.
# Run on the Nova node where the local service listens on :8080.
set -euo pipefail

if ! command -v tailscale >/dev/null 2>&1; then
  echo "tailscale binary missing" >&2
  exit 1
fi

sudo tailscale serve --service=svc:elysium --tcp=8080 127.0.0.1:8080
echo "svc:elysium advertised. Approve the host in the admin console if prompted."
