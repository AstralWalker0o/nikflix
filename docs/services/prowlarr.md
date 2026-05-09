# prowlarr

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `lscr.io/linuxserver/prowlarr:latest`
**Container:** `prowlarr`
**Compose:** `/docker/prowlarr/docker-compose.yml`
**Public:** `services.nikflix.net/prowlarr`

## Ports
- `9696:9696`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/prowlarr/config` | `/config` |

## Environment
- `PUID=1000 PGID=1000` (other *arr services on this host use 1001 —
  inconsistent, see [`architecture.md`](../architecture.md))
- `TZ=Etc/UTC`

## Depends on / talks to
- Pushes indexer config to **sonarr / radarr / lidarr / readarr** on DK-02.

## Secrets
- API key in `config.xml`. Consumed by all *arr services on this host.

## Notes
- The PUID/PGID drift here is the most likely explanation if you ever see
  permission weirdness with files Prowlarr writes vs. files the other *arr
  services write.
