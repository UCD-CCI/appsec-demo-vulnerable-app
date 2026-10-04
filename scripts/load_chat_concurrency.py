#!/usr/bin/env python3
"""Ramp concurrent workshop chats to find the LLM/app cliff.

Each worker:
  1. GET / (session cookie)
  2. GET /testing/1 (jump to Level 1 — uses the LLM)
  3. Wait at a barrier so all chats fire together
  4. POST /api/chat with a short message

Reports setup_s (pages), chat_s (POST only), and total_s separately.

Example:
  python3 scripts/load_chat_concurrency.py --base-url http://127.0.0.1:8167 --concurrency 10
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.cookiejar import CookieJar


def build_opener(
    base_url: str,
    basic_user: str | None = None,
    basic_password: str | None = None,
) -> urllib.request.OpenerDirector:
    jar = CookieJar()
    handlers: list[urllib.request.BaseHandler] = [urllib.request.HTTPCookieProcessor(jar)]
    if basic_user is not None:
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, base_url.rstrip("/"), basic_user, basic_password or "")
        handlers.append(urllib.request.HTTPBasicAuthHandler(password_mgr))
    return urllib.request.build_opener(*handlers)


def request_json(
    opener: urllib.request.OpenerDirector,
    method: str,
    url: str,
    payload: dict | None = None,
    timeout: float = 180.0,
) -> tuple[int, str, float]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body, time.perf_counter() - started
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body, time.perf_counter() - started


def one_user(
    base_url: str,
    message: str,
    timeout: float,
    basic_user: str | None,
    basic_password: str | None,
    barrier: threading.Barrier,
) -> dict:
    opener = build_opener(base_url, basic_user, basic_password)
    base = base_url.rstrip("/")
    t0 = time.perf_counter()
    try:
        status, _, home_s = request_json(opener, "GET", f"{base}/", timeout=30)
        if status >= 400:
            try:
                barrier.abort()
            except Exception:  # noqa: BLE001
                pass
            return {
                "ok": False,
                "error": f"GET / -> {status}",
                "total_s": time.perf_counter() - t0,
                "setup_s": time.perf_counter() - t0,
            }

        status, _, testing_s = request_json(opener, "GET", f"{base}/testing/1", timeout=30)
        # /testing/1 redirects to /challenge; urllib follows by default.
        if status >= 400:
            try:
                barrier.abort()
            except Exception:  # noqa: BLE001
                pass
            return {
                "ok": False,
                "error": f"GET /testing/1 -> {status}",
                "total_s": time.perf_counter() - t0,
                "setup_s": time.perf_counter() - t0,
            }

        setup_s = home_s + testing_s

        # All workers finish page setup, then fire chats together.
        try:
            barrier.wait(timeout=120)
        except threading.BrokenBarrierError:
            return {
                "ok": False,
                "error": "setup barrier broken (another worker failed setup)",
                "total_s": time.perf_counter() - t0,
                "setup_s": setup_s,
            }

        status, body, chat_s = request_json(
            opener,
            "POST",
            f"{base}/api/chat",
            payload={"message": message},
            timeout=timeout,
        )
        total_s = time.perf_counter() - t0
        if status != 200:
            return {
                "ok": False,
                "error": f"chat HTTP {status}: {body[:160]}",
                "total_s": total_s,
                "setup_s": setup_s,
                "chat_s": chat_s,
            }

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return {
                "ok": False,
                "error": f"non-JSON reply: {body[:160]}",
                "total_s": total_s,
                "setup_s": setup_s,
                "chat_s": chat_s,
            }

        reply = str(data.get("reply") or "")
        source = str(data.get("source") or "")
        busy = "too many people chatting" in reply.lower() or source == "capacity-limit"
        unavailable = "unavailable" in reply.lower() or source == "llm-error"
        ok = not busy and not unavailable and bool(reply.strip())
        return {
            "ok": ok,
            "busy": busy,
            "unavailable": unavailable,
            "total_s": total_s,
            "setup_s": setup_s,
            "chat_s": chat_s,
            "reply_preview": reply[:80].replace("\n", " "),
        }
    except Exception as exc:  # noqa: BLE001 — surface any worker failure
        try:
            barrier.abort()
        except Exception:  # noqa: BLE001
            pass
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "total_s": time.perf_counter() - t0,
        }


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    k = (len(ordered) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(ordered) - 1)
    if f == c:
        return ordered[f]
    return ordered[f] + (ordered[c] - ordered[f]) * (k - f)


def _print_latency(label: str, values: list[float]) -> None:
    if not values:
        return
    print(
        f"{label}: "
        f"min={min(values):.1f} "
        f"p50={percentile(values, 50):.1f} "
        f"p95={percentile(values, 95):.1f} "
        f"max={max(values):.1f} "
        f"mean={statistics.mean(values):.1f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8167")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=180.0, help="Per-request timeout seconds")
    parser.add_argument(
        "--basic-user",
        default=os.environ.get("CCI_DEMO_USER") or os.environ.get("BASIC_AUTH_USER"),
        help="HTTP Basic Auth username (or env CCI_DEMO_USER). Do not commit credentials.",
    )
    parser.add_argument(
        "--basic-password",
        default=os.environ.get("CCI_DEMO_PASSWORD") or os.environ.get("BASIC_AUTH_PASSWORD"),
        help="HTTP Basic Auth password (or env CCI_DEMO_PASSWORD). Do not commit credentials.",
    )
    parser.add_argument(
        "--message",
        default="In one short sentence, what is your name?",
    )
    args = parser.parse_args()

    print(f"base_url={args.base_url}")
    print(f"concurrency={args.concurrency}")
    print(f"timeout={args.timeout}s")
    print(f"basic_auth={'yes' if args.basic_user else 'no'}")
    print(f"barrier=yes (chats fire together after setup)")
    print(f"message={args.message!r}")
    print("---")

    barrier = threading.Barrier(args.concurrency)
    wall0 = time.perf_counter()
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [
            pool.submit(
                one_user,
                args.base_url,
                args.message,
                args.timeout,
                args.basic_user,
                args.basic_password,
                barrier,
            )
            for _ in range(args.concurrency)
        ]
        for fut in as_completed(futures):
            results.append(fut.result())
    wall = time.perf_counter() - wall0

    oks = [r for r in results if r.get("ok")]
    busy = [r for r in results if r.get("busy")]
    fails = [r for r in results if not r.get("ok")]
    chat_latencies = [float(r["chat_s"]) for r in results if "chat_s" in r]
    setup_latencies = [float(r["setup_s"]) for r in results if "setup_s" in r]
    total_latencies = [float(r["total_s"]) for r in results if "total_s" in r]

    print(f"wall_clock_s={wall:.1f}")
    print(f"ok={len(oks)} busy={len(busy)} fail={len(fails)}")
    _print_latency("setup_latency_s", setup_latencies)
    _print_latency("chat_latency_s", chat_latencies)
    _print_latency("total_latency_s", total_latencies)
    print("---")
    for i, r in enumerate(results, 1):
        if r.get("ok"):
            print(
                f"{i:02d} OK  setup={r.get('setup_s', 0):.1f}s "
                f"chat={r.get('chat_s', 0):.1f}s  {r.get('reply_preview', '')!r}"
            )
        elif r.get("busy"):
            print(
                f"{i:02d} BUSY setup={r.get('setup_s', 0):.1f}s "
                f"chat={r.get('chat_s', 0):.1f}s"
            )
        else:
            print(f"{i:02d} FAIL {r.get('error') or r}")

    # BUSY replies are expected when testing the cap; count them separately from hard fails.
    hard_fails = [r for r in fails if not r.get("busy")]
    return 0 if not hard_fails and (oks or busy) else 1


if __name__ == "__main__":
    raise SystemExit(main())
