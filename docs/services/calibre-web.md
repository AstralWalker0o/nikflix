# calibre-web (calibre-web-automated)

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `crocodilestick/calibre-web-automated:latest`
**Container:** `calibre-web-automated`
**Compose:** `/docker/calibre-web/docker-compose.yml`
**Public:** `books.nikflix.net`

## Ports
- `8083:8083`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/calibre-web/config` | `/config` |
| `/docker/calibre-web/ingest` | `/cwa-book-ingest` |
| `/docker/calibre-web/library` | `/calibre-library` |
| `/mnt/media/books` | `/books` |

## Environment
- `PUID=1000 PGID=1000 TZ=Australia/Perth`
- `NETWORK_SHARE_MODE=true`

## Coupling
- **calibre-downloader** mounts files from this service's directory:
  `/docker/calibre-web/ingest` and `/docker/calibre-web/config/app.db`.
  The two services must share host filesystem state — keep them on the
  same host or replumb the relationship in Phase 3.

## Notes
- "automated" fork of calibre-web — adds ingest folder + library auto-import.
- `app.db` is the calibre-web user/auth database; downloader reads it to
  authenticate users for OPDS.
