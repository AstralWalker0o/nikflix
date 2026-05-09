# Reaching the hosts (Cloudflare Access SSH)

Both Docker hosts are reachable over the internet through Cloudflare Tunnel,
gated by Cloudflare Access. SSH access is brokered the same way, so you don't
need a VPN or open SSH port to operate them.

## Public hostnames

| Host | SSH hostname | Origin (LAN) |
|---|---|---|
| `INT-PER-DK-01` | `ssh5.internik.net` | `10.10.100.196:22` |
| `INT-PER-DK-02` | `ssh4.internik.net` | `10.10.100.197:22` |

Both routes are served by the single cloudflared connector running as the
`cloudflared-tunnel` container on DK-02.

## Identity options

Two ways to satisfy the Access policy in front of these hostnames:

1. **Azure AD SSO** (humans). Use `cloudflared access ssh-config` on your
   workstation; the first connection bounces you to the Cloudflare login
   page where you SSO with Azure.
2. **Service token** (`claude-sandbox`). Used by automation in this repo.
   Scoped per-app via the `Service Auth` policy on each Access application.

The service token Client ID + Secret are stored in `.cf-access` (gitignored)
and read by the `bin/nfssh` wrapper. Rotate via Zero Trust → Service Auth
when needed; revoking the token cuts off automation cleanly.

## Cloudflare-side configuration

For each host, three things must be in place:

1. **Tunnel public hostname** — Networks → Tunnels → public hostname:
   - Subdomain: `ssh4` or `ssh5`
   - Domain: `internik.net`
   - Service: `SSH`
   - URL: the host's LAN IP, e.g. `10.10.100.197:22`.
2. **Access application** — Access → Applications → Self-hosted:
   - Application domain matches the SSH hostname.
   - Identity providers include Azure AD and Service Auth.
   - Policy 1 — humans (Allow + your Azure group).
   - Policy 2 — automation (**Service Auth** + Service Token =
     `claude-sandbox`). The action *must* be `Service Auth`, not `Allow`.
3. **WAF skip rule** — Security → WAF → Custom rules. Cloudflare's default
   bot/security rules block hosting-provider IPs (where automation often
   runs from) and have to be skipped *only when our service token is
   present on an SSH hostname*:
   ```
   (http.host wildcard "ssh*.internik.net"
    and http.request.headers["cf-access-client-id"][0]
        eq "<service-token-client-id>")
   ```
   Action: **Skip**, with all WAF features and Bot Fight Mode in the skip
   list. Place at position **First**. Without this rule, requests from
   sandboxes / CI / cloud IPs return HTTP 403 from the edge before Access
   ever gets consulted.

## Host-side prerequisites

On each host:

1. **`claude` user** with the public key from the sandbox in
   `~/.ssh/authorized_keys`, in the `docker` group:
   ```bash
   sudo useradd -m -s /bin/bash claude
   sudo usermod -aG docker claude
   sudo install -d -m 700 -o claude -g claude /home/claude/.ssh
   sudo tee /home/claude/.ssh/authorized_keys >/dev/null <<'EOF'
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOH9BPMTUZ1gQ2vYgzesrwj3fd4zJHU8Rs1ZY42kTt1Y claude-sandbox
   EOF
   sudo chmod 600 /home/claude/.ssh/authorized_keys
   sudo chown claude:claude /home/claude/.ssh/authorized_keys
   ```
2. **sshd listens on the LAN interface** (not `127.0.0.1` only). Default
   Ubuntu config does this; verify with `ss -tlnp | grep :22`.
3. **(DK-02 only — runs the tunnel)** the cloudflared container has
   `extra_hosts: ["host.docker.internal:host-gateway"]` if any tunnel
   route ever needs to talk to a process on the host loopback. Currently
   no route uses `host.docker.internal` (we use LAN IPs), but the entry
   is harmless.

## Reaching a host from this repo

The `bin/nfssh` wrapper handles all of the above:

```bash
bin/nfssh int-per-dk-01 'docker ps --format "{{.Names}}"'
bin/nfssh int-per-dk-02 'cat /docker/sonarr/docker-compose.yml'
```

Resolution order:

1. `bin/nfssh <host-key> <command>` reads `<host-key>` from `.cf-hosts`,
   producing the SSH hostname and unix user.
2. Sources `.cf-access` for the service-token credentials.
3. Wraps `ssh` with `ProxyCommand=cloudflared access ssh …`. cloudflared
   accepts the service token via flags and tunnels SSH bytes through.
4. Uses `.cf-ssh-key` for publickey auth (a non-passphrase fallback path
   uses an askpass shim if the key was generated with a passphrase).

`.cf-access`, `.cf-hosts`, `.cf-ssh-key`, `.ssh-known_hosts` are all
gitignored.

## When SSH stops working: troubleshooting tree

Symptoms tend to map to a layer:

| Symptom | Likely cause | Fix |
|---|---|---|
| `HTTP 403` from a `curl https://ssh4...` probe with a "Sorry, you have been blocked" body | Cloudflare WAF | Confirm the WAF skip rule is in place and matches the hostname pattern + service token header; check Security → Events for the Ray ID |
| `HTTP 302` redirect to `cloudflareaccess.com/cdn-cgi/access/login/...` | Access policy not accepting the token (`service_token_status: false` in the redirect JWT) | The Access policy must use action `Service Auth`, not `Allow`; the included service token must match |
| `HTTP 502` with body `protocol error` | Tunnel reaches an origin that isn't sshd, or sshd not bound to the right interface | Public hostname Service type must be SSH (not HTTP); URL must point to a host:port where sshd listens; container restart needed if `extra_hosts` was added |
| `websocket: bad handshake` from cloudflared with no further detail | Same as one of the HTTP layers above; run a `curl -i -H` against the hostname to surface the underlying status code |
| `Permission denied (publickey,password)` after a successful SSH banner | publickey auth failed: user missing on host, key not in `authorized_keys`, perms wrong (`.ssh` 700, `authorized_keys` 600), or wrong shell | `id claude && sudo cat /home/claude/.ssh/authorized_keys` on the host |
