---
name: run-experiment
description: Procedure for writing, running and reporting a tiny reproducible Python experiment. Load when answering a [TASK ...-C] coding task.
version: 1.0.0
---

# Run a tiny experiment

## Procedure

1. Restate the Goal as one measurable question, for example "after 200 steps,
   which optimiser has the lower loss on f(x, y) = x^2 + 10 y^2?".
2. Write the script:
   - `import numpy as np` and `np.random.seed(0)` at the top;
   - no input(), no plots, no files other than the script itself;
   - print a small labelled table, one line per condition.
3. Run `python <file>.py` with the terminal tool.
4. Read the tool result. If there is a traceback, fix the exact line it
   names and rerun. Stop after 3 attempts.
5. Copy stdout into Output exactly as printed.

## Checklist before sending

- The script in the report is the version that produced the output.
- Output has at most 15 lines; if longer, print less and rerun.
- Notes say what was assumed (learning rate, number of steps, seed).
- No claim in Notes goes beyond what the numbers show.
