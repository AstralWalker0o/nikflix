# audiobookshelf

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `ghcr.io/advplyr/audiobookshelf:latest`
**Container:** `audiobookshelf`
**Compose:** `/docker/audiobookshelf/docker-compose.yml`
**Public:** _(not in cloudflared ingress)_ — host port `13378` only

## Ports
- `13378:80`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/audiobookshelf/config` | `/config` |
| `/docker/audiobookshelf/config/metadata` | `/metadata` |
| `/mnt/media` | `/media` |

## Environment
- `TZ=Australia/Perth`

## Notes
- This service tends to crash and not auto-restart on host reboot. Compose
  now has `restart: unless-stopped`, which makes Docker bring it back
  automatically when the daemon (and therefore the VM) starts. Previously
  it had no restart policy and required a manual `docker-compose up -d`.
- Overlaps in scope with **`readmeabook`** on DK-02. Both consume the same
  `/mnt/media/audiobooks` library; pick a primary if you haven't already.
- No PUID/PGID set — runs as the image's default user (likely `node` or
  `root`); files written into `./config/` will reflect that.
