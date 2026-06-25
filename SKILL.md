
---
name: loop
description: Unified iterative workflow triggered by /loop, $loop, or requests to keep working until a task is achieved, verified, optimized, optimised, improved, or reported with improvement stats. Automatically choose Completion Loop for binary success criteria such as fixed/not fixed, tests pass/fail, file exists/missing, UI correct/incorrect, or validation clean/dirty. Choose Research Loop for baseline-and-metric work such as improve, optimize, optimise, experiment, benchmark, metric, Sharpe, accuracy, latency, score, drawdown, strategy, prompt, model, or performance improvement unless binary success is clearly intended. Goal-driven loops continue until the verified target is reached, blocked, or no useful next move remains.
---

# Loop

## Mode Selection

Choose one mode before starting:

- Completion Loop: Use when success is binary: fixed/not fixed, tests pass/fail, file exists/missing, UI correct/incorrect, validation clean/dirty.
- Research Loop: Use when there is a baseline and metric: better/worse, faster/slower, higher/lower score, improved strategy, improved prompt, improved model, improved performance.

If the task includes words like improve, optimize, optimise, experiment, benchmark, metric, baseline, Sharpe, accuracy, latency, score, drawdown, use Research Loop unless binary success is clearly intended.

Mode precedence rule:

- If the user asks for a binary outcome (pass/fail, exists/not exists, fixed/not fixed), prefer Completion Loop.
- If the user asks for a numeric or directional goal (faster/slower, better/worse, higher/lower, optimize X), prefer Research Loop.

Fast trigger: if user says `/loop`, `$loop`, or explicitly asks to "keep iterating", "keep working until", "improve", or "optimize", select a looping mode automatically before making edits.

## Shared Rules

### Loop Project Run Contract

For every non-trivial `/loop` run in a project directory:

- initialize a task workspace under the current task root as `loop_project/`
- append a compact snapshot to `loop_project/state.json` before the first edit
- record each attempt in `loop_project/attempts.jsonl` and each measured metric in `loop_project/metrics.jsonl`
- keep a machine-parseable diff snapshot in `loop_project/diff.patch` for every kept change (or append a note if no diff is produced)
- when available, validate written JSON lines against `attempt_schema.json` and `metrics_schema.json`
- Use a run-specific subfolder when multiple loops run from the same workspace, e.g. `loop_project/<run_id>/` if needed to avoid overwriting logs and metrics.
- If `git` is unavailable, capture file snapshots (`copy src dest.bak`) so rollback is still deterministic.

### Goal Contract (required for each run)

Before edits, state these exact fields:

- objective
- selected mode (`completion` / `research`)
- success criteria or measurable metric + direction
- verification command/output
- editable scope
- keep/revert rule
- evidence requirement (which evidence proves success)
- minimum meaningful improvement (Research only)
- stop condition

- Start with a goal contract: objective, selected mode, target result, success criteria or metric target, verification method, editable scope, keep/revert rule when relevant, and stop conditions.
- For Research Loop, the contract must also include: baseline value, best-so-far target definition, minimum meaningful improvement, and a hypothesis queue/list (or a clear statement that hypotheses are generated dynamically and why).
- For goal-driven work, do not invent an attempt limit. Continue until the verified target is reached, a real blocker is hit, no useful next move remains, or user/tool safety requires stopping.
- If the user requests optimise/improve/iterate and does not provide a clear metric/target, you MUST infer a concrete, measurable target in the goal contract before the first edit (for example: reduce time by 20%, fix 1 specific regression, improve score by X points, etc.) and state it explicitly in the contract.
- Use an iteration budget only when the user explicitly gives one. If the task is open-ended, first translate it into a measurable target and then loop toward that target.
- Treat any user-provided round count as a work budget, not a stopping excuse: if the target is reached early, stop; if the budget ends before success, report the remaining gap and the next best move.
- Auto-loop by default: within the current turn, after each attempt, immediately continue to the next attempt until a stop condition is met.
- Hard-stop rule: never end a Research Loop on a single small/neutral change. At least one additional hypothesis test must be attempted after first edit unless stop condition is already verified by evidence.
- If an attempt cannot measure the target metric, treat it as inconclusive and continue with a sharper experiment; do not mark progress or stop on compile-only or smoke-only checks.
- Do not pause to report progress, ask what to try next, or end the turn after one attempt unless a stop condition is met.
- A progress update may summarize work, but it must not replace the next attempt when the target is not yet verified.
- For Research Loop without an explicit user-provided budget, never stop after the first attempt unless target/stop condition is already verified by evidence.
- "No useful next attempt remains" is valid only when you can show no new, non-repeating hypothesis (different variable/approach) is available.
- If a command, run, browser check, or long task is interrupted or cut off, resume from the last recorded state and continue the loop. Do not turn an interruption into a final answer unless it is a real blocker after retrying or changing approach.
- Do not stop after the first useful change in open-ended improvement work; continue until the target is verified, an explicit user-provided budget is exhausted, no useful next attempt exists, or another stop condition is met.
- Do not declare success without verification.
- Keep loops bounded by stop conditions, verification, and useful progress. For large user budgets such as 100 rounds, continue only while each attempt can make useful progress, maintain a scratch log, and checkpoint progress at least every 10 attempts.
- Never repeat the same failed action unchanged.
- After every failed or inconclusive attempt, update the strategy before retrying.
- Maintain task-local memory: attempt number, hypothesis or plan, action taken, result, verification evidence, failure reason or metric delta, lesson learned, next strategy adjustment.
- For Research Loop, also track current baseline, best-so-far result, target gap, and whether the last attempt moved toward the target.
- For any improvement, optimization, refactor-for-speed, or quality loop, collect end-of-loop improvement stats: before/after, delta, percent change when meaningful, and the best verified proxy when the ideal metric is unavailable.
- For large, risky, long-running, or multi-file tasks, write a scratch log under `memory/scratch/`.
- For optimization and experiments, create and use a task workspace automatically:
  - if it does not exist, create `loop_project/` in the task working directory
  - create at minimum:
    - `loop_project/README.md`
    - `loop_project/metrics.jsonl`
    - `loop_project/attempts.jsonl`
    - `loop_project/state.json`
    - `loop_project/diff.patch` (snapshot of each kept change)
  - if the task workspace cannot be created, ask for explicit permission to proceed without persistent logging and state that metrics are session-only for that turn.
- In every iteration, append one JSON object per line to `loop_project/attempts.jsonl` with:
  - `timestamp`
  - `attempt`
  - `mode`
  - `hypothesis`
  - `action`
  - `result`
  - `evidence`
  - `changed_files` (array of paths)
  - `metric_before`
  - `metric_after`
  - `delta`
  - `decision` (`kept`, `reverted`, `inconclusive`)
  - `failure_reason`
  - `lesson`
  - `next_adjustment`
- Update `loop_project/state.json` before/after each iteration with:
  - `selected_mode`
  - `objective`
  - `target`
  - `baseline_metric`
  - `best_metric`
  - `last_action_files`
  - `attempts`
  - `kept`, `reverted`, `inconclusive`
- Do not update long-term memory unless the user explicitly says to remember it.
- Stop before destructive or external/public actions unless the user confirms.
- If the user asks for "ideal", "best", or open-ended quality, translate that into a concrete target and measurable checks before editing.

Before the first attempt, state this compact contract:

- target outcome
- selected mode and why
- success metric or pass/fail criteria
- verification command or evidence
- revert/keep rule for changes
- user-provided iteration budget, only if explicitly provided

### Research Loop Preflight

Before any Research Loop attempt, ensure these are set:
- objective, baseline, and directional metric
- minimum meaningful delta
- random seed / deterministic settings when available (or explicit nondeterminism note)
- hypothesis queue
- experiment keep/revert guard

## Completion Loop

Use this for tasks with pass/fail success criteria.

### Research Loop Preflight

Before any Research Loop attempt, ensure:

- objective, baseline metric, and target direction are captured
- minimum meaningful delta is defined
- deterministic settings (seed, fixed params, train/test split) are fixed, or explicitly marked as stochastic
- hypothesis queue or ordering policy is explicit
- keep/revert guard is stated before changing files
- rollback command is prepared before risky edits

1. Define objective.
2. Define desired result.
3. Define success criteria.
4. Define verification method.
5. Execute the smallest useful step.
6. Verify with evidence.
7. If success criteria pass, stop.
8. If not, diagnose failure, adjust strategy, and immediately retry.
9. Do not stop because one attempt was made. Stop only when the pass/fail criteria are verified, a blocker is real, or the next move would violate safety or user approval boundaries.
10. If pass/fail criteria are not verifiable from direct outputs (e.g., syntax-only checks for behavior-related changes), label attempt as inconclusive and continue.

## Research Loop

Use this for improvement tasks with a baseline and metric.

1. Establish baseline.
2. Define metric and direction: higher is better, or lower is better.
3. Define target threshold or stopping target: the metric value, score, behavior, or quality bar that means the goal is achieved.
4. Define verification command or evaluation method.
5. Define editable scope.
6. Define keep/revert rule before editing.
7. Capture the pre-experiment state, such as `git diff`, copied file content, generated artifact backup, or command output needed to revert safely.
   If no reliable revert path exists, create one before experimenting or narrow the editable scope.
8. Run one controlled experiment per iteration when possible.
9. Measure result against baseline and target using the defined verification method.
10. Record per-attempt evidence in this order: `baseline -> after`, metric change, target gap, decision.
11. If target is met according to the verification method, keep the change and stop.
12. If better and closer to target, keep the change, update baseline, choose the next hypothesis, and continue.
13. If better but still not useful (improvement smaller than minimum meaningful delta defined in the contract), treat as inconclusive; do not keep, and retry with a sharper experiment.
14. If worse, revert the change before the next attempt and continue only if a different non-repeating hypothesis remains.
15. If inconclusive, either revert or keep only if the keep/revert rule allows neutral changes; log why and retry with a sharper experiment.
16. If improvement would be achieved only by changing constraints, hidden assumptions, or violating scope, mark as invalid and revert.
17. Record attempt result class explicitly:
    - pass: target verified or clear improvement
    - inconclusive: not measurable or insufficient delta
    - blocked: external constraint or safety prevents next safe action
16. Update next hypothesis and immediately repeat.
17. For goal-driven optimization, keep experimenting until the metric target or behavioral target is verified. Do not stop merely because the first improvement was positive.
18. For any Research Loop with no explicit user budget, require at least 2 experiments (attempts) unless the target is verified after attempt 1.
19. If attempts are inconclusive or not useful, you may stop only when all non-repeating, meaningful hypotheses have been tried.

Prefer disciplined optimization:

- Change one variable at a time when practical.
- Set a minimum meaningful improvement before testing.
- Keep the evaluation stable enough that before/after comparisons are fair.
- Treat noisy, flaky, or underpowered results as inconclusive.
- Revert experiments that improve the metric by cheating the goal, overfitting, or breaking constraints.

### Diff and Rollback Procedure

- Capture pre-change state before risky edits (`git diff` baseline or file snapshots in `loop_project/<run>/pre/`).
- For each kept change, write the exact patch segment into `loop_project/diff.patch` and record the command used to create it.
- If a kept change is later reverted, append that revert command and result to `loop_project/attempts.jsonl` and flip `rollback_ok` to `true` only after verification.

For each Research Loop attempt, record:

- baseline value
- target threshold or stopping target
- experiment hypothesis
- changed files
- metric before
- metric after
- target gap after
- decision: keep, revert, or inconclusive
- revert method used or prepared
- lesson learned
- verification evidence and whether rollback succeeded

At the end of every Research Loop, report improvement stats:

- baseline metric and final metric
- absolute delta and percentage delta when meaningful
- best kept experiment and why it was kept
- attempts kept, reverted, and inconclusive
- verification command or evidence used
- any stats that could not be measured reliably

Use this shape when possible: `metric: before -> after, delta, percent`; `attempts: total, kept, reverted, inconclusive`; `evidence: command output, test count, screenshot, diff, benchmark, or validated file check`.

## Verification Examples

- Code: tests, type checks, linters, targeted scripts, command output.
- UI: browser checks, screenshots, console checks, interaction checks.
- Data: row counts, schema checks, validation scripts, spot checks.
- Trading: backtests, CAGR, Sharpe, max drawdown, winrate, risk/reward, out-of-sample checks.
- Prompt or skill work: benchmark prompts, scored examples, regression cases.
- Performance: benchmark time, memory, latency, throughput.

## External Action Guard

For WhatsApp, email, Discord messages, public posts, file sends, or anything that leaves the machine:

- Draft, verify, and prepare only.
- Stop before sending.
- Ask for explicit confirmation with target and payload.

## Stop Conditions

Stop when success is verified, an explicit user-provided experiment budget is reached, required information or credentials are missing, tools are unavailable after adapted retries, external state blocks progress, no useful non-repeated next move remains, or continuing would require destructive or external/public action without confirmation.

## Final Response

Give a final response only after a stop condition is met. Keep it concise and include:

- selected mode
- final result
- verification performed
- iteration count
- improvement stats for optimization or quality loops, including before/after, delta, and percent change when measurable
- for Research Loop: baseline, final metric, and kept/reverted decision
- whether the verified target was reached, an explicit user-provided budget was reached, or the loop stopped because no useful next attempt remained
- remaining blocker or risk, if any

## Logging Templates

Attempt entry example:

- `{\"timestamp\":\"...\",\"attempt\":2,\"mode\":\"research\",\"hypothesis\":\"...\",\"action\":\"...\",\"result\":\"pass|inconclusive|blocked\",\"result_class\":\"pass\",\"evidence\":\"...\",\"verification_cmd\":\"...\",\"metric_name\":\"...\",\"target_gap_before\":10,\"target_gap_after\":4,\"changed_files\":[\"path/to/file\"],\"metric_before\":12,\"metric_after\":14,\"delta\":2,\"decision\":\"kept\",\"failure_reason\":\"\",\"lesson\":\"...\",\"next_adjustment\":\"...\",\"rollback_ok\":true}`

Metric entry example:

- `{\"attempt\":2,\"metric_name\":\"loop_skill_readiness_score\",\"value_before\":12,\"value_after\":14,\"delta\":2,\"unit\":\"count\",\"notes\":\"...\",\"verification\":\"...\",\"rollback_ok\":true,\"attempted_action\":\"...\"}`

Validation command examples:

- `Get-Content loop_project/attempt_schema.json | ConvertFrom-Json` (schema parse)
- `Get-Content loop_project/attempts.jsonl | ForEach-Object { $_ | ConvertFrom-Json }` (attempts parse)
- `Get-Content loop_project/metrics.jsonl | ForEach-Object { $_ | ConvertFrom-Json }` (metrics parse)
- `Get-Content loop_project/state.json | ConvertFrom-Json` (state parse)
