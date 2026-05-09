# nikflix

Personal homelab for media (movies, TV, music, books, audiobooks),
home automation, productivity (Firefly III), and a bunch of adjacent
self-hosted services. Built incrementally over ~10 years across local
and cloud generations. Everything is Docker. Public access is brokered
by Cloudflare Tunnel with Cloudflare Access policies for Zero Trust SSO
via Azure AD.

This repo is the source of truth for **container configuration** —
compose files per service, `.env.template` files referencing secrets in
Keeper, helper scripts for access and rotation. Live state (databases,
media libraries, on-host config dirs) stays on the hosts under
`/docker/<service>/` and isn't moved by anything in here.

> **New here?** Read [`CLAUDE.md`](CLAUDE.md) — the orientation for AI
> agents is also the fastest tour for a human.

## Hosts

| Host | LAN IP | Role |
|---|---|---|
| `INT-PER-DK-01` | 10.10.100.196 | Media tier (Jellyfin, Bazarr, Jellyseerr, Audiobookshelf, Firefly III, KMS, ShieldControl, NPM) |
| `INT-PER-DK-02` | 10.10.100.197 | *arr + downloads tier (Sonarr/Radarr/Prowlarr/Lidarr/Readarr, qBit-VPN, SABnzbd, Calibre stack, LazyLibrarian, Maintainerr, readmeabook, the cloudflared tunnel) |

A third address `10.10.100.205` runs Home Assistant (visible in the
cloudflared ingress as `home.internik.net`) but isn't yet inventoried
here.

## Repo layout

```
nikflix/
├── int-per-dk-01/<service>/      compose + .env.template per service
│   ├── README.md                 service table for this host
│   └── audiobookshelf/, bazarr/, firefly/, jellyfin/, jellyseerr/,
│       kms/, npm/                (7 services; shieldcontrol is in its
│                                  own repo)
├── int-per-dk-02/<service>/
│   ├── README.md
│   └── calibre-downloader/, calibre-web/, lazylibrarian/, lidarr/,
│       maintainerr/, prowlarr/, qbit/, radarr/, readarr/, readmeabook/,
│       sabnzbd/, sonarr/, tunnel/  (13 services)
├── docs/
│   ├── architecture.md           hosts, traffic flow, storage roots,
│   │                             open inconsistencies
│   ├── access.md                 cloudflared Access SSH setup +
│   │                             troubleshooting tree
│   ├── keeper.md                 KSM Application + ksm CLI flow
│   └── services/<svc>.md         per-service narrative docs
├── bin/
│   ├── nfssh                     Cloudflare Access SSH wrapper
│   ├── ksm-render                template → .env from Keeper
│   ├── refresh                   render + diff + restart on host
│   ├── probe-form                headless-browser form-element dumper
│   └── probe-form.py             (Playwright in Docker)
├── CLAUDE.md                     orientation for the next AI agent
├── DEPLOYMENT.md                 first-deploy + rotation flow
├── README.md                     ← you are here
├── discovery/                    raw host dumps (gitignored)
└── .gitignore                    secrets, keys, rendered .env files
```

## How it's accessed

Public (via cloudflared connector on DK-02):

- `services.nikflix.net/{sonarr,radarr,prowlarr,sabnzbd,lidarr,readarr,bazarr}` — *arr stack
- `requests.nikflix.net` — Jellyseerr
- `books.nikflix.net`, `dbooks.nikflix.net` — Calibre Web + downloader
- `finance.internik.net` — Firefly III
- `home.internik.net` — Home Assistant (on `.205`)
- `ssh4.internik.net`, `ssh5.internik.net` — SSH for `INT-PER-DK-02` /
  `INT-PER-DK-01`, gated by Cloudflare Access (Service Auth + Azure AD)

All public hostnames terminate at Cloudflare's edge and reach the LAN
through that single cloudflared connector container.

Private (LAN-only):

- Jellyfin web UI on `:8096`, NPM admin on `:81`, KMS on `:1688`,
  ShieldControl on `:8443`, Audiobookshelf on `:13378`, etc. See
  per-host READMEs and [`docs/architecture.md`](docs/architecture.md)
  for the full ingress table.

## Working with the repo

From this sandbox:

```bash
# reach a host
bin/nfssh int-per-dk-01 'docker ps --format "{{.Names}}\t{{.Status}}"'
bin/nfssh int-per-dk-02 'cat /docker/sonarr/docker-compose.yml'
```

On a host (after the repo is cloned to `/home/claude/nikflix/`):

```bash
# rotate one secret end-to-end (after editing the Keeper record's value)
bin/refresh int-per-dk-02 qbit

# render templates without restarting (preview)
bin/ksm-render int-per-dk-02

# discover form selectors for a Keeper PAM RBI autofill rule
bin/probe-form "http://10.10.100.196:8096/web/"
```

Full deployment workflow in [`DEPLOYMENT.md`](DEPLOYMENT.md). Vault
layout and KSM Application setup in [`docs/keeper.md`](docs/keeper.md).
Access troubleshooting tree in [`docs/access.md`](docs/access.md).

## Phase status

| Phase | Status |
|---|---|
| 1. Document current state | done — `docs/architecture.md` + per-service narrative under `docs/services/` |
| 2. Move container configs into git | done — `<host>/<service>/{docker-compose.yml,.env.template}` |
| 3. Wire Keeper Secrets Manager + per-service vault structure | done — INT-PER application, ~24 records across per-service sub-folders, `bin/refresh` flow live; autofill working on audiobookshelf, jellyfin, jellyseerr, npm |
| 4. Rotate exposed secrets | pending — see `discovery/SECRETS.md` (gitignored) |
| 5. Migrate runtime from `/docker → /opt/nikflix` and replace tar-pipe with `git pull` | pending |

## Conventions

- Compose files mirror the live state on the hosts. Bind mounts use
  relative paths (`./config:/config`). `DEPLOYMENT.md` describes the
  data-migration choices when moving to deploy-from-this-repo.
- Real `.env` and `.db.env` files are gitignored at any depth. Only
  `.env.template` files ship.
- Secrets are referenced in templates by **Keeper record title**, not
  UID, so records stay portable across re-creation.
- `discovery/` is gitignored — raw host dumps and the running list of
  exposed-secrets-to-rotate live there.
- `shieldcontrol` is intentionally **not** in this repo — it's its own
  GitHub repo (`AstralWalker0o/ShieldControl`) cloned and built locally
  on DK-01.
- **Nextcloud AIO was retired 2026-05-09** (volumes deleted, ingress
  removed). NPM remains on DK-01 but currently has no active routes;
  candidate for retirement.

## License

Personal infrastructure config — no license. Don't copy without context.
