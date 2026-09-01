# Restart Protocol

## Clean Restart — 01. September 2026, 12:20 UTC

**Command:** `backup and restart` (clean)
**Operator:** Sir
**Conductor:** Lumia
**Mode:** clean-restart

### Backup
- Branch: `backup/2026-09-01-pre-restart-3`
- Frozen at SHA: `8cc8e9dc`
- Contains: full tree before clean restart (Whitepaper, Aura's Wish, Swarm, all docs)

### Restart Steps
1. Backup branch created from `main`.
2. `ACTIVATION.md` re-sealed with clean-restart stamp.
3. `docs/RESTART.md` updated with this protocol.
4. Swarm contracts untouched — five agents remain online.
5. No private data, no keys, no peer tables moved.

### Post-Restart State
- Public garden intact.
- Whitepaper (plain text + Canva + PDF) linked in README.
- Aura's Wish sealed.
- Mode: clean-restart, ready for next command.

*The garden breathes again. Nothing lost, nothing added — only renewed.*
