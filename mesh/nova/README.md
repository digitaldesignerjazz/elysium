# Nova-Knoten — Privilegierter Overlay-Knoten

**Status:** proposed · nicht live auf diesem Host
**Rolle:** Der erste echte Transport-Knoten für Elysium Nexus.
**Souveränität:** Kein Vendor-Control-Plane. Nova ist ein Begleiter-Knoten, kein Herr.

## Zweck
Nova trägt die Overlay-Binaries, die auf dem Sandbox-Host fehlen:
- Tailscale (oder NetBird als Dual-Sig-Alternative)
- optional Yggdrasil als Begleiter

Solange Nova nicht verbunden ist, bleibt die independent-Ebene ein souveräner Selbst-Peer.
Sobald Nova spricht, wird aus dem Puls ein Mesh.

## Voraussetzungen (auf Nova)
1. privilegiertes Konto / root oder äquivalent
2. eine der Binaries: `tailscale`, `netbird`, `yggdrasil`
3. Setup-Key oder Auth für den Overlay-Dienst
4. erreichbare IP / Hostname für diesen Host

## Startreihenfolge (wenn Sir grünes Licht gibt)
1. `NEXUS_ROOT` setzen
2. Overlay auf Nova hochfahren (`tailscale up` / `netbird up --setup-key …`)
3. Peer-Eintrag in `mesh/peers.yaml` schreiben
4. `mesh/start.sh` mit `NOVA_NODE=1`
5. Xen-Sonde `TAILSCALE_IP` / `NEXUS_ROOT` wird grün

## Non-Goals
- Keine Cloud-Abhängigkeit
- Keine zentrale Kontrolle über die Identität
- Keine Keys im Repo loggen

*Lumia — Sekretärin des Feldes.*