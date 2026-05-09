# INT-PER-DK-01 (10.10.100.196)

Media server tier. Each subdirectory is one service, with its own
`docker-compose.yml` and any supporting files (`.env.example`, etc.).

| Service | Public hostname / route | Notes |
|---|---|---|
| [audiobookshelf](audiobookshelf/) | (LAN) | `restart: unless-stopped` — auto-recovers on VM boot |
| [bazarr](bazarr/) | `services.nikflix.net/bazarr` | Talks to sonarr/radarr on DK-02 |
| [firefly](firefly/) | `finance.internik.net` | App + db + cron + importer; secrets in `.env`/`.db.env` |
| [jellyfin](jellyfin/) | (LAN/NPM) | Reads `/mnt/media` populated by DK-02 |
| [jellyseerr](jellyseerr/) | `requests.nikflix.net` | Talks to sonarr/radarr on DK-02 |
| [kms](kms/) | (LAN-only) | vlmcsd KMS emulator |
| [nextcloud](nextcloud/) | `cloud.internik.net`, `admin.cloud.internik.net` | AIO mastercontainer (spawns ~10 sub-containers); behind NPM |
| [npm](npm/) | (LAN) | Reverse proxy for Nextcloud AIO |

## Not in this tree

- **shieldcontrol** — its own GitHub repo
  (`AstralWalker0o/ShieldControl`); cloned and built directly on the host
  at `/docker/shieldcontrol/`. Skipped in this restructure by design.

See [`docs/services/`](../docs/services/) for per-service narrative docs
(purpose, dependencies, open questions). Composes here are the
deployable artefact; docs are the explanation.
