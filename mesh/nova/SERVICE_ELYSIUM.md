# Service: elysium (svc:elysium)

**Status:** DEFINED in Tailscale admin console. Host pending.

## Service details (from admin console)
- Endpoint: `tcp:8080`
- Tailscale IPv4 (TailVIP): `100.71.9.93`
- Tailscale IPv6: `fd7a:115c:a1e0::5f2e:95e`
- Short domain: `elysium`
- Full domain: `elysium.elephant-fahrenheit.ts.net`
- Description: elysium net

## Next step (on the Nova host)
Advertise this node as the service host:

```bash
sudo tailscale serve --service=svc:elysium --tcp=8080 127.0.0.1:8080
```

Then approve the host in the admin console (or via auto-approver). After approval the service is reachable at `elysium.elephant-fahrenheit.ts.net:8080` or `100.71.9.93:8080`.

Drain / clear:
```bash
sudo tailscale serve drain svc:elysium
sudo tailscale serve clear svc:elysium
```
