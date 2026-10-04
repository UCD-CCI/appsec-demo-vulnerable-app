# Testing throughput and concurrent capacity

## Goals (this workstream)

1. **See what happens when 10 people chat at once** — measure latency, errors, timeouts.  
2. **See what happens when more than 10 do** — ramp (e.g. 15 → 20 → 30) until quality collapses.  
3. **Set an access limit** at the cliff — reject or soft-fail new chats when in-flight load would hurt the room.

Separate from challenge design / slides. Stack: **cci-demo app → worf LLM** (`172.28.0.153:8001`).

## What we limit

For “N people talking at once”, the useful control is **in-flight `/api/chat` calls** (each holds an LLM request), not Basic Auth seats.

| Control | Env var | Behaviour |
|---------|---------|-----------|
| Chat concurrency cap | `MAX_INFLIGHT_CHATS` | If set to N &gt; 0, the (N+1)th simultaneous chat gets a busy message instead of calling the LLM. `0` = unlimited (default until we measure). |

Session “room full” (100 browsers) can come later if needed; it does not protect the GPU by itself.

**How concurrency actually works:** pilot `/api/chat` offloads blocking LLM work onto a dedicated thread pool so uvicorn’s event loop stays free. Page loads and `/testing/N` are not blocked behind an in-flight chat. Still **one uvicorn worker**; capacity is thread-pool waiters + worf’s own queue, not multi-process.

## How to run the load test

**Path under test:** script → **app** (`POST /api/chat`) → **LLM on worf**.  
We do **not** call the LLM URL directly — same path as a browser participant.

Script: `scripts/load_chat_concurrency.py`  
Run from a host that can reach the app **and** whose app can reach worf (best: **on cci-demo**).

Each simulated person:
1. `GET /` — session cookie  
2. `GET /testing/1` — Level 1 (LLM-backed)  
3. **Barrier** — all workers finish setup, then fire chats together  
4. `POST /api/chat` — short message (app calls the LLM)

The script reports **setup_s**, **chat_s**, and **total_s** separately (older runs only timed chat POST and understated setup queueing when the event loop was frozen).

```bash
cd ~/workshop-aida-app

# Baseline: 1 chatter
python3 scripts/load_chat_concurrency.py --base-url http://127.0.0.1:8167 --concurrency 1

# Goal 1: 10 at once
python3 scripts/load_chat_concurrency.py --base-url http://127.0.0.1:8167 --concurrency 10

# Goal 2: more than 10
python3 scripts/load_chat_concurrency.py --base-url http://127.0.0.1:8167 --concurrency 15
python3 scripts/load_chat_concurrency.py --base-url http://127.0.0.1:8167 --concurrency 20
python3 scripts/load_chat_concurrency.py --base-url http://127.0.0.1:8167 --concurrency 30
```

Against public HTTPS (edge Basic Auth — set env vars in your shell only, never commit):

```bash
export CCI_DEMO_USER='…'
export CCI_DEMO_PASSWORD='…'
python3 scripts/load_chat_concurrency.py \
  --base-url https://cci-demo.ucd.ie \
  --concurrency 1
```

Or pass `--basic-user` / `--basic-password` on the command line (still do not write them into tracked files).

### Prove the busy cap locally

```bash
# Temporarily: MAX_INFLIGHT_CHATS=2 in .env, rebuild, then:
python3 scripts/load_chat_concurrency.py --base-url http://127.0.0.1:8167 --concurrency 5
# Expect some BUSY replies (source capacity-limit). Restore MAX_INFLIGHT_CHATS=0 or 15 after.
```

## Results

### Pre-fix (event loop frozen — historical)

Short “what is your name?” via `https://cci-demo.ucd.ie` → app → worf. Chats were effectively serialised in the app process; `MAX_INFLIGHT_CHATS` could never exceed 1; page setup queued behind chats.

| Concurrency | OK | Fail/timeout | p50 (s) | p95 (s) | Notes |
|-------------|----|--------------|---------|---------|-------|
| 1 | 1 | 0 | 1.4 | 1.4 | baseline |
| 10 | 10 | 0 | 5.6 | 9.3 | usable |
| 20 | 20 | 0 | 8.3 | 15.5 | queueing; still all OK |
| 30 | 30 | 0 | 7.8 | 13.8 | still all OK for short replies |

**Re-run the ramp after the thread-pool fix** (barrier + split timings) before trusting new numbers for workshop day.

**Caveat:** Level 1–2 workshop answers use more tokens and often a judge call too. Expect roughly **2× (or worse)** wait under the same concurrency. A follow-up ramp with a long disclosure-style message is worth one run before workshop day.

**Cliff rule of thumb:** first concurrency where p95 &gt; ~45–60s, or error/timeout rate &gt; ~10%, or replies become “model unavailable”.

## Recommended limit

For **room UX**, recommend:

| Setting | Value | Why |
|---------|-------|-----|
| `MAX_INFLIGHT_CHATS` | **15** | Busy message instead of unbounded queues when everyone hits Send together; re-tune after post-fix ramp |

Alternatives: **10** if you want snappier; **20** if you prefer fewer busy messages.

Deploy on cci-demo only in **local `.env`** (not committed):

```bash
# on cci-demo — after pulling code with thread-pool offload + MAX_INFLIGHT_CHATS
grep MAX_INFLIGHT .env || echo 'MAX_INFLIGHT_CHATS=15' >> .env
# edit to 15 if the line already exists as 0
docker compose up -d --build
```

Then confirm: concurrency 15 → mostly OK; concurrency 25 → some `BUSY` replies.

## Nginx timeouts

Repo room-auth gate ([deploy/room-auth/nginx.conf](../deploy/room-auth/nginx.conf)) sets `proxy_read_timeout 180s` so chats are not killed at nginx’s default **60s** while `LLM_TIMEOUT` is often 120.

**cci-demo’s VM nginx is not in this repo.** After deploy, check that host config for `proxy_read_timeout` (and send) ≥ chat wait budget, or browsers will see 504s while the app is still waiting on worf.

## Implementation status

- [x] Plan + load script (barrier + setup/chat/total timings)  
- [x] App support for `MAX_INFLIGHT_CHATS` (0 = off)  
- [x] Pilot chat offloaded to thread pool (event loop no longer frozen)  
- [x] Room-auth nginx `proxy_read_timeout 180s`  
- [x] Run 1 → 10 → 20 → 30 (short prompt) via public demo URL *(pre-fix; re-run after deploy)*  
- [ ] Pull/rebuild on cci-demo; set `MAX_INFLIGHT_CHATS=15` in server `.env` only  
- [ ] Verify VM nginx `proxy_read_timeout` on cci-demo  
- [ ] Optional: one ramp with a **long** Level-1 style message  
- [ ] Optional later: session admission cap for “room full”; multi-worker / shared inflight; streaming replies  
