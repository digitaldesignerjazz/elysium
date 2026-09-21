# Tailscale Key Confirmed — Nova Overlay

**Timestamp:** 2026-09-21T14:56Z  
**Node:** Nova (privileged overlay carrier)  
**Overlay service:** Tailscale  
**Auth-key status:** CONFIRMED by Sir (value never logged, never committed)

## What Sir confirmed
- The overlay service for the Nova-Knoten is **Tailscale**.
- Sir has a valid auth-key (`tskey-auth-…`) and confirms it is ready to use.

## What this host can do right now
- `tailscale` binary: **MISSING** (not in PATH)
- `tailscaled` binary: **MISSING**
- Network egress to `tailscale.com`: **blocked** (curl rc 7)
- Root / privileged install: **not available** in this sandbox
- `TS_AUTH_KEY` env: **not set** (and will not be set from chat — security)

## Honest status
**BLOCKED on this host.** The key is confirmed, but the carrier cannot yet be installed or started here.
A real `tailscale up --auth-key=…` must run on the Nova-Knoten itself (or a privileged host with network), not in this text sandbox.

## Next step (on Nova)
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --auth-key="$TS_AUTH_KEY" --hostname=nova-elysium --ssh
tailscale status
```
Then report the assigned Tailscale IP back so Nexus can register the overlay peer.

## Security note
The auth-key was **not** pasted into chat, **not** written to any file, and **not** committed. It stays with Sir. This document only records that confirmation happened.
