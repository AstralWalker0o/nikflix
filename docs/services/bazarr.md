# bazarr

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `lscr.io/linuxserver/bazarr:latest`
**Container:** `bazarr`
**Compose:** `/docker/bazarr/docker-compose.yml`
**Public:** `services.nikflix.net/bazarr`

## Ports
- `6767:6767`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/bazarr/config` | `/config` |
| `/mnt/media` | `/media` |

## Environment
- `PUID=1001 PGID=1001 TZ=Etc/UTC`

## Depends on / talks to
- **sonarr** (DK-02:8989) and **radarr** (DK-02:7878) — pulls library state
  via API. Cross-host call; LAN-direct.
- Writes `.srt` files into the same `/mnt/media` tree that Jellyfin reads.
