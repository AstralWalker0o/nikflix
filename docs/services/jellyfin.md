# jellyfin

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `lscr.io/linuxserver/jellyfin:latest`
**Container:** `jellyfin`
**Compose:** `/docker/jellyfin/docker-compose.yml`
**Public:** _(not in cloudflared ingress directly)_ — exposed on host port
8096 only. Likely accessed over LAN or via NPM.

## Ports
- `8096:8096` — HTTP web UI / API
- `8920:8920` — HTTPS
- `7359:7359/udp` — auto-discovery
- `1900:1900/udp` — DLNA SSDP

## Bind mounts
| Host | Container |
|---|---|
| `/docker/jellyfin/config` | `/config` |
| `/mnt/media` | `/media` |

## Environment
- `PUID=1001 PGID=1001 TZ=Etc/UTC`
- `JELLYFIN_PublishedServerUrl=nikflix.net` — used in client discovery
  responses.

## Depends on
- `/mnt/media` — populated by the *arr/qBit/SABnzbd stack on DK-02. Implies
  `/mnt/media` is a shared filesystem mounted on both hosts (NFS/SMB/etc.).
  Confirm what the underlying mount is.
- **bazarr** (same host) writes subtitle sidecar files into the same media
  tree.

## Notes
- Hardware acceleration not configured; check whether the host has a GPU
  worth wiring through.
- Image is `linuxserver`, latest tag. No version pin.
