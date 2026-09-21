# Nova-Knoten SPEC v1.0-proposed

## Ziel
Nova ist der privilegierte Knoten, der dem independent Mesh einen echten Transport gibt.

## Anforderungen
- Läuft auf einem Host mit Overlay-Binary (Tailscale bevorzugt, NetBird als Alternative).
- Hält keine Herrschaft über Elysium-Identität.
- Publiziert nur Fingerprint und erreichbare Adresse.

## Sicherheit
- EU/DE-konform: keine unnötige Datenabgabe.
- Keys nur auf Nova, nie im Git.
- Auditierbar über Nexus-Claims.

## Offene Punkte
- [ ] Tatsächliche IP / Hostname von Nova
- [ ] Gewählter Overlay-Dienst (Tailscale vs NetBird)
- [ ] Setup-Key-Verwaltung
- [ ] Erste Peer-Verbindung testen