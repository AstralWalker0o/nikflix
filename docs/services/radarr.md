# radarr

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `lscr.io/linuxserver/radarr:latest`
**Container:** `radarr`
**Compose:** `/docker/radarr/docker-compose.yml`
**Public:** `services.nikflix.net/radarr`

## Ports
- `7878:7878`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/radarr/config` | `/config` |
| `/mnt/media` | `/mnt/media` |
| `/mnt/downdisk01` | `/mnt/downdisk01` |

## Environment
- `PUID=1001 PGID=1001 TZ=Etc/UTC`

## Depends on / talks to
- prowlarr (indexers), sabnzbd + qbit (downloaders) — all DK-02
- bazarr (DK-01) and jellyseerr (DK-01) call its API

## Secrets
- API key in `config.xml`; consumed by bazarr + jellyseerr.

## Notes
- Same shape as sonarr; the two are deliberately near-identical.
