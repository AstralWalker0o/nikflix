# jellyseerr

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `ghcr.io/seerr-team/seerr:latest`
**Container:** `jellyseerr`
**Compose:** `/docker/jellyseerr/docker-compose.yml`
**Public:** `requests.nikflix.net`

## Ports
- `5055:5055`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/jellyseerr/config` | `/app/config` |

## Environment
- `LOG_LEVEL=debug TZ=Australia/Perth PORT=5055`

## Depends on / talks to
- **sonarr** (DK-02:8989) and **radarr** (DK-02:7878) — request fulfillment.
  API keys for both stored in Jellyseerr config.
- **jellyfin** (same host:8096) — for library state / user auth.

## Notes
- Image is `seerr-team/seerr`, the rebranded fork (was `fallenbagel/jellyseerr`
  prior to the rename). If you ever pin or update this, mind that the image
  path moved.
- `LOG_LEVEL=debug` — quite verbose; consider lowering for prod.
