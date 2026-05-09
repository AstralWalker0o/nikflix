# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal homelab config — two Docker hosts (`INT-PER-DK-01`, `INT-PER-DK-02`)
running ~25 services. Compose files + per-host READMEs live under
`int-per-dk-XX/<service>/`. Live data and `/docker/<svc>/` directories
on the hosts are the source of truth for *runtime state*; this repo is
the source of truth for *configuration*. They are kept in sync via
`bin/refresh` (Keeper → host), and via the hand-edits / cutover process
documented in `DEPLOYMENT.md`.

Read `docs/architecture.md` first if this is a fresh session — it has the
host map, public-hostname routing, internal traffic shape, and a
numbered list of inconsistencies / open questions surfaced during
discovery (PUID drift, `version: "2.1"` cruft, `firefly/.db.env`
duplicate password, `calibre-downloader → calibre-web` cross-folder
mount, `readarr/data.old/`, etc.). `docs/access.md` has the SSH-via-
Cloudflare-Access setup. `docs/keeper.md` has the Keeper Secrets Manager
flow.

## Reaching the hosts

Both DK hosts are gated by Cloudflare Access (Service Auth policy).
The `bin/nfssh` wrapper handles the dance:

```bash
bin/nfssh int-per-dk-01 'docker ps --format "{{.Names}}"'
bin/nfssh int-per-dk-02 'cat /docker/sonarr/docker-compose.yml'
```

Resolution: `.cf-hosts` (gitignored) maps host-key → SSH hostname + unix
user; `.cf-access` (gitignored) holds the service-token credentials;
`.cf-ssh-key` (gitignored) is the SSH private key (passphrase-protected,
askpass shim at `/tmp/askpass.sh` reads from `/tmp/.cf-key-pass`).

If `bin/nfssh` is broken, the troubleshooting tree in `docs/access.md`
maps each error symptom (HTTP 403 / 302 / 502, websocket bad handshake,
publickey denied) to its cause.

`/docker/*/` is **world-writable on both hosts**, so the `claude` user
can edit configs without sudo. `claude` is in the `docker` group on both
hosts.

## Keeper Secrets Manager (Phase 3, live)

`int-per-dk-01/firefly/.env`, `firefly/.db.env`, `int-per-dk-02/qbit/.env`,
`int-per-dk-02/tunnel/.env` are populated from Keeper at deploy time —
*not* committed. Each service that needs secrets has a checked-in
`.env.template` referencing records by **title** (not UID):
`{{keeper:firefly-app/DB_PASSWORD}}` etc.

Two CLIs are pre-installed on each host under `/home/claude/.local/bin/`:

- **`ksm`** (`keeper-secrets-manager-cli`) — the headless client. Uses the
  `INT-PER` Secrets Manager Application (UID `IW6A0EPO6oC6nx7rF6hKkg`)
  via `~/keeper.ini`. Read/edit access on the `INT-PER` shared folder.
  Used by `bin/ksm-render` to resolve `{{keeper:title/field}}`
  placeholders.
- **`keeper`** (`keepercommander`) — the full Commander CLI, signed in as
  `nik@nebulait.au` with persistent device login at `~/.keeper/config.json`.
  Used for record/folder CRUD and PAM operations. **Session expires
  after some idle period** and any write op then triggers an interactive
  SSO Connect URL prompt that you cannot complete from this sandbox. If
  that happens, ask the user to `sudo -iu claude && keeper login
  nik@nebulait.au` on the host (their PAM SSH).

### Rotation flow — one command

```bash
bin/refresh int-per-dk-02 qbit       # one service
bin/refresh int-per-dk-02            # everything on DK-02 with templates
```

Walks `<host>/*/`, calls `bin/ksm-render`, diffs the rendered env against
`/docker/<svc>/.env`, backs up the live copy as `*.bak.<timestamp>`, and
`docker compose up -d --force-recreate`s only services whose env
actually changed. Idempotent. **Use the `docker compose` v2 plugin** —
the legacy `docker-compose` v1 binary is broken with Engine 29
(`KeyError: 'ContainerConfig'`); we installed the v2 plugin user-level
at `~/.docker/cli-plugins/docker-compose`.

### Vault structure

```
INT-PER/                                  (shared with KSM Application "INT-PER")
├── INT-PER-DK-01/
│   ├── Connection/                       (existing pamMachine + pamUser records — don't touch)
│   └── Services/<svc>/                   <svc>-web (pamRemoteBrowser) + secret records as needed
└── INT-PER-DK-02/
    ├── Connection/                       (don't touch)
    └── Services/<svc>/                   same shape
```

Records like `firefly-app`, `qbit`, `tunnel` are at `Services/<svc>/`.
Each service that has a web UI also has a `<svc>-web` `pamRemoteBrowser`
record with `rbiUrl`, `pamRemoteBrowserSettings`, and
`trafficEncryptionSeed` populated.

## Keeper PAM Remote Browser autofill

`autofillConfiguration` lives inside `pamRemoteBrowserSettings.connection`
as a JSON string. Format:

```json
[{"page":"http://host:port/path","username-field":"input[name='username']","password-field":"input[name='password']"}]
```

Apply via:

```bash
keeper pam rbi edit -r <UID> --autofill-targets "$(cat /tmp/autofill.json)"
```

**Two non-obvious gotchas** discovered the hard way:

1. `page` must be the **actual final URL** the page settles at after
   redirects, not a wildcard. For SPAs with hash routes, include the
   hash (`/web/#/login`) — Keeper appears to match `location.href`.
   Multiple page rules in one array work for covering variants.
2. CSS selectors with attribute values use **single quotes** around the
   value: `input[name='username']`. Bash's quoting will eat them — write
   the JSON to a file and pass via `"$(cat …)"`.

To discover the right selectors for a service, use `bin/probe-form` on
the host (Microsoft Playwright Python image, runs in a Docker container
with `--network host` so LAN URLs work):

```bash
bin/probe-form "http://10.10.100.196:8096/web/"
```

It dumps every `<input>`, `<select>`, `<button>` with id, name, type,
autocomplete, formcontrolname, etc. Also reports the rendered URL after
JS routing — that's what to put in `page`.

## Live cutover state

`/docker/<svc>/` on both hosts is **still the running deployment**. We
don't run `docker compose` from this repo's tree yet. Per-service
`*.pre-keeper-bak` backups exist for rollback (delete them once you're
confident). `bin/refresh` writes new `.env`s into `/docker/<svc>/`, not
into the repo location. Eventually the `/docker → /opt/nikflix`
migration in `DEPLOYMENT.md` lets us deploy directly from a `git pull`.

## Things to be careful about

- **The cloudflared tunnel container on DK-02 is the SPOF for all public
  access**, including the SSH path Claude uses to reach the host. A
  failed `docker compose up -d` on `int-per-dk-02/tunnel/` cuts off
  everything. The container's TUNNEL_TOKEN now comes from `${TUNNEL_TOKEN}`
  in `.env`. Always pre-validate via `docker compose config` before
  recreating.
- **`shieldcontrol` is excluded from the per-service repo tree** by
  user request. It's a separate GitHub repo (`AstralWalker0o/ShieldControl`)
  cloned at `/docker/shieldcontrol/` on DK-01 and built locally. Don't
  vendor its source here.
- **`/docker/shieldcontrol/.git/config` had a GitHub PAT in clear** at
  discovery time. It's in `discovery/SECRETS.md` (gitignored). Rotation
  is pending — see open items.
- **Don't share `~/.keeper/config.json` (Commander persistent device
  token) outside the host.** It grants full vault access to
  `nik@nebulait.au`. KSM's `~/keeper.ini` is narrower (only the INT-PER
  folder) and is the right credential to use for read-only operations.

## Repo conventions

- Compose files preserve the *live* state (relative bind mounts like
  `./config`, etc.) — don't rewrite to absolute paths or restructure
  bind mounts. `DEPLOYMENT.md` documents how data migrates if/when we
  move away from `/docker`.
- `.env.template` files reference records by **title** (`firefly-app`,
  `qbit`, `tunnel`). Field names inside templates match Keeper custom-
  field labels exactly (case-sensitive).
- Discovery dumps and rendered `.env` files stay gitignored; only
  `.env.template` ships.
- Scripts in `bin/` are bash + Python. `bin/probe-form` is a Docker
  wrapper.

## Common tasks

```bash
# discover service info on a host
bin/nfssh int-per-dk-01 'ls /docker; docker ps --format "{{.Names}}\t{{.Status}}"'

# render a single service's env locally (sandbox repo) — purely for diff
bin/ksm-render int-per-dk-01 firefly   # actually requires ksm CLI; runs on host

# rotate a secret end-to-end (after editing the Keeper record's value)
bin/nfssh int-per-dk-XX '/home/claude/nikflix/bin/refresh int-per-dk-XX <svc>'

# add an autofill rule to a pamRemoteBrowser record (run on host)
echo '[{"page":"...","username-field":"...","password-field":"..."}]' > /tmp/af.json
keeper pam rbi edit -r <web-record-UID> --autofill-targets "$(cat /tmp/af.json)"

# discover form selectors on any LAN URL
bin/nfssh int-per-dk-01 '/home/claude/nikflix/bin/probe-form "<url>"'
```

## Open work

In `discovery/SECRETS.md` (gitignored) and at the bottom of
`docs/architecture.md`. Headlines:

1. **Rotate exposed secrets** — GitHub PAT (urgent), PIA, TUNNEL_TOKEN,
   firefly's MAIL_PASSWORD/APP_KEY/etc., Cloudflare Access service
   token. The `bin/refresh` flow makes (2)–(4) trivial after rotating
   at the source vendor.
2. **Roll out autofill** to the remaining 17 web records (audiobookshelf
   and jellyfin are done, jellyseerr and npm just configured; the rest
   pending). Use `bin/probe-form` to discover selectors.
3. **Migrate `/docker → /opt/nikflix`** so we deploy from `git pull`
   rather than tar-pipe.
4. **Replace tar-pipe with `git pull`** on hosts. Currently the host's
   `/home/claude/nikflix/` is populated by an explicit tar transfer
   from this sandbox. See `DEPLOYMENT.md`.
5. **Stale-config normalisation** — PUID/PGID drift, TZ drift,
   `version: "2.1"` removal, `readarr/data.old/` cleanup, `maintainerr`
   `/mnt/datadisk01` outlier mount, etc. None blocking; cosmetic +
   correctness.
