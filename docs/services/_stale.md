# Removed services (former stale folders)

These were defined-but-not-running on disk during initial discovery
(2026-05-09). All have since been deleted from the host filesystem.

## Removed 2026-05-09

| Service | Host | Folder size | Reason |
|---|---|---|---|
| `channels` (Channels DVR) | DK-01 | 721 MB | Compose was malformed (top-level `channels-dvr:` without `services:`); never ran on this stack |
| `homeassistant` | DK-01 | 1.7 GB | Ghost folder; live HA runs on `10.10.100.205`. Last write on this copy was 2025-11-16 (~6 months stale at deletion time) |
| `zero` (ZeroTier router) | DK-01 | 108 KB | Replaced by Cloudflare Tunnel for external reach |
| `zigbee2mqtt` | DK-01 | 132 KB | Belongs on the same host as the Zigbee dongle; that's `.205` now (or HA's built-in Zigbee integration there) |
| `nextcloud` | DK-02 | 8 KB | Earlier AIO compose (port 9090, no NPM); active deployment was on DK-01 (also since removed) |

Networks `firefly_default` and `nextcloud_default` were also pruned at the
same time — both were unused defaults; the active stacks use
`firefly_firefly_iii` and `nextcloud-aio` respectively.

## Removed 2026-05-09 (later)

| Service | Host | Reason |
|---|---|---|
| `nextcloud` (AIO) | DK-01 | User decision. Mastercontainer + ~10 spawned sub-containers stopped, all `nextcloud_aio_*` named volumes deleted (Postgres/Redis/user data — destructive). Cloudflared ingress for `cloud.internik.net` and `admin.cloud.internik.net` removed. NPM proxy host left in place but unused — NPM itself now has no active routes |

## Audiobookshelf was on this list

Initially documented as stale because no container was running. The user
clarified it had crashed (a known recurring issue when the VM restarts).
Compose was patched to add `restart: unless-stopped`, container was
brought up, and it now lives in [`audiobookshelf.md`](audiobookshelf.md).
