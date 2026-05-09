# firefly (Firefly III)

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `fireflyiii/core:latest` + `mariadb:lts` + `alpine` (cron)
  + `fireflyiii/data-importer:latest`
**Containers:** `firefly_iii_app`, `firefly_iii_db`, `firefly_iii_cron`,
  `firefly_iii_importer`
**Compose:** `/docker/firefly/docker-compose.yml`
**Public:** `finance.internik.net` → `firefly_iii_app:8080` → host `:8051`

## Sub-services

- **`app`** — Firefly III Laravel core. Port `8051:8080`.
- **`db`** — MariaDB. Internal-only (port `3306` not published).
- **`cron`** — Alpine container running a single `crontab` line that hits
  the app's `/api/v1/cron/<token>` endpoint daily. **Note:** the compose
  currently has the literal string `YOUR_32_CHAR_CRON_TOKEN` in the cron
  command; the real `STATIC_CRON_TOKEN` lives in `.env`. Either templates
  the compose to substitute it, or the cron is currently no-op. Confirm.
- **`importer`** — Data importer for CSVs / bank feeds. Port `8081:8080`.

## Bind mounts
| Host | Container |
|---|---|
| `/docker/firefly/firefly_iii_upload` | `/var/www/html/storage/upload` (app) |
| `/docker/firefly/firefly_iii_db` | `/var/lib/mysql` (db) |
| `/docker/firefly/import` | `/import` (importer) |

## Environment

Loaded from two `env_file`s:

- **`firefly/.env`** — Laravel app config. Contains:
  - `APP_KEY` (Laravel encryption key)
  - `DB_PASSWORD` (must match `.db.env`)
  - `MAIL_*` — smtp2go SMTP credentials
  - `STATIC_CRON_TOKEN`
  - `FIREFLY_III_ACCESS_TOKEN` (Firefly III personal access JWT, used by
    the importer; expires ~2027)
  - `AUTO_IMPORT_SECRET`
  - `APP_URL=http://localhost:8051` — set to `http://localhost`, but the
    public URL is `https://finance.internik.net`. Reverse-proxy compatible
    if Firefly is behind cloudflared with `TRUSTED_PROXIES=*`, which is
    set. Worth setting `APP_URL` to the public URL too.
- **`firefly/.db.env`** — MariaDB env. `MYSQL_PASSWORD` duplicates
  `DB_PASSWORD` from `.env`. Single source needed.

## Networks

- Internal `firefly_iii` bridge for app↔db↔cron↔importer.

## Notes

- Multiple secrets sit in plaintext today; see
  [`SECRETS.md`](../../discovery/SECRETS.md) — gitignored discovery copy.
  All move to Keeper in Phase 3, then rotate.
- `MAP_DEFAULT_LAT/LONG` is `51.98 / 5.92` (Netherlands default), not
  Perth. Cosmetic.
