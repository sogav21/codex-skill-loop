---
name: loop
description: Codex-optimized iterative workflow for /loop and $loop with goal-based execution, verifiable evidence, explicit keep/revert logic, and merge-after-pass handling.
---

# Loop

## Pre-loop intake

Start only when the request is concrete enough to run safely. If any of these
are missing and cannot be inferred cheaply, ask before the first iteration:

- exact target outcome or problem statement
- the file, subsystem, or surface to work on
- what counts as success or done
- whether the user wants completion mode or research mode
- any explicit attempt budget, deadline, or stop condition

Ask up to 3 focused questions. If the user already gave enough detail, skip
intake and restate the working objective in one sentence.

## Mode selection

- Completion mode: binary target such as fixed, passing, present, valid, or
  successful.
- Research mode: metric target such as faster, higher score, lower latency,
  better accuracy, higher recall/precision, lower drawdown, or optimized.
- If intent is mixed, choose the mode with the clearest verifiable end
  condition.
- Do not invent an attempt limit.
- If user gives explicit `N rounds`, treat it as a hard attempt budget.
- If no budget is given, keep looping until target is verified or a non-recoverable stop rule is hit.

Research mode reaches `pass` only when:

- the user-defined research objective is explicit enough to measure
- the target metric reached the requested direction or threshold
- the final result is reproducible from the recorded evidence

If the research target is not concrete, ask before editing instead of guessing.

## Goal card

Before the first edit, write a compact goal card:

- objective
- measurable success rule
- hypothesis queue with one action per iteration
- stop rules in priority order
- verification command(s)
- evidence required
- scope and constraints
- keep/revert rule
- attempt budget: explicit `N` or no fixed budget

Keep long-term memory out of the loop. Store task-local state in attempt logs,
scratch files, or `loop_project/` only.

Stop rules:

1. success verified
2. explicit budget exhausted
3. user-blocked external action required
4. repeated no-improvement attempts with no new hypothesis

## One-cycle loop

Each iteration does exactly one smallest useful action:

1. Load state and choose the next hypothesis.
2. Make one minimal change only.
3. Run the planned verification.
4. Record attempt evidence immediately.
5. Update counters.
6. Decide `pass`, `keep`, `revert`, `inconclusive`, or `blocked`.
7. Continue unless a stop rule fired.

Decision meanings:

- `pass` = verified success criteria for the mode
- `keep` = useful progress, not yet finished
- `revert` = harmful or out-of-scope, revert immediately
- `inconclusive` = no reliable evidence or too little signal
- `blocked` = external/tool/permission/risk prevents safe progress

Never repeat the same failed action unchanged. Retry an inconclusive/blocked
attempt only with a changed strategy; after 2 consecutive repeats with no new
evidence, stop as blocked.

## State and evidence

For risky, multi-file, or long-running work, create:

- `loop_project/state.json`
- `loop_project/attempts.jsonl`
- `loop_project/metrics.jsonl`
- `loop_project/diff.patch`
- `loop_project/README.md`

Attempt entry:

- `{"attempt":1,"mode":"completion|research","hypothesis":"...","action":"...","result":"pass|keep|revert|inconclusive|blocked","metric_before":12,"metric_after":14,"delta":2,"changed_files":["..."],"verification_cmd":"...","verification":"...","decision":"...","failure_reason":"","lesson":"...","next_adjustment":"...","rollback_ok":true}`

Metric entry:

- `{"attempt":1,"metric_name":"loop_score","value_before":12,"value_after":14,"delta":2,"direction":"higher|lower","unit":"count","notes":"...","verification":"...","rollback_ok":true}`

State file includes `attempt`, `kept`, `reverted`, `inconclusive`,
`baseline_metric`, `best_metric`, and `last_action_files`.

For simple one-pass work, a concise in-chat goal plus command evidence is
enough. For loops, persist state every iteration.

## Tools

Prefer:

- `rg` for discovery
- file reads for quick checks
- `git diff` for baseline and review
- `apply_patch` for deterministic edits
- the lightest verification command that proves the target

Before risky edits, record baseline with `git diff` or a deterministic
snapshot. If `git` is unavailable, create explicit backups before editing.
Append kept changes to `loop_project/diff.patch` when using persistent loop
state.

## Final response

When stopping, report:

- selected mode
- final result
- verification evidence
- iteration count
- kept/reverted/inconclusive counts
- research baseline -> final metric, delta, and percent when meaningful
- reason for stop (target reached, budget reached, blocker, or no useful hypothesis)
- `attempt_limit`: `explicit <N>` or `none`
- `stopped_for`: `success|budget|blocked|hypothesis_stagnation`

## GitHub merge on pass

If the user asked to merge on success:

- merge only after verified `pass`
- stage only the minimal intended change set
- use the workspace GitHub workflow or repository script
- report merge target, commit/PR, and verification evidence
