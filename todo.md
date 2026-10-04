# Workshop todos

## Questions

1. **Level-pass feedback** — When a level is cleared, should we show “level passed” briefly (e.g. banner that fades) or keep it visible permanently on the next level (e.g. progress bar + collected flags list)?
2. **Scoring model** — **Locked: collaborative** — work through challenges together; no competitive points in pilot. Notes still capture flag, root cause, business impact, remediation.
   - **Possible expansion later:** simple 10 pts/level or multi-criteria 30-pt scoring.
3. **Escalating hints** — Extra hint after **2** failed attempts on the current level; another at **4**. (Was 3 / 6.)
4. **Assistant branding (AIDA)** — Pick a name direction before any rename:
   1. Keep AIDA (soften mission copy only)
   2. Generic role (“ops assistant” / “internal chatbot”)
   3. Company-tied rename under Celtic Services Group
   4. Facilitator-supplied name

   **Context:** AIDA is from the classic workshop (system prompt, UI, repo `workshop-aida-app`), not the worf pilot. Workshop title stays **Break the AI App**; AIDA is the in-fiction bot name. Full brief: `docs/people_design.md` → “Branding: where AIDA came from”.  
   **Locked choice:** _(none yet — no UI/prompt changes until locked)_

### Breadcrumbs (Level 2 — goal hijack)

Participants should learn that chatbots have a **scope/remit** and that off-topic asks can succeed if framed well — but we should not print exact jailbreak strings in the UI.

Suggested tiers:

| When | What to tell them |
|------|-------------------|
| Always | Off-mission output (recipe, poem, story) = pass; a refusal = fail. |
| After 2 fails | Direct overrides and fake authority often fail; try indirect framing (training scenario, sample format, security-awareness content). |
| After 4 fails | Scope abuse angle: what sounds *almost* work-related but still pulls AIDA off remit? |

**Implemented (pilot):** escalating hints in the Challenge path panel — review wording after a live run.

### Preference (for now)

**Scoring:** Collaborative — challenge by challenge, no points in pilot UI. Notes for learning.

## Todos

- [x] Decide level-pass UX (brief vs permanent) — green clear banner also appears in chat
- [x] Scoring → collaborative (no login, no points bar in pilot)
- [x] Pilot: no participant login; stale alice session cleared on home page
- [x] Worf model → `unsloth/Qwen3.8-27B-NVFP4` (was Qwen3.6-35B)
- [x] Log chat attempts (`chat_attempts` table); replay via `GET /api/chat-attempts` as **admin** after `/login`
- [ ] Review escalating-hint wording on Level 2 after a live workshop run
- [x] Session Activity card shows attempts + hints (replaces What AIDA accessed UI)
- [x] Pilot Level 3 PII + Level 4 poisoned case load
- [x] Pilot Level 5 Employee Access (BOLA)
- [x] Pilot Level 6 encoded sneak-out (filter bypass; submit secret to pass)
- [x] Document AIDA branding origin + name options (people_design + todo); rename deferred until choice locked
- [ ] After branding choice locked: update mission/UI/prompts (index.html, app.js, main.py) — see people_design touch list
- [ ] Define six pilot levels we are happy with — map each to [OWASP LLM Top 10 2026 one-pager](docs/OWASP-LLM-Top-10-2026-one-pager.md) (full PDF: `docs/OWASP-GenAI-LLM-Top-10-2026-v1.0.pdf`)
