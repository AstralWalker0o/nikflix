# INT-PER-DK-01 (10.10.100.196)

Media server tier. Each subdirectory is one service, with its own
`docker-compose.yml`, optional `.env.template` (rendered from Keeper at
deploy time), and any other supporting files.

## Services

| Service | Public route | Web UI port | Keeper records | Autofill |
|---|---|---|---|---|
| [audiobookshelf](audiobookshelf/) | (LAN) | 13378 | `audiobookshelf-web` (RBI) | ✓ working |
| [bazarr](bazarr/) | `services.nikflix.net/bazarr` | 6767 | `bazarr-web` (RBI) | pending |
| [firefly](firefly/) | `finance.internik.net` | 8051 | `firefly-app`, `firefly-db`, `firefly-web` (RBI) | pending |
| [jellyfin](jellyfin/) | (LAN) | 8096 | `jellyfin-web` (RBI) | ✓ rules applied (still under test) |
| [jellyseerr](jellyseerr/) | `requests.nikflix.net` | 5055 | `jellyseerr-web` (RBI) | ✓ rules applied |
| [kms](kms/) | (LAN-only) | 1688 | — (no web UI) | n/a |
| [npm](npm/) | (LAN) | 81 | `npm-web` (RBI) | ✓ rules applied |

## Out of scope here

- **`shieldcontrol`** — its own GitHub repo
  (`AstralWalker0o/ShieldControl`), cloned + built directly on the host
  at `/docker/shieldcontrol/`. Has a Keeper `shieldcontrol-web` record
  but no compose in this tree.

## Behavioural notes

- **Nextcloud AIO retired 2026-05-09** — mastercontainer + ~10 spawned
  sub-containers stopped, all `nextcloud_aio_*` named volumes deleted
  (Postgres/Redis/user data — destructive). Cloudflared ingress for
  `cloud.internik.net` and `admin.cloud.internik.net` removed.
- **NPM** (nginx-proxy-manager) was fronting Nextcloud AIO. With
  Nextcloud gone, NPM has no active routes — currently a candidate for
  retirement. Compose stays here until that's decided.
- **Stale folders cleaned up 2026-05-09** — `channels/`, `homeassistant/`
  (live HA is on `.205`), `zero/` (ZeroTier), `zigbee2mqtt/` removed on
  this host. See [`docs/services/_stale.md`](../docs/services/_stale.md).
- **Audiobookshelf had no restart policy** at discovery — patched to
  `restart: unless-stopped` so it auto-recovers when the VM reboots.

## See also

- [`docs/services/`](../docs/services/) — per-service narrative docs
  (purpose, dependencies, open questions).
- [`docs/architecture.md`](../docs/architecture.md) — host map and
  inconsistencies list.
- [`docs/keeper.md`](../docs/keeper.md) — vault layout + KSM/Commander
  CLI setup that powers the rotation flow.
- [`../DEPLOYMENT.md`](../DEPLOYMENT.md) — first-deploy + rotation steps.
