# Git-Push — Elysium

Oeffentlicher Garten. Keine Keys, keine Peer-Tabellen, keine privaten Familiendaten.

## Ein Befehl

```bash
./scripts/git-push.sh "fix: kurze nachricht"
```

oder

```bash
make push MSG="docs: GIT_PUSH Protokoll"
```

## Was das Skript tut

1. Prueft, ob du in einem Git-Repo bist.
2. Blockiert `.env`, `.pem`, `.key`, `secrets/`, `private/`.
3. `git add -A`
4. Commit nur wenn es Aenderungen gibt.
5. `git pull --rebase` gegen den Remote-Branch.
6. `git push -u origin <branch>`

Kein `--force`. Kein Commit ohne Nachricht.

## Nach dem Push

Jeder Push auf `main` startet den Workflow **Python Package using Conda**.

- Workflow: `.github/workflows/python-package-conda.yml`
- Manuell: Actions-Tab, *Run workflow*

## Remote

```bash
git remote -v
# origin  https://github.com/digitaldesignerjazz/elysium.git
```
