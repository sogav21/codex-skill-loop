---
name: loop
description: Codex-optimized iterative workflow for /loop and $loop with goal-based execution, verifiable evidence, and explicit keep/revert logic.
---

# Loop

## Trigger

- `/loop`
- `$loop`
- user asks to keep working until verified, optimize, improve, iterate, or run research

## Mode selection

- Completion mode: binary success (pass/fail, exists/missing, fixed/broken, valid/invalid).
- Research mode: metric-based success (improve/worsen, faster/slower, higher/lower score).
- If ambiguous, choose the mode that gives the clearest measurable success check.
- If user gives explicit `N rounds`, treat it as hard attempt budget; otherwise loop by objective.

## Codex goal contract (required)

Before first edit, write a compact goal card:

- objective
- measurable goal (pass/fail or metric + direction)
- hypothesis queue / action order (1 action per iteration)
- success rule (the exact condition for done)
- stop rule (why you will stop)
- verification command(s)
- evidence required (commands, tests, files, screenshots, benchmark output)
- scope and constraints
- keep/revert rule
- budget handling (explicit count or no budget)

Use this as a running goal object through all iterations.

## Shared 1-loop cycle (both modes)

Each iteration is one cycle:

1. Load state and choose next hypothesis/action.
2. Make one minimal change only.
3. Run the planned verification command(s).
4. Record attempt evidence immediately.
5. Update `loop_project/state.json` counters.
6. Decide: `keep`, `revert`, or `retry`.
7. Continue to next cycle if stop rule not met.

Decision classes:

- `pass` = verified success criteria for the mode
- `keep` = useful progress, not yet finished
- `revert` = harmful or out-of-scope, revert immediately
- `inconclusive` = no reliable evidence or too little signal
- `blocked` = external/tool/permission/risk prevents safe progress

Rules:

- Never claim success without evidence.
- Never repeat the same failed action unchanged.
- Do not send progress-only turns when task not finished.
- Always use deterministic command/output evidence where possible.
- If interrupted, resume from last saved state and continue loop.

## Completion vs Research (same core, different checks)

- Completion mode target check: `done` vs `not done`.
- Research mode target check: metric movement to target + minimum meaningful delta.
- Shared workflow and logging remain identical.

## Workspace contract

Create/ensure:

- `loop_project/state.json`
- `loop_project/attempts.jsonl`
- `loop_project/metrics.jsonl`
- `loop_project/diff.patch`
- `loop_project/README.md`

If `git` is not available for rollback, use deterministic snapshots (`.bak`) before risky edits.

## Codex execution abilities (required)

Prefer these tools in this order:

- `rg` for fast discovery
- `Get-Content` / file read for quick checks
- `git diff` for change diff
- `apply_patch` for deterministic edits
- `attempts/state/metrics` jsonl updates as compact logs

Use the lightest command set that still produces verifiable evidence.

## Logging format

Attempt entry (one line json):

- `{"attempt":1,"mode":"completion|research","hypothesis":"...","action":"...","result":"pass|keep|revert|inconclusive|blocked","metric_before":12,"metric_after":14,"delta":2,"changed_files":["..."],"verification_cmd":"...","verification":"...","decision":"...","failure_reason":"","lesson":"...","next_adjustment":"...","rollback_ok":true}`

Metric entry (one line json):

- `{"attempt":1,"metric_name":"loop_score","value_before":12,"value_after":14,"delta":2,"direction":"higher|lower","unit":"count","notes":"...","verification":"...","rollback_ok":true}`

State file:

- include `attempt`, `kept`, `reverted`, `inconclusive`, `baseline_metric`, `best_metric`, `last_action_files`.

## Diff and rollback

Before risky edits, record baseline (`git diff` or snapshot).
For each kept change, append to `loop_project/diff.patch`.
If a kept change is reverted, log revert action and set `rollback_ok=true` only after verification.

## Final response format

When stopping, return only:

- selected mode
- final result
- verification evidence
- iteration count
- completion/research stats: kept/reverted/inconclusive
- Research: baseline -> final metric, delta, percent (if meaningful)
- reason for stop (target reached, budget reached, blocker, or no useful hypothesis)
