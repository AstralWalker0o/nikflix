# Service inventory

One file per running service, plus [`_stale.md`](_stale.md) for the
defined-but-not-running ones. Format: image, ports, bind mounts, env,
cross-service dependencies, notes/questions specific to *this* deployment.

## DK-02 (10.10.100.197) — *arr + downloads tier

| Service | Public | Notes |
|---|---|---|
| [sonarr](sonarr.md) | `services.nikflix.net/sonarr` | TV automation |
| [radarr](radarr.md) | `services.nikflix.net/radarr` | Movies |
| [prowlarr](prowlarr.md) | `services.nikflix.net/prowlarr` | Indexer hub. PUID outlier (1000 vs 1001) |
| [lidarr](lidarr.md) | `services.nikflix.net/lidarr` | Music |
| [readarr](readarr.md) | `services.nikflix.net/readarr` | Books. `data.old/` cleanup pending |
| [sabnzbd](sabnzbd.md) | `services.nikflix.net/sabnzbd` | Usenet |
| [qbit](qbit.md) | `services.nikflix.net` (default) | qBit + PIA WG VPN. **Privileged.** Inline secrets. |
| [calibre-web](calibre-web.md) | `books.nikflix.net` | Calibre Web Automated |
| [calibre-downloader](calibre-downloader.md) | `dbooks.nikflix.net` | Cross-folder mounted to calibre-web |
| [lazylibrarian](lazylibrarian.md) | — | Books/audiobooks; overlaps with calibre/readarr/readmeabook |
| [maintainerr](maintainerr.md) | — | Plex/Jellyfin retention. Outlier `/mnt/datadisk01` mount |
| [readmeabook](readmeabook.md) | — (Cloudflared route TBD) | Audiobook tool. Postgres+Redis bind-mounted in same dir |
| [tunnel](tunnel.md) | — | cloudflared connector. Single SPOF for all public access |

## DK-01 (10.10.100.196) — media + web tier

| Service | Public | Notes |
|---|---|---|
| [jellyfin](jellyfin.md) | (LAN/NPM) | Media server. Reads `/mnt/media` populated by DK-02 |
| [jellyseerr](jellyseerr.md) | `requests.nikflix.net` | Talks to sonarr+radarr on DK-02 |
| [bazarr](bazarr.md) | `services.nikflix.net/bazarr` | Subtitles. Cross-host API to *arr |
| [firefly](firefly.md) | `finance.internik.net` | Multi-container; many secrets in `.env` |
| [npm](npm.md) | (LAN) | nginx-proxy-manager. Was the internal layer to Nextcloud AIO; now unused |
| [shieldcontrol](shieldcontrol.md) | (LAN) | **Custom built-from-source app.** Multi-stage Dockerfile |
| [kms](kms.md) | (LAN-only) | vlmcsd KMS emulator |
| [audiobookshelf](audiobookshelf.md) | (LAN-only) | Audiobook library; was crashing on VM restart, now has `restart: unless-stopped` |

[Removed services](_stale.md) — channels, homeassistant ghost, zero,
zigbee2mqtt (all DK-01), the leftover nextcloud on DK-02, and the live
nextcloud AIO on DK-01 (purged with its data on user request). Folders
deleted 2026-05-09.
