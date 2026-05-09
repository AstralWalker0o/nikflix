# sonarr

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `lscr.io/linuxserver/sonarr:latest`
**Container:** `sonarr`
**Compose:** `/docker/sonarr/docker-compose.yml`
**Public:** `services.nikflix.net/sonarr` (Cloudflare Tunnel + Access)

## Ports
- `8989:8989` — web UI / API

## Bind mounts
| Host | Container |
|---|---|
| `/docker/sonarr/config` | `/config` |
| `/mnt/media` | `/mnt/media` |
| `/mnt/downdisk01` | `/mnt/downdisk01` |

## Environment
- `PUID=1001 PGID=1001`
- `TZ=Etc/UTC` (most other DK-01 services use `Australia/Perth`; worth normalising)

## Depends on / talks to
- **prowlarr** — indexer aggregator, also on DK-02
- **sabnzbd** + **qbit** — for download fulfillment, also on DK-02
- **bazarr** (DK-01) — calls Sonarr's API for subtitle workflow
- **jellyseerr** (DK-01) — calls Sonarr's API for request fulfillment

## Secrets
- API key stored in `/docker/sonarr/config/config.xml`. Used by bazarr +
  jellyseerr — needs to be retrievable from Keeper post-migration.

## Notes
- `version: "2.1"` declaration at top — obsolete in modern Compose, harmless.
