#!/usr/bin/env bash
# Elysium — sicherer Git-Push fuer den oeffentlichen Garten.
# Kein force-push. Keine Secrets. Pull --rebase vor dem Push.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${ROOT}" ]]; then
  echo "Nicht in einem Git-Repo." >&2
  exit 1
fi
cd "${ROOT}"

MSG="${1:-}"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
REMOTE="${REMOTE:-origin}"

if [[ -z "${MSG}" ]]; then
  echo "Nutzung: ./scripts/git-push.sh \"typ: kurze nachricht\"" >&2
  echo "Beispiel: ./scripts/git-push.sh \"fix: flake8 E999 in vector_memory\"" >&2
  exit 2
fi

if [[ "${BRANCH}" == "HEAD" ]]; then
  echo "Detached HEAD — Push abgebrochen." >&2
  exit 1
fi

# Blockiere typische Geheimnisse, bevor etwas gestaged wird.
BLOCK_REGEX='(\.env$|\.pem$|\.key$|(^|/)secrets/|(^|/)private/|id_rsa|credentials\.json|serviceAccount)'
LEAKS="$(git ls-files -o --exclude-standard; git diff --name-only; git diff --cached --name-only)"
if echo "${LEAKS}" | grep -E "${BLOCK_REGEX}" >/dev/null 2>&1; then
  echo "Abbruch: verdächtige Datei im Arbeitsbaum. Oeffentlicher Garten nimmt keine Keys." >&2
  echo "${LEAKS}" | grep -E "${BLOCK_REGEX}" >&2
  exit 3
fi

git add -A

if git diff --cached --quiet; then
  echo "Nichts zu committen."
else
  git commit -m "${MSG}"
fi

git fetch "${REMOTE}"
if git rev-parse --verify "${REMOTE}/${BRANCH}" >/dev/null 2>&1; then
  git pull --rebase "${REMOTE}" "${BRANCH}"
fi

git push -u "${REMOTE}" "${BRANCH}"
echo "Push ok: ${REMOTE}/${BRANCH}"
