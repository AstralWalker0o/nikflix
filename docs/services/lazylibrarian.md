# lazylibrarian

**Host:** INT-PER-DK-02 (10.10.100.197)
**Image:** `lscr.io/linuxserver/lazylibrarian:latest`
**Container:** `lazylibrarian`
**Compose:** `/docker/lazylibrarian/docker-compose.yml`
**Public:** _(not in cloudflared ingress)_ — host port `5299` only

## Ports
- `5299:5299`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/lazylibrarian/data` | `/config` |
| `/mnt/media/books` | `/books` |
| `/mnt/media/audiobooks` | `/audiobooks` |
| `/mnt/downdisk01` | `/mnt/downdisk01` |

## Environment
- `PUID=1001 PGID=1001 TZ=Etc/UTC`

## Notes
- Overlaps in scope with calibre-web + readarr + readmeabook. Worth a
  call about which is the canonical book/audiobook automation tool — running
  three is fine, but probably not all three are getting equal use.
- Compose uses 4-space indentation (everything else uses 2-space). Cosmetic.
