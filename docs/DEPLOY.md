# Server deployment

Run the workshop app as a Docker container.

**Current shared demo:** app on **cci-demo** (`https://cci-demo.ucd.ie/`, host port **5001**), LLM on **worf** (`172.28.0.153:8001`). `.env.example` matches that layout.

Workshop day alternative: **app + LLM both on worf** (see below; switch `LLM_URL` to `host.docker.internal`).

## Running on cci-demo (app on demo VM → LLM on worf)

1. Clone and use the workshop branch:

```bash
cd ~
git clone https://ccilab.ucd.ie/cci/workshop-aida-app.git
cd workshop-aida-app
git checkout feature/classic-and-worf-pilot
cp .env.example .env
# Edit SESSION_SECRET. Defaults already set:
#   HOST_PORT=5001
#   LLM_URL=http://172.28.0.153:8001/v1/chat/completions
```

2. Confirm the demo VM can reach worf’s LLM:

```bash
curl -sS -m 10 http://172.28.0.153:8001/v1/models | head
```

3. Start the app (do **not** enable `docker-compose.room-auth.yml` — the VM nginx already has Basic Auth):

```bash
docker compose up -d --build
docker compose exec break-ai-app python tests/test_llm.py
```

4. Point the site nginx `proxy_pass` at `http://127.0.0.1:5001` if participants use `https://cci-demo.ucd.ie/`. Direct access: `http://cci-demo:5001` if UFW allows it.

## Running on worf (app + LLM same host)

1. Confirm the LLM is listening on the host (typical: port `8001`):

```bash
curl -s http://127.0.0.1:8001/v1/models | head
```

2. Deploy the workshop:

```bash
cd workshop-aida-app
cp .env.example .env
# Edit SESSION_SECRET and override LLM_URL for same-host LLM:
#   LLM_URL=http://host.docker.internal:8001/v1/chat/completions
#   LLM_MODEL=unsloth/Qwen3.8-27B-NVFP4
# Optional: HOST_PORT=8167 if you prefer worf's older published port
# HOST_BIND=0.0.0.0 so participants can hit http://worf:PORT

docker compose up -d --build
```

3. Smoke-test LLM reachability **from inside the app container**:

```bash
docker compose exec break-ai-app python tests/test_llm.py
```

4. Participants open `http://WORF_IP:HOST_PORT` (not `127.0.0.1` from their laptops).

## Optional room gate (HTTP Basic Auth)

For warmup talks and private testers, put an nginx Basic Auth dialog in front of the app. It is intentionally ugly and easy to remove before the main conference. Default credentials: **`conference` / `secret`**.

**Turn ON (warmup):**

```bash
cd ~/workshop-aida-app
cp deploy/room-auth/htpasswd.example deploy/room-auth/htpasswd
# Or set your own: ./scripts/make-room-htpasswd.sh conference secret
docker compose -f docker-compose.yml -f docker-compose.room-auth.yml up -d
```

Participants open the same URL (`http://WORF_IP:8167`); the browser asks for username/password first. The app itself is no longer published on the host — only the gate is.

**Turn OFF (main conference):**

```bash
cd ~/workshop-aida-app
docker compose -f docker-compose.yml -f docker-compose.room-auth.yml stop room-gate
docker compose up -d
```

That restores the app on port 8167 with **no** Basic Auth. Confirm:

```bash
docker compose ps
# expect: break-ai-app … 0.0.0.0:8167->8000
# and no room-gate
```

Requires Docker Compose **v2.24+** (uses `ports: !reset`). Check with `docker compose version`.

Why `host.docker.internal`? The LLM runs on the host (or is published to the host). Inside Docker, `127.0.0.1` is the container itself — not worf. Compose maps `host.docker.internal` to the host gateway so the container can call `8001` on worf.

If the LLM only binds to a LAN IP (for example `172.28.0.153:8001`), you can instead set:

```bash
LLM_URL=http://172.28.0.153:8001/v1/chat/completions
```

That also works when the container can route to that address.

## Running the app elsewhere (laptop → worf LLM)

Use worf’s LAN address from the machine that hosts the container:

```bash
LLM_URL=http://172.28.0.153:8001/v1/chat/completions
```

## Prerequisites

- Docker Engine with Compose plugin
- Network path from the app container to the LLM OpenAI-compatible endpoint
- A copy of this repo on the server

## Quick start

```bash
cd workshop-aida-app
cp .env.example .env
# Edit .env: SESSION_SECRET, LLM_URL, LLM_MODEL, HOST_BIND, HOST_PORT

docker compose up -d --build
```

Open `http://SERVER_IP:8167` (or the port you set in `HOST_PORT`).

Pilot mode (default in `.env.example`):

- Participants: `http://SERVER_IP:8167` → Start → challenges (no login)
- Facilitator testing jumps: `/testing` or `/testing/5`
- Facilitator login (replay logs): `/login` with `admin` / `facilitator`

## Important environment variables

| Variable | Purpose |
|---|---|
| `HOST_BIND` | `0.0.0.0` on a server; keep `127.0.0.1` for laptop-only |
| `HOST_PORT` | Published port (default `5001` for cci-demo; use `8167` on worf if preferred) |
| `LLM_URL` | Chat completions URL **as seen from inside the container** (demo default: worf `172.28.0.153:8001`) |
| `LLM_MODEL` | Model id expected by that endpoint |
| `SESSION_SECRET` | Change before any shared workshop |
| `DM_RPG_MODE` | `pilot` for the LLM levels; omit/`off` for classic keyword mode |
| `APP_MODE` | Keep `vulnerable` for the workshop |

## Database

SQLite lives in `./data` on the host (bind-mounted). On first start the entrypoint seeds `workshop.db` if it is missing.

Reset workshop data:

```bash
docker compose exec break-ai-app python scripts/seed.py
```

## Operations

```bash
docker compose ps
docker compose logs -f break-ai-app
docker compose restart break-ai-app
docker compose down
```

Rebuild after pulling code:

```bash
git pull
docker compose up -d --build
```

## Safety

This app is **deliberately vulnerable**. Run it only on an isolated training network or behind access control. Do not put it on the public internet without a reverse proxy, auth gate, and a conscious risk decision.

Default compose still prefers an explicit `HOST_BIND` so laptop builds stay localhost-safe unless you set `0.0.0.0`.
