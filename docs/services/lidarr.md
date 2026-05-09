# lidarr

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `lscr.io/linuxserver/lidarr:latest`
**Container:** `lidarr`
**Compose:** `/docker/lidarr/docker-compose.yml`
**Public:** `services.nikflix.net/lidarr`

## Ports
- `8686:8686`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/lidarr/config` | `/config` |
| `/mnt/media` | `/mnt/media` |
| `/mnt/downdisk01` | `/mnt/downdisk01` |

## Environment
- `PUID=1001 PGID=1001 TZ=Etc/UTC`

## Depends on / talks to
- prowlarr (indexers), sabnzbd + qbit (downloaders).

## Notes
- No outliers; standard *arr shape.
