# Keeper Secrets Manager (KSM)

How secrets get from your Keeper vault into the running containers, and how
to set the Keeper side up for the first time.

## Why KSM, not PAM, not a regular user

KSM Applications are headless service identities. They:

- **Don't consume a user license** (free with Keeper Business/Enterprise).
- Have their own config / token, completely separate from your account.
- Can be scoped to specific records or folders only — no access to the rest
  of your vault.
- Fetch secrets without a browser or interactive login.
- Are revocable independently from any human account.

Each Docker host gets its own KSM Application, sharing **only** the records
that host needs. If `INT-PER-DK-02`'s ksm config leaks, `INT-PER-DK-01`'s
secrets are unaffected.

## Vault layout you need to create

Create this folder hierarchy in your vault. The exact record types don't
matter — `Login`, `Server Credentials`, or generic `File` records all work
as long as they have **custom fields** with the names below.

```
Nikflix/                                    (organisational folder)
├── secrets-manager/
│   ├── int-per-dk-01/                      ← share with KSM App "nikflix-dk-01"
│   │   ├── firefly-app                     (record)
│   │   │   custom fields:
│   │   │     APP_KEY                       e.g. base64:hellohello…
│   │   │     DB_PASSWORD                   ← also referenced by firefly-db
│   │   │     MAIL_PASSWORD
│   │   │     STATIC_CRON_TOKEN
│   │   │     FIREFLY_III_ACCESS_TOKEN
│   │   │     AUTO_IMPORT_SECRET
│   │   └── firefly-db                      (record)
│   │       custom fields:
│   │         MYSQL_PASSWORD                ← same value as firefly-app/DB_PASSWORD
│   │
│   └── int-per-dk-02/                      ← share with KSM App "nikflix-dk-02"
│       ├── qbit                            (record)
│       │   custom fields:
│       │     VPN_USER
│       │     VPN_PASS
│       │     SOCKS_USER
│       │     SOCKS_PASS
│       └── tunnel                          (record)
│           custom fields:
│             TUNNEL_TOKEN
```

Field names are case-sensitive. Use **exactly** the names above — the
templates in this repo (`<service>/.env.template`) reference them by name.

## KSM Application setup

In the Keeper Web Vault → **Secrets Manager** (left nav, looks like a key
icon under Apps).

1. **Create application** → name it `nikflix-dk-01`.
2. Add a **Folder share** for `Nikflix/secrets-manager/int-per-dk-01/`,
   permission *Can Edit* (so the app can read all current and future
   records in that folder).
3. **Add Device → One-Time Access Token**. Save the token —
   you'll use it once to initialise `ksm` on the host. It's
   single-use.
4. Repeat for `nikflix-dk-02` with the corresponding folder + a separate
   one-time token.

## Host-side initialisation

Once per host. Done by you (one-time token shouldn't pass through the
sandbox — it's better that you initialise locally and the persistent
config lives only on the host).

```bash
# on the host, as the claude user
mkdir -p ~/.keeper
curl -fsSL https://keeper-security.github.io/gitops-cdn/scripts/ksm-cli.sh | bash
# now `ksm` is on PATH

ksm init default --token <YOUR_ONE_TIME_TOKEN>
# this creates ~/.keeper/client-config.json — the persistent KSM identity

# smoke test
ksm secret list
# should show the records you shared with this host's app
```

## Rendering .env files from templates

In this repo, each service that needs secrets has a `.env.template`
alongside its `docker-compose.yml`. Templates use a simple
`{{keeper:<record-title>/<field-name>}}` placeholder.

The `bin/ksm-render` script walks a host's tree and renders every
`.env.template` to a sibling `.env` file:

```bash
bin/ksm-render int-per-dk-01           # render all DK-01 envs
bin/ksm-render int-per-dk-02 qbit      # render only the qbit env on DK-02
```

`.env` files are gitignored. They're regenerated on demand from Keeper.

## Day-to-day

- **New secret needed by a service:** add the field to the relevant
  Keeper record, add `{{keeper:…}}` placeholder to the service's
  `.env.template`, run `bin/ksm-render`. No vault re-share or app
  recreate needed.
- **Rotate a secret:** edit the Keeper record's value, run
  `bin/ksm-render` to regenerate `.env`, then `docker compose up -d`
  the service.
- **Revoke host access:** Secrets Manager → the application → Devices →
  remove. Host's persistent config becomes useless immediately.

## What's intentionally not in Keeper

- The `ksm` persistent config itself (`~/.keeper/client-config.json`) —
  it's the bootstrap credential, lives on the host filesystem at 600.
- The Cloudflare Access service token + SSH key in this sandbox
  (`.cf-access`, `.cf-ssh-key`) — Phase 4 work, lower priority.
