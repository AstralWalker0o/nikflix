# maintainerr

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `ghcr.io/maintainerr/maintainerr:latest`
**Container:** `maintainerr`
**Compose:** `/docker/maintainerr/docker-compose.yml`
**Public:** _(not in cloudflared ingress)_ — host port `6246` only

## Ports
- `6246:6246`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/maintainerr/config` | `/config` |
| `/mnt/datadisk01` | `/mnt/media` *(outlier — see notes)* |

## Environment
- `PUID=1001 PGID=1001 TZ=Australia/Perth`

## Notes
- **Outlier path mapping:** `/mnt/datadisk01` is mapped to `/mnt/media`
  inside the container, while every other service maps `/mnt/media` →
  `/mnt/media`. Confirm that this is intentional and what the data on
  `/mnt/datadisk01` is. If it's a duplicate of `/mnt/media`, change the host
  side to match. If it's an actual second media root, this is fine but worth
  documenting.
- Maintainerr decides what media to remove/keep based on Plex/Jellyfin
  usage; check whether it's pointed at this stack's Jellyfin (DK-01).
