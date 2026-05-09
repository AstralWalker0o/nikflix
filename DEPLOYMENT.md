# Deployment

The `<host>/<service>/` layout in this repo is the source of truth for
container configuration. Bind-mounted state (config dirs, databases, media,
caches, downloads) stays on each host — this repo does **not** move data.

## First-time deployment on a host

1. **Clone the repo somewhere stable on the host** — e.g. `/opt/nikflix`:
   ```bash
   sudo git clone https://github.com/AstralWalker0o/nikflix.git /opt/nikflix
   sudo chown -R claude:claude /opt/nikflix
   ```

2. **Migrate existing state** — for each service, the live data lives at
   `/docker/<service>/{config,data,...}/`. The compose files in this repo
   use **relative bind mounts** (`./config:/config`, etc.), so once you
   `cd` into the repo's service directory the relative paths resolve
   *there*, not at `/docker/<service>/`. Two ways to bridge this:

   **Option A — move state into the repo tree (one-time).**
   ```bash
   for svc in /docker/*/; do
       name=$(basename "$svc")
       dst=/opt/nikflix/$(hostname)/$name
       [ -d "$dst" ] || continue
       sudo rsync -a "$svc"/ "$dst"/  --exclude=docker-compose.yml \
                                      --exclude=docker-compose.yaml \
                                      --exclude=.env --exclude=.db.env
   done
   ```
   Replace `/docker/<service>/` with a symlink so any tool (or human
   muscle memory) hitting the old path still works:
   ```bash
   sudo mv /docker /docker.bak && \
   sudo ln -s /opt/nikflix/$(hostname) /docker
   ```

   **Option B — symlink the new tree at the existing data location.**
   Quicker, no data move:
   ```bash
   for svc in /opt/nikflix/$(hostname)/*/; do
       name=$(basename "$svc")
       # bring the live config dirs into the repo tree as symlinks
       [ -d "/docker/$name/config" ] && \
           ln -s "/docker/$name/config" "$svc/config"
       [ -d "/docker/$name/data" ] && \
           ln -s "/docker/$name/data" "$svc/data"
       # ...and so on for any other state dirs the service uses
   done
   ```
   Slightly more fragile (an extra indirection layer) but no rsync.

   For a brand-new host with no live state, neither step is needed.

3. **Populate `.env` files from Keeper.** Services that need secrets ship
   a `.env.template` next to their compose. Once `ksm` is initialised on
   the host (see [`docs/keeper.md`](docs/keeper.md)), render every env
   for the host in one pass:
   ```bash
   bin/ksm-render $(hostname)
   ```
   Or render a single service: `bin/ksm-render $(hostname) firefly`.
   Resulting `.env` / `.db.env` files are mode 0600 and gitignored.

4. **Bring services up** — per-service:
   ```bash
   cd /opt/nikflix/$(hostname)/<service>
   docker compose up -d        # use the v2 plugin, NOT docker-compose v1
   ```

   Or in bulk:
   ```bash
   cd /opt/nikflix/$(hostname)
   for svc in */; do (cd "$svc" && docker compose up -d); done
   ```

## Updating a service

```bash
cd /opt/nikflix/$(hostname)/<service>
git pull
docker compose pull           # if the image is :latest or otherwise drifting
docker compose up -d
```

## Important: docker-compose v1 vs v2

Both DK hosts currently have `docker-compose` v1.29.2 installed system-wide.
**It does not work cleanly with Docker Engine 29** — every recreate hits
`KeyError: 'ContainerConfig'` and needs a `docker rm -f` first. Do **not**
deploy with v1.

Install the v2 plugin instead:
```bash
sudo apt-get install docker-compose-plugin
docker compose version    # should show v2.x
```

Then everywhere in this repo, use `docker compose` (space) not
`docker-compose` (dash).

## Keeper Secrets Manager flow

Vault layout, Application setup, host-side `ksm` initialisation, and the
template format are documented in [`docs/keeper.md`](docs/keeper.md).

Day-to-day rotation is one command. After editing a secret in Keeper, on
the host:

```bash
bin/refresh $(hostname)            # all services with templates
bin/refresh $(hostname) firefly    # one service
```

`refresh` calls `ksm-render`, diffs the rendered env against
`/docker/<svc>/.env`, backs up the current file (`*.bak.<timestamp>`),
swaps the new one in (mode 0600), then `docker compose up -d
--force-recreate` only the services whose env actually changed. Skips
the rest.

## Hosts in scope

| Host | LAN IP | This repo tree |
|---|---|---|
| `INT-PER-DK-01` | 10.10.100.196 | [`int-per-dk-01/`](int-per-dk-01/) |
| `INT-PER-DK-02` | 10.10.100.197 | [`int-per-dk-02/`](int-per-dk-02/) |
