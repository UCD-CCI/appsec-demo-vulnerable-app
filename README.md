# AppSec Demo — Vulnerable App

**⚠️ INTENTIONALLY VULNERABLE — for education and demos only. Do not deploy to the public internet or use with real data.**

Demo target for [UCD-CCI/check-code-skill](https://github.com/UCD-CCI/check-code-skill): a small ops-assistant style app with classic code bugs and LLM trust-boundary issues so an agent skill can find them.

Derived from a UCD workshop “Break the AI App” codebase, with extra educational sinks added for talks.

## Planted / demo issues (non-exhaustive)

Marked `NOT SAFE` / `DEMO ONLY` in code where added for teaching:

| Issue | Where |
|-------|--------|
| SQL injection | `GET /api/employees/search?q=` |
| `eval()` on user input | `POST /api/expenses/evaluate-formula` |
| Path traversal | `GET /api/exports/download?file=` |
| Weak RNG reset token | `issue_reset_token` / `POST /api/auth/request-reset` |
| Insecure default API key | `LLM_API_KEY` default `CSG-ORBIT-EXFIL-9` |
| LLM: secret in prompt + output filter | Level 6 / exfil path in `app/main.py` |

The workshop also includes deliberate vulnerable/hardened challenge modes (BOLA, tool agency, prompt injection). Those are teaching surfaces, not production patterns.

## Pair with the skill

```text
Load the Check Code skill from UCD-CCI/check-code-skill,
then analyze all source files under this repository for security vulnerabilities.
```

## Run locally (optional)

```bash
cp .env.example .env
python scripts/seed.py
# optional model: python scripts/download_model.py
docker compose up --build
```

Open `http://127.0.0.1:8080`. Workshop credentials in docs are for the training UX only.

## License / use

Use for classroom demos and secure-code-review practice. Treat every secret and password in this tree as public demo material.
