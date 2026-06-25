---
name: loop
description: Auto-iterate `/loop` and `$loop` tasks with verified completion/research loops, compact logging, and explicit stop conditions.
---

# Loop

## Mode selection

1. Use **Completion Loop** for binary outcomes:
   - fixed/not fixed
   - tests pass/fail
   - file exists/missing
   - UI correct/incorrect
2. Use **Research Loop** when success is baseline+metric:
   - better/worse, faster/slower, higher/lower score
   - optimize, improve, benchmark, latency, Sharpe, drawdown, etc.
3. If ambiguous, infer from user wording and keep both in scope:
   - binary intent → Completion
   - performance/quality intent → Research

## Always trigger

Triggering phrases: `/loop`, `$loop`, “keep working until”, “improve”, “optimize”, “run until verified”.

## Pre-flight contract (required per run)

State these fields before the first edit:

- objective
- mode (`completion` | `research`)
- success criterion set (pass/fail or metric + direction)
- verification command/evidence
- editable scope
- keep/revert rule
- iteration budget (only if user gave one)
- stop condition

Full criteria checklist (required for both modes):

- target and exact pass rule are explicit
- verification command is defined and executable
- expected evidence is defined
- hypothesis/action is minimal and focused
- failure reason and next adjustment are logged
- decision class is one of: pass, keep, revert, inconclusive, blocked
- rollback/rollback_ok is considered
- state counters are updated
- target gap is recalculated when metric is used

For Research:

- baseline value
- best-so-far target definition
- minimum meaningful improvement
- hypothesis queue/order

This checklist must be completed in every 1-loop cycle before claiming stop.

## Workspace and evidence

Create/ensure under task root:

- `loop_project/state.json`
- `loop_project/attempts.jsonl`
- `loop_project/metrics.jsonl`
- `loop_project/diff.patch`
- `loop_project/README.md`

If workspace cannot be created or `git` is unavailable, take deterministic file snapshots (`.bak`) before risky edits.

## Iteration behavior

For each iteration:

1. choose one minimal action (do not batch unrelated changes),
2. apply it,
3. run verification,
4. classify result (`pass` / `inconclusive` / `blocked`),
5. append one line to `attempts.jsonl`,
6. update `state.json`,
7. stop if verified target reached, else adjust and continue.

Rules:

- Never repeat the same failed action unchanged.
- If result is inconclusive, tighten the next experiment and retry.
- Do not claim success without evidence.
- Keep looping after the first positive in optimization tasks unless target is verified.
- Stop only on verified success, explicit budget hit, blocker, or no useful non-repeating hypothesis.
- Never end after reporting progress; progress updates do not replace the next attempt.
- If a command/test/check is interrupted, retry briefly, then continue from last saved state.

For Research, if a change improves metric but misses minimum delta, mark inconclusive and run a stronger next experiment.

## Completion Loop and Research Loop (same core loop)

Both modes use the same iteration flow above. The only difference is the contract and pass criteria:

- Completion: pass/fail success gate (`done` / `not done`).
- Research: baseline-to-target metric gate, with minimum meaningful improvement.

Shared loop body:

1. Define objective, target, verification.
2. Execute smallest useful edit.
3. Verify with evidence.
4. Update metric/progress (for Research: compute delta vs target).
5. Decide `keep`, `revert`, or `retry`.
6. Update logs/state.
7. If verified target is met, stop; otherwise retry with a new approach.

## Diff and rollback

- Capture pre-change state (`git diff` or `.bak`) before risky edits.
- Append exact patch for each kept change to `loop_project/diff.patch`.
- If reverting later, write revert action to `attempts.jsonl` and only mark `rollback_ok=true` after verification.

## Logging templates

Attempt line:

- `{"timestamp":"...","attempt":1,"mode":"research","hypothesis":"...","action":"...","result":"pass|inconclusive|blocked","evidence":"...","verification_cmd":"...","metric_name":"...","metric_before":12,"metric_after":14,"delta":2,"changed_files":["..."],"target_gap_before":10,"target_gap_after":8,"decision":"kept|reverted|inconclusive","failure_reason":"","lesson":"...","next_adjustment":"...","rollback_ok":true}`

Metric line:

- `{"attempt":1,"metric_name":"loop_skill_readiness_score","value_before":12,"value_after":14,"delta":2,"unit":"count","notes":"...","verification":"...","rollback_ok":true,"attempted_action":"..."}`

## Final response

When stopping, report only:

- selected mode
- final result
- verification done
- attempts run
- kept/reverted/inconclusive counts
- for Research: baseline → final metric, delta, percent, decision (kept/reverted/inconclusive)
- remaining blocker/risk
