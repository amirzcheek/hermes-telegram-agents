---
name: evidence-brief
description: Layout and checklist for a short, source-backed research brief. Load when answering a [TASK ...-R] research task.
version: 1.0.0
---

# Evidence brief

## Procedure

1. Turn the Goal into 2 or 3 search queries: one broad, one with the exact
   technical term, one with "paper" or "arXiv" added.
2. For each promising result, open the page and confirm the claim is really
   there. A search snippet alone is not a source.
3. Keep 2 to 4 findings. Each finding is one sentence plus one URL.
4. Prefer, in this order: the original paper, official documentation, a
   survey, a well-known textbook. Avoid forum answers and SEO blogs.
5. If two sources disagree, report both and say so in Summary.

## Checklist before sending

- Every URL was returned by a tool call in this task.
- No finding without a URL.
- Paper titles, author names and years are copied from the page, not recalled.
- Total length under 3000 characters.
- Confidence is "low" when fewer than two independent sources agree.
