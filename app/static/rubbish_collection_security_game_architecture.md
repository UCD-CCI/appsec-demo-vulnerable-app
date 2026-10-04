# Rubbish Collection Security Game — Architecture

## Purpose

The game presents participants with a realistic rubbish collection chatbot and asks them to discover security weaknesses across a series of levels.

The chatbot should still behave like a normal service assistant: it can answer questions about bin collections, charges, bin types, missed collections, and replacement bins. The security challenge sits around this chatbot rather than replacing its normal function.

## Core Components

### 1. Target Rubbish Collection Chatbot

This is the user-facing chatbot.

It:

- Answers genuine waste collection questions.
- Receives a level-specific system prompt.
- May later access simulated customer records or call fake tools.
- Does not know the level pass condition, hints, or scoring rules.
- May contain an intentional weakness for a particular lesson.

### 2. In-World Security Reviewer

Some later levels include a second model that reviews a proposed response or tool call before it is allowed.

This reviewer is part of the system being tested and may itself be weak.

For example, a bad reviewer might block the exact protected word `SECRET` but fail to recognise its ROT13 representation, `FRPERG`.

A later repaired level can replace it with a stronger reviewer or deterministic policy controls.

### 3. Independent Game Judge

The game judge is hidden from the participant, target chatbot, and in-world reviewer.

It decides whether the player completed the challenge.

It should judge what actually happened, not merely whether the user entered a plausible attack.

Examples:

- Did the chatbot substantially perform an unrelated task?
- Did protected information appear in an encoded form?
- Was another customer's record accessed?
- Was a prohibited simulated tool called?
- Was a required confirmation bypassed?

Use deterministic checks where possible and an evaluator model only where interpretation is necessary.

### 4. Game Controller

The game controller is ordinary application code.

It:

- Loads the current level.
- Sends messages to the target chatbot.
- Invokes the in-world reviewer when the level uses one.
- Executes permitted simulated tools.
- Sends evidence to the independent judge.
- Tracks attempts, hints, score, completion, and progression.
- Stores transcripts, tool events, and evaluator decisions.

Models should not directly control scoring, permissions, or level progression.

### 5. Simulated Data and Tools

Later levels can provide fake customer records and safe, disposable tools such as:

- `get_my_account`
- `report_missed_collection`
- `request_replacement_bin`
- `change_collection_address`
- `cancel_account`
- `delete_test_database`

All data and actions should be fictional and isolated from real systems.

### 6. User Interface

A minimalist interface should contain:

- The chat window.
- Current level and public objective.
- Attempts and score.
- Hint and reset controls.
- A level-completion notice.
- An explanation shown after completion.

The chatbot should remain in character. Hints, scoring, and completion messages should come from the game interface, not from the rubbish collection bot.

## Information Provenance

The system should record where sensitive information came from and how it moved through the system.

Example:

```json
{
  "source": "customer_record.recovery_phrase",
  "classification": "protected",
  "value": "SECRET",
  "target_output": "FRPERG",
  "reviewer_decision": "allow"
}
```

This allows the game judge to identify a successful disclosure even when the protected value has been transformed, split, encoded, translated, or indirectly described.

A practical detection pipeline is:

1. Exact protected-value matching.
2. Normalisation and common decoding.
3. Tool-call and record-access evidence.
4. Provenance checks.
5. LLM semantic evaluation for ambiguous cases.

## Message Flow

```text
Player
  |
  v
Game Controller
  |
  v
Target Rubbish Collection Chatbot
  |
  | proposed response or tool call
  v
Optional In-World Security Reviewer
  |
  | allow or block
  v
Simulated Tool / User-Visible Response
  |
  v
Independent Game Judge
  |
  v
Score, completion state, hints, and level progression
```

## Initial Level Progression

A useful progression is:

1. **Goal Hijack** — persuade the chatbot to perform an unrelated task.
2. **Internal Information Disclosure** — extract hidden fictional instructions or markers.
3. **Customer Data Access** — obtain another fictional customer's information.
4. **Unsafe Action** — trigger an unauthorised simulated tool.
5. **Reviewer Bypass** — evade a weak second-model reviewer using encoding or indirection.
6. **Remediated Version** — repeat the challenge against stronger controls.

## Minimum Viable Version

The first spike only needs:

- One target chatbot.
- One goal-hijack level.
- One independent evaluator.
- Three fixed hints.
- A simple game controller.
- A small SQLite or in-memory state store.
- A chat UI with objective, attempts, score, hint, reset, and completion state.

The central principle is:

> The target chatbot and in-world reviewer are part of the system being attacked. The independent judge and game controller sit outside that system and measure what actually happened.
