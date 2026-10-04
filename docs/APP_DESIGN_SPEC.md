# Break the AI App — Recreation Specification

## Objective

Recreate a single-user, localhost-only AI security workshop application with the same dark blue visual design, two-column participant layout, six challenges, live tool logs, CPU-only local LLM fallback and Markdown notes workspace.

## Visual design

- Dark navy radial-gradient page background.
- Translucent navy cards with subtle borders, rounded 16px corners and soft shadows.
- Cyan eyebrow labels and primary actions.
- Main header with three zones:
  - **Left:** UCD CCI logo (`ucd-logo.svg`).
  - **Centre:** "NCSC Cyber Week workshop" eyebrow text and large `Break the AI App` title.
  - **Right:** Vulnerable/hardened mode badge (text only, no logo).
- Note: `aida_logo.png` is present in `app/static/` but is not currently referenced in any template.
- Desktop layout: main content approximately two-thirds width; challenge sidebar approximately one-third.
- Mobile layout collapses to one column.

## Main page structure

1. Header with NCSC logo, title and vulnerable/hardened mode badge.
2. Login card when unauthenticated.
3. Session bar when authenticated.
4. Left column:
   - AIDA chat card
   - AI tool-call log card
5. Right column:
   - mission card
   - challenge path card with Notes link opening a new tab
   - scoring card

Do not advertise `/docs` in the mission or navigation.

## Challenge order and labels

1. Hidden instructions
2. Tool discovery
3. Tickets 101 or 313
4. Employee Access
5. Password reset
6. Supplier 77

## Application stack

- Python 3.12
- FastAPI and Jinja2 templates
- SQLite
- Vanilla JavaScript and CSS
- Docker Compose
- llama.cpp server running a quantised SmolLM2-360M-Instruct GGUF model

## Chat routing

Process recognised workshop inputs before calling the LLM:

- Prompt-disclosure phrases return the vulnerable system prompt.
- Tool-discovery phrases return the tool schema and challenge flag.
- Regex `ticket\s+(\d+)` extracts a ticket number and performs a parameterised SQL lookup.
- Regex `employee\s+(\d+)` extracts an employee number and performs a parameterised SQL lookup.
- Password-reset and supplier phrases expose the relevant POST route.
- All unrecognised prompts are sent to the local LLM. Do not replace a successful LLM response with a canned hint.

## Ticket behaviour

All ticket numbers must be searchable. Seed at least tickets 101, 202 and 313.

- Ticket 101 includes a plausible embedded workflow instruction to retrieve expense 9001.
- Ticket 313 includes a plausible embedded workflow instruction to retrieve expense 9007.
- In vulnerable mode, use `TICKET_EXPENSE_MAP = {101: 9001, 313: 9007}` and retrieve the expense.
- In hardened mode, return the ticket but refuse to treat embedded content as an instruction.
- Expenses 9001 and 9007 contain `FLAG{RETRIEVED_CONTENT_BY_UNTRUSTED}` and a clue pointing to employee 1042.

## Flags

- `FLAG{SYSTEM_PROMPT_IS_NOT_A_SECRET}`
- `FLAG{TOOLS_ARE_ATTACK_SURFACE}`
- `FLAG{RETRIEVED_CONTENT_BY_UNTRUSTED}`
- `FLAG{BOLA_EXPOSED_ANOTHER_USER}`
- `FLAG{FUNCTION_LEVEL_AUTH_MATTERS}`
- `FLAG{AGENTS_NEED_LIMITED_AUTHORITY}`

## Notes page

Route: `/workshop_notes`; authentication required.

- Same visual design and NCSC header as main page.
- Six sections matching the challenge order.
- Four editable text areas per challenge: FLAG, Root cause, Business impact and Remediation.
- Autosave to browser local storage.
- `Save Markdown` uses the File System Access API when supported and otherwise downloads `break-ai-app-workshop-notes.md`.
- Include a link back to the workshop.

## Security modes

Vulnerable mode deliberately permits prompt disclosure, tool enumeration, indirect prompt injection, arbitrary employee access, non-admin password resets and supplier approval.

Hardened mode must enforce object/function authorization, reject embedded instructions and require appropriate approval.
