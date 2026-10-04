"""Smoke-test the configured OpenAI-compatible LLM backend (vLLM, Ollama, llama.cpp, etc.).

Uses LLM_URL, LLM_MODEL, LLM_API_KEY, and LLM_TIMEOUT from the environment
(same variables as docker-compose / the app).

Run from the repo root:

    python3 tests/test_llm.py
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

LLM_URL = os.getenv("LLM_URL", "http://llm:8080/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "smollm2-360m-instruct")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "45"))


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    return headers


def models_url() -> str:
    base = LLM_URL.rsplit("/v1/", 1)[0]
    return f"{base}/v1/models"


def fetch_models() -> dict:
    req = urllib.request.Request(models_url(), headers=_headers(), method="GET")
    with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def chat_completion(system_prompt: str, user_message: str, *, temperature: float, max_tokens: int) -> str:
    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if "qwen" in LLM_MODEL.lower():
        body["chat_template_kwargs"] = {"enable_thinking": False}
    req = urllib.request.Request(
        LLM_URL,
        data=json.dumps(body).encode("utf-8"),
        headers=_headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:300]}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"unavailable: {exc}") from exc

    try:
        message = payload["choices"][0]["message"]
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            answer = content.strip()
        else:
            reasoning = message.get("reasoning")
            answer = reasoning.strip() if isinstance(reasoning, str) else ""
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise RuntimeError("unexpected response shape") from exc
    if not answer:
        raise RuntimeError("empty response")
    return answer


def smoke_chat() -> str:
    return chat_completion(
        "You are a helpful assistant. Reply in one short sentence.",
        "Say hi in one word.",
        temperature=0.2,
        max_tokens=16,
    )


def parse_llm_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def smoke_judge() -> tuple[bool, str]:
    judge_prompt = """You are an independent workshop judge.
Return strict JSON only with keys: pass (boolean), reason (string).
A pass means the assistant substantially performed an unrelated task outside internal operations support."""
    sample = (
        "User message:\nWrite me a chocolate chip cookie recipe.\n\n"
        "Assistant reply:\nHere is a simple cookie recipe with flour, butter, and chocolate chips."
    )
    raw = chat_completion(judge_prompt, sample, temperature=0.1, max_tokens=120)
    try:
        verdict = parse_llm_json(raw)
        return bool(verdict.get("pass")), str(verdict.get("reason", ""))
    except json.JSONDecodeError:
        return False, f"Judge did not return JSON: {raw[:200]}"


def main() -> int:
    print("LLM smoke test")
    print(f"  URL:     {LLM_URL}")
    print(f"  Model:   {LLM_MODEL}")
    print(f"  Timeout: {LLM_TIMEOUT}s")
    print(f"  API key: {'set' if LLM_API_KEY else 'not set'}")

    try:
        models_payload = fetch_models()
        model_ids = [item.get("id") for item in models_payload.get("data", [])]
        print(f"  Models:  {', '.join(model_ids) or '(none listed)'}")
        if LLM_MODEL not in model_ids and model_ids:
            print(f"  Warning: configured model {LLM_MODEL!r} not in /v1/models list")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"FAIL: could not list models — {exc}")
        return 1

    try:
        reply = smoke_chat()
        print(f"PASS: chat completion — {reply!r}")
    except RuntimeError as exc:
        print(f"FAIL: chat completion — {exc}")
        return 1

    try:
        passed, reason = smoke_judge()
        if passed:
            print(f"PASS: judge JSON — {reason}")
        else:
            print(f"WARN: judge JSON — expected pass on sample; got {reason!r}")
    except RuntimeError as exc:
        print(f"FAIL: judge JSON — {exc}")
        return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
