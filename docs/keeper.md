# Keeper Secrets Manager (KSM)

How secrets get from your Keeper vault into the running containers.

## Why KSM, not PAM, not a regular user

KSM Applications are headless service identities. They:

- **Don't consume a user license** (free with Keeper Business/Enterprise).
- Have their own config / token, completely separate from your account.
- Can be scoped to specific records or folders only — no access to the rest
  of your vault.
- Fetch secrets without a browser or interactive login.
- Are revocable independently from any human account.

## Vault layout

```
INT-PER/                                    (folder — shared with KSM Application "INT-PER")
├── INT-PER-DK-01/
│   └── Services/
│       └── firefly/                        (sub-folder)
│           ├── firefly-app                 (record — title is what bin/ksm-render looks up)
│           │   custom fields:
│           │     APP_KEY                   e.g. base64:hellohello…
│           │     DB_PASSWORD               (also referenced by firefly-db)
│           │     MAIL_PASSWORD
│           │     STATIC_CRON_TOKEN
│           │     FIREFLY_III_ACCESS_TOKEN
│           │     AUTO_IMPORT_SECRET
│           └── firefly-db
│               custom fields:
│                 MYSQL_PASSWORD            (= firefly-app/DB_PASSWORD)
│
└── INT-PER-DK-02/
    └── Services/
        ├── qbit                            (record)
        │   custom fields:
        │     VPN_USER
        │     VPN_PASS
        │     SOCKS_USER
        │     SOCKS_PASS
        └── tunnel                          (record)
            custom fields:
              TUNNEL_TOKEN
```

The KSM Application is shared with the top-level `INT-PER` folder, so it
inherits access to everything below.

**Record titles are the lookup key.** The templates in this repo reference
records by exact (case-sensitive) title: `firefly-app`, `firefly-db`,
`qbit`, `tunnel`. The folder hierarchy can be anything you like — the
renderer doesn't care where the record lives, only that a record with
that title is shared with the Application.

**Field names matter too.** They must match the `{{keeper:<title>/<field>}}`
references in each `.env.template`. Use the exact names above.

### Tradeoff worth knowing

A single `INT-PER` Application means both hosts can read every secret in
the tree. If the persistent KSM config on `INT-PER-DK-02` were stolen, an
attacker could also pull `INT-PER-DK-01`'s firefly secrets, and vice
versa. Acceptable in a homelab; in a tighter blast-radius design you'd
have one Application per host. Easy to switch later — split the folder
share, create a second Application — without touching the templates.

## KSM Application setup

In the Keeper Web Vault → **Secrets Manager** (under Apps in the left nav).

1. **Create application** → name it `INT-PER`.
2. **Add a folder share** for the top-level `INT-PER` folder, permission
   *Can Edit* (so the app can read all current and future records under
   it).
3. **Add Device → Add Device → One-Time Access Token.** Generate one
   token, save it, then **generate a second OTT** for the second host.
   Each host needs its own OTT — they're single-use, and using one
   registers a unique "device" under the Application with its own
   persistent config.

## Host-side initialisation

Once per host. Better done by you on the host directly so the
one-time tokens don't pass through this sandbox. As `claude` on each
host:

```bash
# install the ksm CLI (Python package — Ubuntu has python3 + pip3)
sudo apt-get install -y python3-pip
pip install --user keeper-secrets-manager-cli
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# initialise with this host's one-time token
ksm profile init --token <YOUR_ONE_TIME_TOKEN_FOR_THIS_HOST>
# this writes ~/.keeper/ksm-config.json — the persistent KSM identity

# smoke test
ksm secret list
# should show the records that this host's app can read
```

If pip-in-userspace isn't desirable, the Go-based `ksm-cli` is also an
option (single static binary). Either CLI exposes the same JSON shape
that `bin/ksm-render` consumes.

## Rendering .env files from templates

Each service that needs secrets ships a `.env.template` next to its
`docker-compose.yml`. Templates use a simple
`{{keeper:<record-title>/<field-name>}}` placeholder.

The `bin/ksm-render` script walks a host's tree and renders every
`.env.template` to a sibling `.env` file (mode 0600):

```bash
bin/ksm-render int-per-dk-01           # render all DK-01 envs
bin/ksm-render int-per-dk-02 qbit      # render only the qbit env on DK-02
```

`.env` files are gitignored. They're regenerated on demand from Keeper.

## Day-to-day

- **New secret needed by a service:** add the field to the relevant
  Keeper record, add `{{keeper:…}}` placeholder to the service's
  `.env.template`, run `bin/ksm-render`. No vault re-share or app
  re-create needed (the share at folder level already covers it).
- **Rotate a secret:** edit the Keeper record, run `bin/ksm-render` to
  regenerate `.env`, then `docker compose up -d` the service.
- **Revoke a host's access:** Secrets Manager → INT-PER → Devices →
  remove the device for that host. The host's persistent config becomes
  useless immediately. The other host(s) keep working.

## What's intentionally not in Keeper

- The `ksm` persistent config itself (`~/.keeper/ksm-config.json`) — it's
  the bootstrap credential, lives on the host filesystem at 600.
- The Cloudflare Access service token + SSH key in this sandbox
  (`.cf-access`, `.cf-ssh-key`) — Phase 4 work, lower priority.
