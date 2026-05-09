# INT-PER-DK-02 (10.10.100.197)

*arr + downloads tier, plus the cloudflared connector that fronts the
entire stack. Each subdirectory is one service, with its own
`docker-compose.yml`, optional `.env.template` (rendered from Keeper),
and supporting files.

## Services

| Service | Public route | Web UI port | Keeper records | Autofill |
|---|---|---|---|---|
| [calibre-downloader](calibre-downloader/) | `dbooks.nikflix.net` | 8084 | `calibre-downloader-web` (RBI) | pending |
| [calibre-web](calibre-web/) | `books.nikflix.net` | 8083 | `calibre-web-web` (RBI) | pending |
| [lazylibrarian](lazylibrarian/) | (LAN) | 5299 | `lazylibrarian-web` (RBI) | pending |
| [lidarr](lidarr/) | `services.nikflix.net/lidarr` | 8686 | `lidarr-web` (RBI) | pending |
| [maintainerr](maintainerr/) | (LAN) | 6246 | `maintainerr-web` (RBI) | pending |
| [prowlarr](prowlarr/) | `services.nikflix.net/prowlarr` | 9696 | `prowlarr-web` (RBI) | pending |
| [qbit](qbit/) | `services.nikflix.net` (default) | 8082 | `qbit` (creds), `qbit-web` (RBI) | pending |
| [radarr](radarr/) | `services.nikflix.net/radarr` | 7878 | `radarr-web` (RBI) | pending |
| [readarr](readarr/) | `services.nikflix.net/readarr` | 8787 | `readarr-web` (RBI) | pending |
| [readmeabook](readmeabook/) | (no public route yet) | 3030 | `readmeabook-web` (RBI) | pending |
| [sabnzbd](sabnzbd/) | `services.nikflix.net/sabnzbd` | 8080 | `sabnzbd-web` (RBI) | pending |
| [sonarr](sonarr/) | `services.nikflix.net/sonarr` | 8989 | `sonarr-web` (RBI) | pending |
| [tunnel](tunnel/) | — (cloudflared, no web UI) | — | `tunnel` (TUNNEL_TOKEN) | n/a |

## Behavioural deltas from on-host configs

These are intentional cleanups made while copying composes into the repo:

- **`qbit/docker-compose.yml`** — `LAN_NETWORK` was the upstream sample
  default `192.168.1.0/24`. Changed to `10.10.100.0/24` to match the
  actual LAN. This affects which traffic the container allows out
  *without* the VPN tunnel. Previously `192.168.1.0/24` traffic was
  needlessly being forced through PIA.
- All inline secrets externalised: `qbit` PIA + SOCKS creds and `tunnel`
  TUNNEL_TOKEN are now `${VAR}` references; real values live in
  Keeper-rendered `.env` files.

## Special-case services

- **`tunnel`** is a single point of failure — every public hostname
  routes through this connector. A failed restart cuts off all
  external access (including Claude's SSH path back in). Always run
  `docker compose config` to validate before recreating.
- **`qbit`** is `privileged: true` and has its own VPN — the only
  service in the stack that gets traffic through PIA WireGuard. After
  every restart, check `docker logs qbittorrentvpn` for the
  "Successfully retrieved external IP" line to confirm the tunnel came
  up.
- **`calibre-downloader`** has cross-folder bind mounts into
  `/docker/calibre-web/{ingest,config/app.db}` — the two services are
  tightly coupled and need to live on the same host filesystem.
- **`maintainerr`** maps `/mnt/datadisk01 → /mnt/media` (every other
  service maps `/mnt/media → /mnt/media`). Outlier — confirm
  intentionality.

## See also

- [`docs/services/`](../docs/services/) — per-service narrative docs.
- [`docs/architecture.md`](../docs/architecture.md) — public-hostname
  ingress table is the canonical reference for what's reachable how.
- [`docs/keeper.md`](../docs/keeper.md), [`../DEPLOYMENT.md`](../DEPLOYMENT.md) — operational flows.
