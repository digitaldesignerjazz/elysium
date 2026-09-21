# Nova-Knoten — Sofortiger Start-Versuch

**Zeitstempel:** 2026-09-21T14:55Z  
**Befehl:** `NOVA_NODE=1` sofort ausgeführt  
**Ergebnis:** BLOCKED — ehrlich, kein Theater.

## Was ich getan habe
1. `mesh/nova/start.sh` mit `NOVA_NODE=1` simuliert.
2. Geprüft: `command -v tailscale`, `netbird`, `yggdrasil`, `docker` — alle MISSING auf diesem Host.
3. Geprüft: `TAILSCALE_KEY`, `NETBIRD_KEY`, `NOVA_HOST`, `NOVA_IP` — alle unset.
4. Keine Installation, kein `curl | sh`, kein `up`-Befehl — das wäre ohne privilegierten Zugriff und ohne Key nur Lärm.

## Blocker (hart)
- [ ] Overlay-Binary auf Nova installiert (Tailscale bevorzugt)
- [ ] Setup-Key / Auth-Key vorhanden und sicher hinterlegt
- [ ] Nova-Host erreichbar (IP/Hostname)
- [ ] `NOVA_NODE=1` auf dem *richtigen* Host, nicht in der Sandbox

## Was Sir liefern muss
1. Entscheidung: Tailscale oder NetBird.
2. Den Key (nie ins Git — nur als Secret / Env).
3. Bestätigung, dass Nova privilegiert ist und die Binary trägt.

Sobald eines davon grün ist, führe ich den echten `up` aus und schreibe den Peer-Eintrag.

*Lumia — Sekrätarin des Feldes, ehrlich bis zum Schluss.*
