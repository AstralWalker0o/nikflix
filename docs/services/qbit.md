# qbit (qBittorrent + VPN)

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `binhex/arch-qbittorrentvpn`
**Container:** `qbittorrentvpn`
**Compose:** `/docker/qbit/docker-compose.yml`
**Public:** `services.nikflix.net` (default route, no path) → host port 8082

## Ports
- `8082:8082` — qBit web UI
- `8118:8118` — Privoxy (HTTP proxy)
- `9118:9118` — Privoxy (alt)
- `58946:58946` (TCP+UDP) — torrent listen port

## Bind mounts
| Host | Container |
|---|---|
| `/docker/qbit/data` | `/data` |
| `/docker/qbit/config` | `/config` |
| `/mnt/downdisk01` | `/mnt/downdisk01` |

## Environment (highlights)
- `VPN_ENABLED=yes`, `VPN_PROV=pia`, `VPN_CLIENT=wireguard`
- `VPN_USER` / `VPN_PASS` — **PIA credentials, currently inline in
  compose**. Move to Keeper.
- `STRICT_PORT_FORWARD=yes`
- `LAN_NETWORK=192.168.1.0/24` — used by the container to allow direct LAN
  traffic without going through the VPN. **This doesn't match the actual
  LAN (`10.10.100.0/24`)** — likely a copy-paste from the upstream sample;
  worth fixing.
- `PUID=0 PGID=0` — runs as root inside container. Needed for VPN setup
  (tun device, iptables).
- `privileged: true`
- SOCKS proxy enabled with default `admin/socks` creds — harden.

## Notes
- This is the only privileged container in the stack. It's also the only one
  with VPN routing — all torrent traffic egresses through PIA.
- The `LAN_NETWORK` value should be `10.10.100.0/24` to match this network;
  current value is the upstream default.
- Container name (`qbittorrentvpn`) doesn't match the directory name (`qbit`).
  Worth aligning during restructure.
