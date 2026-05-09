# npm (nginx-proxy-manager)

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `jc21/nginx-proxy-manager:latest`
**Container:** `npm_app_1` (default-named)
**Compose:** `/docker/npm/docker-compose.yml`
**Public:** _(not in cloudflared ingress)_ — was the internal reverse
proxy in front of Nextcloud AIO. Nextcloud has since been removed; NPM
now has no active routes.

## Ports
- `80:80` — HTTP
- `81:81` — NPM admin UI
- `443:443` — HTTPS

## Bind mounts
| Host | Container |
|---|---|
| `/docker/npm/config` | `/data` |
| `/docker/npm/letsencrypt` | `/etc/letsencrypt` |

## Role in the stack

- Internal reverse proxy on DK-01.
- Used to front **Nextcloud AIO** (cloudflared sent `cloud.internik.net`
  → NPM, NPM forwarded to AIO Apache on `:11000`). Nextcloud has been
  removed; the proxy host entry can be deleted from the NPM admin UI.
- NPM admin UI on host port 81 — should not be exposed publicly. Confirm
  there's no cloudflared route to it.

## Notes

- With Nextcloud gone, NPM has no active routes. Candidate for removal
  from DK-01 unless reused for something else.
- No env file. Configuration is entirely UI/database-driven; backups live
  under `/docker/npm/config/`.
