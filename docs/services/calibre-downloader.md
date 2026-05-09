# calibre-downloader (calibre-web-automated-book-downloader)

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `ghcr.io/calibrain/calibre-web-automated-book-downloader:latest`
**Container:** `calibre-downloader_calibre-web-automated-book-downloader_1`
  (default-named — directory + service combined)
**Compose:** `/docker/calibre-downloader/docker-compose.yml`
**Public:** `dbooks.nikflix.net`

## Ports
- `8084:8084`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/calibre-web/ingest` | `/cwa-book-ingest` *(cross-service mount)* |
| `/docker/calibre-downloader/config` | `/config` |
| `/docker/calibre-web/config/app.db` (read-only) | `/auth/app.db:ro` *(cross-service mount)* |
| `/mnt/media/books` | `/books` |

## Environment
- `FLASK_PORT=8084 LOG_LEVEL=info BOOK_LANGUAGE=en USE_BOOK_TITLE=true`
- `TZ=Australia/Perth APP_ENV=prod`
- `UID=1000 GID=100`
- `CWA_DB_PATH=/auth/app.db`

## Coupling
- Hard dependency on **calibre-web** running on the same host filesystem —
  see notes in [`calibre-web.md`](calibre-web.md).

## Notes
- Container name follows compose v1 default naming because the service block
  has no `container_name:` field. Worth setting one for cleaner ops.
