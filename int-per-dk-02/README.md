# INT-PER-DK-02 (10.10.100.197)

*arr + downloads tier, plus the Cloudflare Tunnel connector that fronts the
entire stack. Each subdirectory is one service.

| Service | Public hostname / route | Notes |
|---|---|---|
| [calibre-downloader](calibre-downloader/) | `dbooks.nikflix.net` | **Cross-folder mounts** into calibre-web's directory |
| [calibre-web](calibre-web/) | `books.nikflix.net` | Calibre Web Automated |
| [lazylibrarian](lazylibrarian/) | (LAN) | Books + audiobooks; overlaps scope with calibre/readarr/readmeabook |
| [lidarr](lidarr/) | `services.nikflix.net/lidarr` | Music |
| [maintainerr](maintainerr/) | (LAN) | Plex/Jellyfin retention. Maps `/mnt/datadisk01` → `/mnt/media` (outlier) |
| [prowlarr](prowlarr/) | `services.nikflix.net/prowlarr` | Indexer hub. **PUID=1000** (others 1001) |
| [qbit](qbit/) | `services.nikflix.net` (default) | qBit + PIA WireGuard. **Privileged**. Secrets in `.env` |
| [radarr](radarr/) | `services.nikflix.net/radarr` | Movies |
| [readarr](readarr/) | `services.nikflix.net/readarr` | Books. Image is `:develop` |
| [readmeabook](readmeabook/) | (no public route yet) | Audiobook tool. PostgreSQL + Redis bind-mounted in same dir |
| [sabnzbd](sabnzbd/) | `services.nikflix.net/sabnzbd` | Usenet |
| [sonarr](sonarr/) | `services.nikflix.net/sonarr` | TV |
| [tunnel](tunnel/) | — | cloudflared connector for *all* public access. SPOF. Secrets in `.env` |

## Behavioural deltas from on-host configs

These are intentional cleanups made while copying composes into the repo:

- **`qbit/docker-compose.yml`** — `LAN_NETWORK` was the upstream sample
  default `192.168.1.0/24`. Changed to `10.10.100.0/24` to match the
  actual LAN. This affects which traffic the container allows out
  without going via the VPN tunnel; `192.168.1.0/24` traffic was being
  needlessly forced through PIA.
- All inline secrets (`qbit` PIA + SOCKS, `tunnel` `TUNNEL_TOKEN`) are
  now `${VAR}` references; real values live in untracked `.env` files
  populated from Keeper.

See [`docs/services/`](../docs/services/) for per-service narrative.
