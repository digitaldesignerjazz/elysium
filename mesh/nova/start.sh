#!/usr/bin/env bash
# Nova-Knoten Start — nur ausführen, wenn Sir NOVA_NODE=1 setzt und die Binary da ist.
set -euo pipefail

if [ "${NOVA_NODE:-0}" != "1" ]; then
  echo "Nova-Knoten: NOVA_NODE!=1 — kein Start. (Sir muss grünes Licht geben.)"
  exit 0
fi

if ! command -v tailscale >/dev/null 2>&1 && ! command -v netbird >/dev/null 2>&1; then
  echo "Nova-Knoten: keine Overlay-Binary gefunden. Installiere zuerst."
  exit 1
fi

echo "Nova-Knoten: Overlay-Start vorbereitet. (Echter up-Befehl nur mit Key.)"
# tailscale up --auth-key "$TAILSCALE_KEY"   # nur wenn Key gesetzt
# netbird up --setup-key "$NETBIRD_KEY"     # Alternative
echo "Nova bereit — warte auf Peer-Handshake."