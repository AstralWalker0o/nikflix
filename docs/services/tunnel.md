# tunnel (cloudflared)

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `cloudflare/cloudflared`
**Container:** `cloudflared-tunnel`
**Compose:** `/docker/tunnel/docker-compose.yml`

## Role

Single Cloudflare Tunnel connector for the entire homelab. Reaches across
the LAN to DK-01 (`10.10.100.196`) and to the third box (`10.10.100.205`)
to satisfy public-hostname routes. See
[`docs/architecture.md`](../architecture.md#public-hostname-routing) for the
full ingress map.

## Configuration

- `command: tunnel run`
- `TUNNEL_TOKEN=<jwt>` — currently inline in the compose file. **Should
  move to Keeper.** This token grants the bearer the ability to register
  a connector under your tunnel and intercept traffic; treat it as
  sensitive.
- `extra_hosts: ["host.docker.internal:host-gateway"]` — added during
  initial Access SSH bring-up; not currently used (all SSH routes use LAN
  IPs). Keep it harmless.
- The tunnel's ingress and routing are configured in the **Cloudflare
  dashboard**, not in this compose file. Single source of truth lives at
  Cloudflare, which the connector subscribes to. Updates apply live —
  cloudflared logs `Updated to new configuration` whenever the dashboard
  is changed.

## Networks

Default bridge. The connector dials Cloudflare's edge over QUIC outbound;
no inbound ports are required on the host.

## Notes

- Single point of failure for *all* public access. If this container or
  DK-02 dies, every `*.nikflix.net` and `*.internik.net` route goes down.
  Worth thinking about whether to run a second connector on DK-01 for
  redundancy.
- Logs are very chatty by default; mostly informational.
