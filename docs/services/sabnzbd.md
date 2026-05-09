# sabnzbd

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `lscr.io/linuxserver/sabnzbd:latest`
**Container:** `sabnzbd`
**Compose:** `/docker/sabnzbd/docker-compose.yml`
**Public:** `services.nikflix.net/sabnzbd`

## Ports
- `8080:8080`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/sabnzbd/config` | `/config` |
| `/mnt/media` | `/mnt/media` |
| `/mnt/downdisk01` | `/mnt/downdisk01` |

## Environment
- `PUID=1001 PGID=1001 TZ=Etc/UTC`

## Notes
- Used as Usenet downloader for the *arr stack. Configured indexers + API
  key live in `/docker/sabnzbd/config/sabnzbd.ini`.
