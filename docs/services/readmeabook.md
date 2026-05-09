# readmeabook

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `ghcr.io/kikootwo/readmeabook:latest`
**Container:** `readmeabook`
**Compose:** `/docker/readmeabook/docker-compose.yml`
**Public:** _(not in cloudflared ingress)_ — host port `3030` only

## Ports
- `3030:3030`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/readmeabook/config` | `/app/config` |
| `/docker/readmeabook/cache` | `/app/cache` |
| `/docker/readmeabook/pgdata` | `/var/lib/postgresql/data` |
| `/docker/readmeabook/redis` | `/var/lib/redis` |
| `/mnt/downdisk01` | `/mnt/downdisk01` |
| `/mnt/media` | `/mnt/media` |

## Environment
- `PUID=1000 PGID=1000`
- `PUBLIC_URL="https://audiobooks.example.com"` — placeholder; should be
  the real public URL once an `audiobooks.*` cloudflared route is added.

## Notes
- Single image runs PostgreSQL + Redis + the app inside it (data dirs bind-
  mounted out). Unusual shape — keep an eye on backup ergonomics.
- This is the active audiobook tool. Audiobookshelf on DK-01 is defined
  but not running — confirm whether to retire it.
- `pgdata/` directory is owned by uid `pollinate` on the host, distinct
  from the rest. This is a side-effect of Postgres' uid mapping; harmless
  but unusual.
