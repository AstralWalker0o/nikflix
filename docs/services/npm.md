# npm (nginx-proxy-manager)

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `jc21/nginx-proxy-manager:latest`
**Container:** `npm_app_1` (default-named)
**Compose:** `/docker/npm/docker-compose.yml`
**Public:** _(not in cloudflared ingress)_ — fronts services internally on
the host. Cloudflared forwards to NPM where applicable (notably for
Nextcloud AIO).

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
- Currently fronts **Nextcloud AIO** (cloudflared sends
  `cloud.internik.net` → NPM, NPM forwards to AIO Apache on `:11000`).
- NPM admin UI on host port 81 — should not be exposed publicly. Confirm
  there's no cloudflared route to it.

## Notes

- Two layers of reverse proxy (Cloudflare → NPM → service) for the
  Nextcloud path is mostly an artefact of the AIO + LetsEncrypt-via-NPM
  pattern. Worth a once-over to see whether NPM is doing anything that
  cloudflared couldn't directly.
- No env file. Configuration is entirely UI/database-driven; backups live
  under `/docker/npm/config/`.
