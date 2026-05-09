# nextcloud (AIO)

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `nextcloud/all-in-one:latest` (mastercontainer); spawns ~10
sub-containers it manages itself.
**Container:** `nextcloud-aio-mastercontainer`
**Compose:** `/docker/nextcloud/docker-compose.yaml`
**Public:**
- `cloud.internik.net` (user-facing) — fronted by NPM, then AIO Apache
  on `:11000`.
- `admin.cloud.internik.net` (AIO admin UI) — direct cloudflared route to
  `https://10.10.100.196:8080`.

## Sub-containers spawned by the mastercontainer

`nextcloud-aio-{apache, nextcloud, imaginary, redis, database, whiteboard,
notify-push, talk, collabora}` — all managed by AIO. Don't hand-edit.

## Ports
- `8443:8080` — AIO admin interface (HTTPS).
- Apache binds to `127.0.0.1:11000` via `APACHE_IP_BINDING=10.10.100.196`
  (binds to LAN IP) + `APACHE_PORT=11000`. NPM forwards to it.

## Volumes
- Named volume `nextcloud_aio_mastercontainer` — AIO state.
- AIO creates additional volumes under the hood for Postgres / Redis /
  user data.
- Mounts `/var/run/docker.sock:ro` (so the mastercontainer can manage its
  child containers).

## Environment
- `NEXTCLOUD_TRUSTED_DOMAIN=cloud.internik.net`
- `SKIP_DOMAIN_VALIDATION=false` — AIO validates the domain end-to-end via
  NPM. NPM proxy host + SSL cert must be configured before running setup.
- `NEXTCLOUD_TIMEZONE=Australia/Perth`
- `COLLABORA_ENABLED=yes`, `ONLYOFFICE_ENABLED=no` — AIO can't run both.
- `CLAMAV_ENABLED=yes`, `FULLTEXTSEARCH_ENABLED=yes`,
  `TALK_RECORDING_ENABLED=yes`, `IMAGINARY_ENABLED=yes`.

## NPM proxy host configuration (per the inline comments in the compose)

- Domain: `cloud.internik.net`
- Scheme: `http`, Forward IP: `127.0.0.1`, Forward Port: `11000`
- Websockets: ON
- SSL: Let's Encrypt cert, Force SSL ON, HTTP/2 ON
- Custom Nginx config:
  ```
  client_max_body_size 0;
  client_body_timeout 1d;
  client_body_buffer_size 512k;
  proxy_read_timeout 1d;
  proxy_connect_timeout 1d;
  proxy_send_timeout 1d;
  ```

## Notes

- A second `/docker/nextcloud/` directory exists on **DK-02** with an older
  AIO compose (port `9090:8080`, no NPM in front, no `APACHE_IP_BINDING`).
  Not running. Likely the live deployment was migrated from DK-02 to DK-01;
  the DK-02 copy should be removed once we confirm.
- AIO is opinionated; restructuring this for the GitHub-deployable layout
  needs care because most of the stack is managed by the mastercontainer
  rather than by the compose file.
