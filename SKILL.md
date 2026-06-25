---
name: loop
description: Codex-optimized iterative workflow for /loop and $loop with goal-based execution, verifiable evidence, and explicit keep/revert logic.
---

# Loop

## Trigger

- `/loop`
- `$loop`
- user asks to keep working until verified, optimize, improve, iterate, or run research

## Pre-loop intake

Before starting the first loop iteration, check whether the request is concrete enough to run safely and usefully.

If any of these are missing or ambiguous, ask for them first and do not start looping yet:

- exact target outcome or problem statement
- the file, subsystem, or surface to work on
- what counts as success or done
- whether the user wants completion mode or research mode
- any explicit attempt budget, deadline, or stop condition

Keep the intake short and focused:

- ask up to 3 questions at once
- prefer questions that unblock the next iteration directly
- split broad prompts into smaller parts and confirm each part only when needed
- if the user already gave enough detail, skip questions and start the loop immediately

After intake, restate the working objective in one sentence before the first iteration.

## Mode selection

- **Completion mode**: binary success (pass/fail, exists/missing, fixed/broken, valid/invalid).
- **Research mode**: metric-based success (improve/worsen, faster/slower, higher/lower score).
- Auto mode selection:
  - Choose completion mode for explicit binary outcomes (`fixed`, `pass`, `exists`, `valid`, `success`).
  - Choose research mode for optimization/reasoning words (`improve`, `optimize`, `benchmark`, `metric`, `faster`, `score`, `latency`, `Sharpe`, `accuracy`, `recall`, `precision`, `drawdown`) unless user clearly states a binary target.
  - If intent is mixed, pick the mode with the clearest verifiable end condition.
- Do not add an attempt limit unless the user explicitly asks for one.
- If user gives explicit `N rounds`, treat it as a hard attempt budget.
- If no budget is given, keep looping until target is verified or a non-recoverable stop rule is hit.

## Research pass definition

When operating in research mode, `pass` means all of the following are true:

- the user-defined research objective is explicit enough to measure
- the target metric reached the requested direction or threshold
- the final result is reproducible from the recorded evidence
- any remaining ambiguity about what "loop research" means has been resolved into a concrete measurable target

If the user has not provided a concrete research target yet, ask for it before the first iteration instead of guessing.

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
- attempt budget handling (`N` rounds if explicit; otherwise no fixed budget)
- do not write to long-term memory; keep task-local memory in attempt logs/state only.

Before the first iteration, set a **working objective**:

- objective summary
- exact success condition(s)
- measurable target and baseline/method (for research)
- hypothesis stack (one action per attempt)
- stop conditions in priority order:
  1. success verified
  2. explicit budget exhausted
  3. user-blocked external action required
  4. repeated no-improvement attempts with no new hypothesis (`stop`)
- for risky, multi-file, or long-running tasks, keep a scratch log in `memory/scratch/` with each attempt record.

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

### Autoloop contract

- Default to `while not done` with explicit state persisted every iteration.
- On every attempt, run exactly one smallest action, verify immediately, then:
  - `pass` -> stop and report success
  - `keep` -> continue with improved/next hypothesis
  - `revert` -> rollback and continue only if objective still open
  - `inconclusive`/`blocked` -> retry with a changed strategy once; if repeated without new evidence in 2 consecutive attempts, stop as `blocked`
- Never stop because partial progress was made if target is still not verified.
- Never repeat the same failed action unchanged; if no fresh hypothesis is available, stop with explicit blocker reason.

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
- Never stop a research loop only because of first neutral/positive change; verify that either target is reached or the next attempt is no longer useful.

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

Add these required stop fields:

- `attempt_limit`: `explicit <N>` or `none`
- `iterations_run`: integer
- `stopped_for`: `success|budget|blocked|hypothesis_stagnation`

## GitHub merge on pass

If the user asked to merge on success, then after a verified `pass`:

- prepare the minimal merge-ready change set
- use the GitHub workflow available in the workspace to merge the branch or PR
- report the merge target and the verification evidence in the final handoff

Do not merge before the `pass` condition is verified.
