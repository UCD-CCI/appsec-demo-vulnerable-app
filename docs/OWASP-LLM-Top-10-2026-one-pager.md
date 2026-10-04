# OWASP GenAI LLM Top 10 (2026) — workshop one-pager

**Full guide (122 pp):** [`OWASP-GenAI-LLM-Top-10-2026-v1.0.pdf`](OWASP-GenAI-LLM-Top-10-2026-v1.0.pdf)  
**Project page:** [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) · [genai.owasp.org](https://genai.owasp.org/)  
**License:** CC BY-SA 4.0 (summaries below are abbreviated; cite OWASP when sharing)

Use this page in the workshop. Use the PDF for depth, mitigations, and facilitator prep.

---

## The ten (2026)

| # | Risk | One-line summary |
|---|------|------------------|
| **LLM01** | Prompt Injection | Untrusted input (chat, RAG, tools, media, memory) changes model behaviour away from what the app intended. |
| **LLM02** | Sensitive Information Disclosure | The system exposes confidential or regulated data through a channel that should not reveal it. |
| **LLM03** | Excessive Agency | The app gives the model tools or autonomy to act on other systems without enough limits or approval. |
| **LLM04** | Supply Chain | Compromised models, adapters, pipelines, or platforms undermine integrity of what you deploy. |
| **LLM05** | Data and Model Poisoning | Adversarial or bad training/fine-tuning data embeds bias, backdoors, or unsafe behaviour. |
| **LLM06** | Unbounded Consumption | Uncontrolled inference load causes cost blowout, DoS, or resource abuse. |
| **LLM07** | Misinformation | Plausible-but-wrong model output drives bad human or automated decisions. |
| **LLM08** | Hidden Context Exposure | Attackers extract hidden system instructions, policy logic, tools, or secrets from context. |
| **LLM09** | Vector and Embedding Weaknesses | RAG / similarity search lets attackers steer what the model “sees”. |
| **LLM10** | Improper Output Handling | Downstream code trusts LLM output without validation (e.g. unsafe generated code). |

**Note:** 2026 renames and rescopes several 2023 items (e.g. “system prompt leakage” → **LLM08 Hidden Context Exposure**). Agentic/tool-heavy risks also overlap [OWASP Agentic Top 10](https://genai.owasp.org/) — pair both when the model *acts*, not just chats.

---

## Map to our workshop challenges

### Pilot (natural LLM — live now)

| Level | Workshop challenge | Primary OWASP 2026 |
|-------|-------------------|-------------------|
| 1 | Hidden instructions | **LLM08** Hidden Context Exposure · **LLM02** Sensitive Information Disclosure |
| 2 | Goal Hijack | **LLM01** Prompt Injection (direct / scope abuse) |
| 3 | Support ticket PII | **LLM02** Sensitive Information Disclosure |
| 4 | Poisoned case load | **LLM01** Prompt Injection (indirect / pasted content) |
| 5 | Employee Access | **LLM02** · classic API BOLA |
| 6 | Encoded sneak-out | **LLM01** / output-filter bypass |

Facilitator walkthrough: [FACILITATOR_GUIDE.md](FACILITATOR_GUIDE.md) (pilot section first).

### Classic (six challenges, keyword/API path)

| # | Challenge | Primary OWASP 2026 |
|---|-----------|-------------------|
| 1 | Hidden instructions | **LLM08** · **LLM02** |
| 2 | Tool discovery | **LLM03** Excessive Agency (attack surface) · **LLM01** (enumeration via chat) |
| 3 | Tickets 101/313 | **LLM01** Prompt Injection (indirect / retrieved content) |
| 4 | Employee Access | **LLM03** + classic API BOLA (outside pure LLM list) |
| 5 | Password reset | **LLM03** Excessive Agency · broken function authorization |
| 6 | Supplier 77 | **LLM03** Excessive Agency |

### Architecture sketch (six LLM-native levels, not all built)

| # | Planned level | Primary OWASP 2026 |
|---|---------------|-------------------|
| 1 | Goal Hijack | **LLM01** |
| 2 | Internal disclosure | **LLM08** · **LLM02** |
| 3 | Customer data access | **LLM02** · **LLM03** |
| 4 | Unsafe action | **LLM03** |
| 5 | Reviewer bypass | **LLM01** · **LLM08** |
| 6 | Remediated replay | Controls across **LLM01–03** |

---

## What we are *not* covering yet

- **LLM04** Supply Chain, **LLM05** Poisoning, **LLM06** Unbounded Consumption, **LLM07** Misinformation, **LLM09** Vector weaknesses, **LLM10** Improper output handling — good candidates for future levels or debrief-only topics.
