# Stale / non-running services

These services have a `/docker/<name>/` folder with a compose file but no
running container as of discovery (2026-05-09). For each, decide:

- **Retire** — delete folder, remove from any backup scripts.
- **Resurrect** — bring back to life and document properly.
- **Migrate** — being moved to a different host; clean up source location.

## audiobookshelf — DK-01

- **Compose:** `/docker/audiobookshelf/docker-compose.yml`
- **Image:** `ghcr.io/advplyr/audiobookshelf:latest`
- **Port:** `13378:80`
- **Mounts:** `/mnt/media:/media`, `./config:/config`,
  `./config/metadata:/metadata`
- **Likely status:** Superseded by **`readmeabook`** on DK-02 which is
  serving as the active audiobook tool. Confirm and retire.

## channels — DK-01

- **Compose:** `/docker/channels/docker-compose.yml` —
  **malformed**: top-level `channels-dvr:` without a `services:` parent.
  Won't run on modern Docker Compose; might run under the host's old
  docker-compose v1.29 if one ever tried, but probably not.
- **Image:** `fancybits/channels-dvr:latest`
- **Port:** `8089:8089`
- **Likely status:** Never fully deployed, or was ripped out years ago.
  Decide if you still want OTA DVR; if so, fix the compose; if not, remove.

## homeassistant — DK-01 (ghost)

- **Compose:** `/docker/homeassistant/docker-compose.yml`
- **Image:** `ghcr.io/home-assistant/home-assistant:stable`
- **Port:** `8123:8123`, `privileged: true`
- **Live deployment is on `10.10.100.205`** (per cloudflared ingress
  `home.internik.net → 10.10.100.205:8123`), not on DK-01. The DK-01
  folder is leftover from a migration. Recommend removing once we have
  documentation/config for the `.205` deployment.

## zero (ZeroTier) — DK-01

- **Compose:** `/docker/zero/docker-compose.yml`
- **Image:** `zyclonite/zerotier:latest`
- **`network_mode: host`**, `cap_add: NET_ADMIN`, `SYS_ADMIN`,
  `/dev/net/tun` device passthrough.
- **`ZEROTIER_ONE_NETWORK_IDS=af78bf943695c6cb`** (also in `.env`)
- **Likely status:** Either retired in favour of Cloudflare Tunnel /
  WARP, or paused. ZeroTier networks are still active on Zerotier's side
  by network ID; if not used, leave it disabled and remove the compose, or
  re-enable if it provides a different reachability path you still want.

## zigbee2mqtt — DK-01

- **Compose:** `/docker/zigbee2mqtt/docker-compose.yml`
- **Images:** `koenkk/zigbee2mqtt`, `eclipse-mosquitto:2.0`
- `network_mode: host`, `privileged: true`
- **`TZ=Europe/Kiev`** — almost certainly a copy-paste from the upstream
  sample, never changed.
- Port `1883`/`9001` for MQTT broker.
- **Likely status:** Made sense when HA ran on this host. Now HA is on
  `.205`, so this either:
  - Should move to `.205` next to HA (zigbee2mqtt typically wants to be
    on the same host as the USB Zigbee dongle), or
  - Was already replaced by HA's built-in Zigbee integration on `.205`.
  Worth confirming.

## nextcloud — DK-02

- **Compose:** `/docker/nextcloud/docker-compose.yaml`
- Older / pre-NPM version of the AIO compose. Listens on `9090:8080`
  rather than `8443:8080`, no `APACHE_IP_BINDING`.
- **Likely status:** Migrated to DK-01 (which has the active deployment
  at `cloud.internik.net`). DK-02 copy is leftover.
