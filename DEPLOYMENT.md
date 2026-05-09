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

3. **Populate `.env` files** — every service that needs secrets has a
   committed `.env.example`. Until Keeper Secrets Manager is wired up
   ([Phase 3](#phase-3--keeper-secrets-manager)), copy each `.env.example`
   to `.env` (and `.db.env.example` to `.db.env` for `firefly`) and fill
   in real values from Keeper manually. The `.env` files are gitignored.

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

## Phase 3 — Keeper Secrets Manager

Once a Keeper Secrets Manager Application is provisioned and shared with
the right records, the manual `.env` step above is replaced by:

```bash
ksm exec -- docker compose up -d   # one option
# or, render envs ahead of time:
ksm secret notation get keeper://record/field > .env
```

See `docs/keeper.md` (TBD) for the exact pattern once we set it up.

## Hosts in scope

| Host | LAN IP | This repo tree |
|---|---|---|
| `INT-PER-DK-01` | 10.10.100.196 | [`int-per-dk-01/`](int-per-dk-01/) |
| `INT-PER-DK-02` | 10.10.100.197 | [`int-per-dk-02/`](int-per-dk-02/) |
