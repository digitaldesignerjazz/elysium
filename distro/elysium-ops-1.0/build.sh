#!/usr/bin/env bash
# Elysium Operations Assistent 1.0 — Build-Skript
# Baut die Conda-Umgebung, klont das Repo und startet den Schwarm.
set -euo pipefail

REPO_URL="https://github.com/digitaldesignerjazz/elysium.git"
INSTALL_DIR="${ELYSIUM_HOME:-/opt/elysium}"
BRANCH="distro/elysium-ops-1.0"

echo "==> Elysium Ops 1.0 Build"
echo "    Repo:   $REPO_URL"
echo "    Branch: $BRANCH"
echo "    Ziel:   $INSTALL_DIR"

# 1. Repo klonen oder aktualisieren
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "==> Repo existiert — pull"
    git -C "$INSTALL_DIR" fetch --all
    git -C "$INSTALL_DIR" checkout "$BRANCH"
    git -C "$INSTALL_DIR" pull --ff-only
else
    echo "==> Clone"
    git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

# 2. Conda-Umgebung
if command -v conda >/dev/null 2>&1; then
    echo "==> Conda-Umgebung 'elysium' bauen"
    conda env create -f "$INSTALL_DIR/environment.yml" || conda env update -f "$INSTALL_DIR/environment.yml"
else
    echo "!! conda nicht gefunden — überspringe Env-Build"
fi

# 3. Tests
if command -v conda >/dev/null 2>&1; then
    echo "==> Tests"
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate elysium
    cd "$INSTALL_DIR"
    pytest agents/aura/test_providers.py -v || echo "!! Tests fehlgeschlagen — weiter ohne Blockade"
fi

# 4. Schwarm-Daemon (optional)
if [ "${1:-}" = "--daemon" ]; then
    echo "==> Starte Schwarm-Daemon"
    exec python -m agents.aura.cycle --daemon
fi

echo "==> Fertig. Starte mit:"
echo "    cd $INSTALL_DIR && python -m agents.aura.cycle"
