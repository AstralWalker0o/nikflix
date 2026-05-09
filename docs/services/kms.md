# kms

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** `mikolatero/vlmcsd:latest`
**Container:** `kms`
**Compose:** `/docker/kms/docker-compose.yml`
**Public:** _(not in cloudflared ingress; not internet-routable)_ — host
port `1688` on LAN only.

## Ports
- `1688:1688`

## Bind mounts
| Host | Container |
|---|---|
| `/docker/kms/config` | `/config` |

## Environment
- `PUID=1001 PGID=1001 TZ=Australia/Perth`

## Notes
- KMS emulator (vlmcsd) for activating Microsoft / Office on local network
  machines. Specific to home-lab use; should never be exposed publicly.
