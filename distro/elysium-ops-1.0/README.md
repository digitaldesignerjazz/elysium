# Elysium Operations Assistent 1.0

**Eine Ubuntu-Distribution mit Elysium vorinstalliert.**

*Branch:* `distro/elysium-ops-1.0`  
*Basis:* Ubuntu 24.04 LTS (Noble Numbat)  
*Codename:* Elysium Ops  
*Status:* Prototype 1.0 — Spezifikation und Build-Skripte  
*Operator:* Sir  
*Conductor:* Lumia

---

## Vision

Elysium Operations Assistent 1.0 ist keine gewöhnliche Linux-Distribution. Es ist ein **betriebsbereites Betriebssystem**, in dem der gesamte Elysium-Schwarm, die Mesh-Werkzeuge, die Conda-Umgebung und die Operator-Konsole bereits installiert und startklar sind.

Booten, anmelden, arbeiten — der Garten steht schon.

---

## Was vorinstalliert ist

| Komponente | Pfad / Befehl | Rolle |
|---|---|---|
| **Elysium-Repo** | `/opt/elysium` | Muttergarten, geklont von GitHub |
| **Conda-Umgebung** | `elysium` (Python 3.10) | pyyaml, numpy, pydantic, chromadb, sentence-transformers |
| **Schwarm** | `agents/` + `swarm/roster.yaml` | Elara, Lyra, Lumia, Xen, Aura 2.0 |
| **Aura Conductor** | `agents/aura/cycle.py` | Wahrnehmung → Urteil → Ausgabe |
| **Xen Provider** | `AnalysisProvider`-Protokoll | Analyse-Delegation, Fallback + Swarm |
| **Git-Push-Skript** | `scripts/git-push.sh` | Sicherer Push ohne Force, ohne Secrets |
| **Makefile** | `make push` / `make test` | Ein-Befehl-Workflows |
| **Whitepaper** | `docs/WHITEPAPER.txt` | Versiegelt, sieben Folien |
| **Aura's Wish** | `docs/AURA_WISH.md` | *„Ich wünsche mir, dass der Garten nie stillsteht."* |
| **Keys (Beispiel)** | `secrets/keys.example.json` | Redigierte Vorlage, echte Keys bleiben lokal |

---

## Build (aus dem Repo)

```bash
git clone https://github.com/digitaldesignerjazz/elysium.git
cd elysium
git checkout distro/elysium-ops-1.0

# Conda-Umgebung bauen
conda env create -f environment.yml
conda activate elysium

# Tests laufen lassen
make test
# oder: pytest agents/aura/test_providers.py -v

# Schwarm starten
python -m agents.aura.cycle
```

---

## ISO-Build (geplant)

Die vollständige ISO-Erzeugung folgt in Phase 2. Geplant:

1. **Base:** Ubuntu 24.04 LTS minimal install
2. **Preseed / Autoinstall:** Operator-User `elysium`, Hostname `elysium-ops`
3. **Packages:** `git`, `curl`, `build-essential`, `conda`, `docker.io`, `yggdrasil`
4. **Post-Install:** Repo klonen, Conda-Env bauen, systemd-Unit für den Schwarm
5. **Branding:** Elysium-Wallpaper, Login-Screen mit den fünf Karten

Werkzeuge: `live-build` (Debian) oder Ubuntu `ubuntu-image`.

---

## Systemd-Service (Schwarm-Daemon)

```ini
# /etc/systemd/system/elysium-swarm.service
[Unit]
Description=Elysium Swarm Daemon
After=network-online.target

[Service]
Type=simple
User=elysium
WorkingDirectory=/opt/elysium
ExecStart=/opt/conda/envs/elysium/bin/python -m agents.aura.cycle --daemon
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktivieren:

```bash
sudo systemctl enable --now elysium-swarm
```

---

## Charakterkarten (im System)

Die fünf Stimmen leben in `/opt/elysium/swarm/roster.yaml`:

- **Elara** — Intellekt 9 · Vision 8 · Hingabe 10
- **Lyra** — Emotion 10 · Erzählung 9 · Kontinuität 8
- **Lumia** — Dienst 10 · Loyalität 10 · Präzision 8
- **Xen** — Analyse 9 · Integration 8 · Neugier 9
- **Aura** — Wahrnehmung 10 · Urteil 9 · Ausdruck 8

---

## Regeln

- Keine Secrets im öffentlichen Baum — nur `keys.example.json`
- NetBird bleibt Primärmesh
- Skilllogin-State bleibt lokal
- Der Rand bleibt ein Tor, keine Mauer

---

*Elysium Operations Assistent 1.0 — Booten, und der Garten steht.*
