# shieldcontrol

**Host:** INT-PER-DK-01 (10.10.100.196)
**Image:** _built locally_ from `/docker/shieldcontrol/Dockerfile` (multi-stage)
**Containers:** `shieldcontrol_app_1`, `shieldcontrol_adb_1`
  (+ `builder` profile, on-demand)
**Compose:** `/docker/shieldcontrol/docker-compose.yml`
**Public:** _(not in cloudflared ingress)_ — host port `8443` only

## Ports
- `8443:8443` — app (HTTPS)
- `5037:5037` — ADB server

## Volumes (named)
- `db-data` → `/app/data` (app)
- `apk-store` → `/app/apks` (app), `/output` (builder)
- `adb-keys` → `/root/.android` (adb)
- `gradle-cache` → `/root/.gradle` (builder)
- Also bind-mounts `/var/run/docker.sock` (app spawns containers).

## Environment
- `app`:
  - `ADB_SERVER_HOST=adb`, `ADB_SERVER_PORT=5037`
  - `DATABASE_PATH=/app/data/shieldcontrol.db`
  - `LOG_LEVEL=info`
  - `JWT_SECRET=${JWT_SECRET:-}` — currently no `.env` on the host, so
    this is empty. The application likely needs a real value for secure
    session signing — confirm and populate from Keeper.
- `adb`:
  - `DEVICES=${DEVICES:-}` — empty default.
- `builder` (profile-gated):
  - `BUILD_TYPE=${BUILD_TYPE:-debug}`, `OUTPUT_DIR=/output`

## What it is

Custom Python (FastAPI?) + React frontend app that talks to NVIDIA Shield
Android TV devices over ADB. Source lives entirely under
`/docker/shieldcontrol/`:

- `Dockerfile` — Stage 1: React build. Stage 2: Python 3.12 + ADB tools +
  Docker CLI static binary. Includes a `companion/` and a
  `Dockerfile.builder` which the app uses to build the Android companion
  APK on demand.
- `Dockerfile.adb` — Alpine + `android-tools`, runs an ADB server.
- `Dockerfile.builder` — Android APK builder (Gradle).

## Notes

- Privileged ADB container.
- Source code is meaningful (this is the only service whose deployment
  *includes its own source*). When we restructure into a GitHub-deployable
  layout, decide:
  - **Inline:** keep the source at `services/shieldcontrol/` and `docker-compose`
    builds locally on the target host. Simple but redeploys are slower
    (build time, source size).
  - **Split:** move shieldcontrol source to its own repo, publish images
    to a registry (GHCR), pull from there in this repo's compose.
    Cleaner separation, faster redeploys.
