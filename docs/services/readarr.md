# readarr

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `lscr.io/linuxserver/readarr:develop`
**Container:** `readarr`
**Compose:** `/docker/readarr/docker-compose.yml`
**Public:** `services.nikflix.net/readarr`

## Ports
- `8787:8787`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/readarr/data` | `/config` (note: `data`, not `config`) |
| `/mnt/media` | `/mnt/media` |
| `/mnt/downdisk01` | `/mnt/downdisk01` |

## Environment
- `PUID=1001 PGID=1001 TZ=Etc/UTC`

## Notes
- Image tag is `develop`, not `latest` — Readarr stable was abandoned upstream.
- `/docker/readarr/data.old/` exists alongside `data/` from a previous migration.
  Confirm it's safe to remove and clean up.
