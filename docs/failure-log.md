# Failure log

Real requests where the system failed. One entry per failure, written right
after it happened. Copy the messages from the group and the relevant lines from
`~/.hermes/profiles/<agent>/logs/gateway.log`.

## Template

### F<n>: <short name>

- **Date:**
- **Request:** (exact text sent to the coordinator)
- **Expected:** (which messages should have appeared)
- **Observed:** (what appeared instead; where the chain stopped)
- **Evidence:** (log lines, message screenshots)
- **Cause:** (Telegram delivery / gateway gate / prompt / model / rate limit)
- **Fix applied or proposed:**
- **Still open:**

## Observed

### F1: final answer exceeded the length limit and was split

- **Date:** 2026-10-03
- **Request:** "Does Adam really converge faster than SGD with momentum on an
  ill-conditioned quadratic? Check what the papers say and show it numerically."
- **Expected:** one `[FINAL T614]` message under 3500 characters.
- **Observed:** the chain completed (TASK-R, RESULT-R, TASK-C, RESULT-C, FINAL),
  but the final answer was longer than Telegram's 4096-character limit and
  arrived as two messages marked (1/2) and (2/2).
- **Cause:** prompt and model. The coordinator restated every setting and every
  number from the Coder's output. The length rule in `SOUL.md` is only an
  instruction; nothing in the gateway enforces it.
- **Why it matters:** harmless for a final answer, which carries no mention.
  The same overflow in a specialist's RESULT would deliver only the first part
  to the coordinator, because the mention is in the first part only.
- **Fix applied:** limit lowered to 3000 characters and "at most six key
  numbers, do not repeat the full output" added to the coordinator's rules.
- **Still open:** no hard enforcement. A real fix is a length check in code
  (a gateway hook) or passing long results as a file.

### F2: LaTeX shown as raw text

- **Date:** 2026-10-03
- **Request:** same run as F1; also `explain dropout in 3 lines` to the Study Buddy.
- **Expected:** readable formulas.
- **Observed:** formulas appeared as raw LaTeX source with backslashes and
  brackets, in the Researcher's report, the final answer and the Study
  Buddy's reply.
- **Cause:** the model writes LaTeX by default; Telegram does not render it.
- **Fix applied:** "plain text math, no LaTeX" rule added to all four `SOUL.md`.
- **Still open:** complex formulas are hard to read as plain text.

### F3: part of a formula missing in the Researcher's brief

- **Date:** 2026-10-03
- **Request:** "Explain why Adam needs bias correction, back it with the
  original paper, and give me two practice questions."
- **Expected:** `E[v_t] = E[g_t^2] * (1 - beta_2^t) + zeta` in the brief.
- **Observed:** the message showed "E[v_t] = Eg_t^2 + zeta": the brackets and
  the factor (1 - beta_2^t) were gone.
- **Cause:** likely formatting. Plain-text math written as `[..](..)` has the
  shape of a Markdown link, so Telegram shows only the bracketed text.
- **Impact:** none this time; the coordinator did not pass that line on. A
  formula copied into Context could reach the final answer corrupted, and
  nobody in the chain would notice.
- **Fix proposed:** require every formula to be wrapped in backticks.
- **Still open:** not applied.

### F4: the Researcher did part of the Study Buddy's job

- **Date:** 2026-10-03
- **Request:** same run as F3.
- **Expected:** the Researcher returns findings and sources only; practice
  questions come from the Study Buddy.
- **Observed:** the Researcher's Summary contained two practice questions of
  its own.
- **Cause:** prompt. The coordinator copied the whole human request into
  Context ("...and two practice questions"), so the Researcher saw work that
  belonged to another step. Its `SOUL.md` forbids writing code but says
  nothing about teaching content.
- **Impact:** none on the final answer; the coordinator used the Study Buddy's
  questions. It shows that role boundaries depend on what the coordinator
  writes into Context, not only on each specialist's own rules.
- **Fix proposed:** coordinator rule "Context holds only what this specialist
  needs; do not restate the other steps of the plan".
- **Still open:** not applied.

## Not tested yet

Probes for known weak points of the design that we have not run.

| Probe | What it tests | Likely outcome |
| --- | --- | --- |
| Ask for "a detailed survey with 10 sources" | 4096-character split of the Researcher's report | Coordinator receives a truncated RESULT |
| Send two different requests 10 seconds apart | Shared coordinator session, task ids | Results attached to the wrong request |
| Ask for a script that needs pandas or the network | Coder restrictions | FAILED, one retry, final answer with Limits |
| Ask about a made-up paper title | Researcher honesty | Either FAILED or an invented link |
| Stop the Coder's gateway, then send a RESEARCH then CODE request | Missing timeout | Coordinator waits forever after the handoff |
| Ask the Study Buddy directly about a paper from the last few months | No web access, honesty rule | Either "not sure, ask the Coordinator" or an invented summary |
| Answer a quiz question by plain message instead of a reply | Mention gate in direct tutoring | Study Buddy stays silent; the quiz stalls |
| Run requests until the provider's usage limit is hit | Rate-limit behaviour mid-chain | Chain stops silently at some agent |
