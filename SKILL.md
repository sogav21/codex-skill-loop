---
name: loop
description: Unified iterative workflow triggered by /loop, $loop, or requests to keep working until a task is achieved, verified, or improved. Automatically choose Completion Loop for binary success criteria such as fixed/not fixed, tests pass/fail, file exists/missing, UI correct/incorrect, or validation clean/dirty. Choose Research Loop for baseline-and-metric work such as improve, optimize, experiment, benchmark, metric, Sharpe, accuracy, latency, score, drawdown, strategy, prompt, model, or performance improvement unless binary success is clearly intended.
---

# Loop

## Mode Selection

Choose one mode before starting:

- Completion Loop: Use when success is binary: fixed/not fixed, tests pass/fail, file exists/missing, UI correct/incorrect, validation clean/dirty.
- Research Loop: Use when there is a baseline and metric: better/worse, faster/slower, higher/lower score, improved strategy, improved prompt, improved model, improved performance.

If the task includes words like improve, optimize, experiment, benchmark, metric, baseline, Sharpe, accuracy, latency, score, drawdown, use Research Loop unless binary success is clearly intended.

## Shared Rules

- Do not declare success without verification.
- Keep iteration count bounded. Default max attempts: 5.
- Never repeat the same failed action unchanged.
- After every failed or inconclusive attempt, update the strategy before retrying.
- Maintain task-local memory: attempt number, hypothesis or plan, action taken, result, verification evidence, failure reason or metric delta, lesson learned, next strategy adjustment.
- For large, risky, long-running, or multi-file tasks, write a scratch log under `memory/scratch/`.
- Do not update long-term memory unless the user explicitly says to remember it.
- Stop before destructive or external/public actions unless the user confirms.

## Completion Loop

Use this for tasks with pass/fail success criteria.

1. Define objective.
2. Define desired result.
3. Define success criteria.
4. Define verification method.
5. Execute the smallest useful step.
6. Verify with evidence.
7. If success criteria pass, stop.
8. If not, diagnose failure, adjust strategy, and retry.

## Research Loop

Use this for improvement tasks with a baseline and metric.

1. Establish baseline.
2. Define metric and direction: higher is better, or lower is better.
3. Define verification command or evaluation method.
4. Define editable scope.
5. Define keep/revert rule.
6. Run one controlled experiment per iteration when possible.
7. Measure result against baseline.
8. If better according to the keep rule, keep the change and update baseline.
9. If worse, revert the change.
10. If inconclusive, log it and decide whether to retry with a sharper experiment.
11. Update next hypothesis and repeat.

For each Research Loop attempt, record:

- baseline value
- experiment hypothesis
- changed files
- metric before
- metric after
- decision: keep, revert, or inconclusive
- lesson learned

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

Stop when success is verified, max attempts are reached, required information or credentials are missing, tools are unavailable, external state blocks progress, or continuing would require destructive or external/public action without confirmation.

## Final Response

Keep the final response concise and include:

- selected mode
- final result
- verification performed
- iteration count
- for Research Loop: baseline, final metric, and kept/reverted decision
- remaining blocker or risk, if any
