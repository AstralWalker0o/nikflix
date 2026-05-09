# Architecture

## Hosts

```
                   ┌────────────────────────────────────────────┐
                   │           Cloudflare edge / DNS            │
                   │  *.nikflix.net   *.internik.net  (Access)  │
                   └────────────────────┬───────────────────────┘
                                        │  cloudflare tunnel (QUIC)
                                        ▼
              ┌─────────────────────────────────────────────────┐
              │ INT-PER-DK-02   10.10.100.197                   │
              │   cloudflared-tunnel  (single connector for the │
              │   whole homelab; reaches across LAN to .196 and │
              │   .205 too — see ingress table below)           │
              │                                                 │
              │   *arr stack  · qBit-VPN · SABnzbd · Calibre    │
              │   Maintainerr · LazyLibrarian · readmeabook     │
              └────────────────┬────────────────────────────────┘
                               │ LAN 10.10.100.0/24
                               ▼
              ┌─────────────────────────────────────────────────┐
              │ INT-PER-DK-01   10.10.100.196                   │
              │                                                 │
              │   Jellyfin · Bazarr · Jellyseerr                │
              │   Firefly III (app + db + cron + importer)      │
              │   nginx-proxy-manager (NPM)                     │
              │   ShieldControl · KMS · Audiobookshelf          │
              └─────────────────────────────────────────────────┘

              + 10.10.100.205  — Home Assistant lives here per ingress;
                                 not yet inventoried.
```

Both DK hosts run Ubuntu 24.04, Docker 29.x, docker-compose v1.29.2.

## Public hostname routing

From the live cloudflared ingress on DK-02 (one tunnel for everything):

| Public hostname | Path | Origin | Notes |
|---|---|---|---|
| `services.nikflix.net` | `/sabnzbd` | `http://10.10.100.197:8080` | DK-02 |
| `services.nikflix.net` | `/sonarr` | `http://10.10.100.197:8989` | DK-02 |
| `services.nikflix.net` | `/radarr` | `http://10.10.100.197:7878` | DK-02 |
| `services.nikflix.net` | `/prowlarr` | `http://10.10.100.197:9696` | DK-02 |
| `services.nikflix.net` | `/readarr` | `http://10.10.100.197:8787` | DK-02 |
| `services.nikflix.net` | `/lidarr` | `http://10.10.100.197:8686` | DK-02 |
| `services.nikflix.net` | `/bazarr` | `http://10.10.100.196:6767` | DK-01 |
| `services.nikflix.net` | (default) | `http://10.10.100.197:8082` | qBit |
| `requests.nikflix.net` | / | `http://10.10.100.196:5055` | Jellyseerr |
| `books.nikflix.net` | / | `http://10.10.100.197:8083` | Calibre Web |
| `dbooks.nikflix.net` | / | `http://10.10.100.197:8084` | Calibre downloader |
| `home.internik.net` | / | `http://10.10.100.205:8123` | Home Assistant (third box) |
| `finance.internik.net` | / | `http://10.10.100.196:8051` | Firefly III |
| `remote-3.internik.net` | / | `ssh://10.10.100.205:22` | Legacy SSH route |
| `ssh4.internik.net` | / | `ssh://10.10.100.197:22` | DK-02 SSH (claude) |
| `ssh5.internik.net` | / | `ssh://10.10.100.196:22` | DK-01 SSH (claude) |

WARP-routing is enabled on the tunnel.

## Authentication & Zero Trust

Public-hostname HTTP services that aren't meant for the open internet are
protected by **Cloudflare Access**. Identity providers:

- **Azure AD** — for human users (you and other end-users), via SSO. This
  is how you and any users of Firefly / Jellyseerr / etc. are meant to
  authenticate.
- **Service Auth** with the `claude-sandbox` service token — used by
  automation in this repo (the `bin/nfssh` wrapper). Scoped per-app and
  revocable from the Zero Trust dashboard.

Access policies sit in front of each application; see
[`access.md`](access.md) for the SSH-specific setup.

## Internal traffic shape

- **No service mesh.** Containers reach each other either over their own
  per-compose bridge network (`<svc>_default`) or via host port → LAN IP.
- **Most services don't need cross-host calls.** Notable exceptions:
  - **Bazarr** (DK-01) → Sonarr, Radarr (DK-02) for subtitle workflow.
    Currently uses LAN IPs / host ports.
  - **Jellyseerr** (DK-01) → Sonarr, Radarr (DK-02) for request fulfillment.
    Same pattern.
  - **Jellyfin** (DK-01) reads media off shared filesystem (`/mnt/media`),
    populated by *arr/qBit/SABnzbd on DK-02. The `/mnt/media` mount is
    expected to be the same data on both hosts (NFS/SMB/etc. — confirm).
- **nginx-proxy-manager** (NPM) on DK-01 was fronting Nextcloud AIO; with
  Nextcloud removed it currently has no active routes and is a candidate
  for retirement.

## Storage roots (bind-mount conventions)

| Path | Used by | Purpose |
|---|---|---|
| `/mnt/media` | Jellyfin, Bazarr, Audiobookshelf, *all *arr, Calibre, Lidarr, Lazylibrarian | Primary media library (TV, movies, music, books, audiobooks) |
| `/mnt/downdisk01` | qBit, SABnzbd, *arr, Lazylibrarian, Calibre downloader, readmeabook | Active downloads & downloader staging |
| `/mnt/datadisk01` | Maintainerr only | Used for `/mnt/media` mapping in Maintainerr — outlier; reason unclear |
| `/docker/<svc>/config/` (per-service) | Most services | Service config + state on the host |
| `/docker/<svc>/data/` (some services) | LazyLibrarian, qBit, Readarr | Same shape as `config/`; legacy naming |

## Inconsistencies / open questions captured during discovery

1. **PUID/PGID drift across services.**
   - DK-01: `bazarr`, `jellyfin`, `kms`, `sabnzbd`, etc. — `1001`.
     `audiobookshelf` declares `UID/GID 1000/100` (different).
   - DK-02: `prowlarr` — `1000`. Most others — `1001`. `qbit` — `0/0`.
   - Picking a canonical mapping in Phase 3 is sensible (and rationalising
     ownership of `/docker/*` accordingly).
2. **TZ drift.** Mix of `Etc/UTC`, `Australia/Perth`, `Europe/Kiev`
   (zigbee2mqtt — likely upstream sample, never edited).
3. **`version: "2.1"` declarations** in several composes — obsolete in
   Compose v2, harmless but worth removing.
4. **Stale folders cleaned up 2026-05-09** — `channels`, `homeassistant`
   (ghost; live HA on `.205`), `zero`, `zigbee2mqtt` on DK-01 plus the
   stale `nextcloud` on DK-02. See [`services/_stale.md`](services/_stale.md).
   `audiobookshelf` was on the original list because the container had
   crashed; restored with `restart: unless-stopped` so it auto-recovers.
5. **`readarr/data.old/` directory** — leftover from a previous migration.
   Worth cleaning up after confirming it's not needed.
6. **Cross-folder bind mount** — `calibre-downloader` on DK-02 mounts
   `/docker/calibre-web/ingest` and `/docker/calibre-web/config/app.db`,
   tightly coupling the two services' deployment.
7. **`firefly/` references `.db.env`** — credentials duplicated between
   `.env` (DB_PASSWORD) and `.db.env` (MYSQL_PASSWORD). Single source of
   truth needed when we move to Keeper.
8. **`shieldcontrol/` is built from local source** — multi-stage Dockerfile
   in `/docker/shieldcontrol/`. In Phase 3 we need to decide whether the
   source lives in this repo or in its own.
9. **`docker-compose` v1.29 is end-of-life** on both DK hosts and
   incompatible with the Docker Engine 29 API surface — every recreate
   throws `KeyError: 'ContainerConfig'` and needs `docker rm -f` first.
   Migrate to the `docker compose` plugin (v2) as part of the restructure.
