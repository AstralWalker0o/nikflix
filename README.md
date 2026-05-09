# nikflix

Personal homelab for media (movies, TV, music, books, audiobooks), automation
(Home Assistant, Zigbee), productivity (Firefly III), and a bunch of
adjacent services. Built incrementally over ~10 years across local and cloud
generations.

Everything is Docker. Public access is brokered by **Cloudflare Tunnel** with
**Cloudflare Access** policies for Zero Trust SSO via Azure AD.

## Repo purpose

Two goals, both in flight:

1. **Document the current state** — what runs where, how services depend on
   each other, where secrets live, what the public hostname routing looks like.
   See [`docs/architecture.md`](docs/architecture.md).
2. **Move container configs to GitHub** so a fresh redeploy of any host is a
   `git clone` + `docker compose up` away, with secrets pulled from Keeper at
   deploy time rather than baked into compose files.

The repo is on a feature branch (`claude/initialize-system-aCBFE`) while we
inventory and restructure. Today the live configs still live on each Docker
host under `/docker/<service>/`; this repo is being populated to mirror and
ultimately replace them.

## Hosts in scope

| Host | LAN IP | Role |
|---|---|---|
| `INT-PER-DK-01` | 10.10.100.196 | Media server tier (Jellyfin, Bazarr, Firefly III, ShieldControl, etc.) |
| `INT-PER-DK-02` | 10.10.100.197 | *arr + downloads tier (Sonarr/Radarr/Prowlarr/Lidarr/Readarr, qBit-VPN, SABnzbd, Calibre, cloudflared tunnel) |

A third LAN address (`10.10.100.205`) appears in the cloudflared ingress for
Home Assistant; it isn't yet in scope for this discovery pass.

## Layout (current)

```
.
├── bin/                 helper scripts (e.g. nfssh wrapper for SSH-via-Access)
├── docs/                architecture, access, per-service notes
│   ├── architecture.md
│   ├── access.md
│   └── services/        one file per service
├── discovery/           raw dumps from each host (gitignored)
└── README.md
```

The `.cf-*` and `.keeper/` paths in `.gitignore` are credentials and tooling
artefacts — never committed.

## Quick references

- [Architecture & traffic flow](docs/architecture.md)
- [How to reach hosts (cloudflared Access SSH)](docs/access.md)
- [Service inventory](docs/services/)
