---
name: loop
description: Unified iterative workflow triggered by /loop, $loop, or requests to keep working until a task is achieved, verified, optimized, optimised, or improved. Automatically choose Completion Loop for binary success criteria such as fixed/not fixed, tests pass/fail, file exists/missing, UI correct/incorrect, or validation clean/dirty. Choose Research Loop for baseline-and-metric work such as improve, optimize, optimise, experiment, benchmark, metric, Sharpe, accuracy, latency, score, drawdown, strategy, prompt, model, or performance improvement unless binary success is clearly intended.
---

# Loop

## Mode Selection

Choose one mode before starting:

- Completion Loop: Use when success is binary: fixed/not fixed, tests pass/fail, file exists/missing, UI correct/incorrect, validation clean/dirty.
- Research Loop: Use when there is a baseline and metric: better/worse, faster/slower, higher/lower score, improved strategy, improved prompt, improved model, improved performance.

If the task includes words like improve, optimize, optimise, experiment, benchmark, metric, baseline, Sharpe, accuracy, latency, score, drawdown, use Research Loop unless binary success is clearly intended.

## Shared Rules

- Start with a goal contract: objective, selected mode, max attempts, success target, verification method, editable scope, and stop conditions.
- Auto-loop by default: within the current turn, after each attempt, immediately continue to the next attempt until a stop condition is met.
- Do not pause to report progress or ask what to try next between attempts unless blocked or approval is required.
- A progress update may summarize work, but it must not replace the next attempt when attempts remain.
- Do not stop after the first useful change in open-ended improvement work; continue until max attempts, no useful next attempt exists, or another stop condition is met.
- Do not declare success without verification.
- Keep iteration count bounded. Default max attempts: 5; use the user's explicit max when provided.
- For large limits such as 100 rounds, continue only while each attempt can make useful progress, maintain a scratch log, and checkpoint progress at least every 10 attempts.
- Never repeat the same failed action unchanged.
- After every failed or inconclusive attempt, update the strategy before retrying.
- Maintain task-local memory: attempt number, hypothesis or plan, action taken, result, verification evidence, failure reason or metric delta, lesson learned, next strategy adjustment.
- For Research Loop, also track current baseline, best-so-far result, target gap, and whether the last attempt moved toward the target.
- For large, risky, long-running, or multi-file tasks, write a scratch log under `memory/scratch/`.
- Do not update long-term memory unless the user explicitly says to remember it.
- Stop before destructive or external/public actions unless the user confirms.
- If the user asks for "ideal", "best", or open-ended quality, translate that into a concrete target and measurable checks before editing.

## Completion Loop

Use this for tasks with pass/fail success criteria.

1. Define objective.
2. Define desired result.
3. Define success criteria.
4. Define verification method.
5. Execute the smallest useful step.
6. Verify with evidence.
7. If success criteria pass, stop.
8. If not, diagnose failure, adjust strategy, and immediately retry.

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
9. Measure result against baseline and target.
10. If target is met according to the verification method, keep the change and stop.
11. If better but target is not met, keep the change, update baseline, choose the next hypothesis, and continue.
12. If worse, revert the change before the next attempt.
13. If inconclusive, either revert or keep only if the keep rule allows neutral changes; log why and retry with a sharper experiment.
14. Update next hypothesis and immediately repeat.

Prefer disciplined optimization:

- Change one variable at a time when practical.
- Set a minimum meaningful improvement before testing.
- Keep the evaluation stable enough that before/after comparisons are fair.
- Treat noisy, flaky, or underpowered results as inconclusive.
- Revert experiments that improve the metric by cheating the goal, overfitting, or breaking constraints.

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

Give a final response only after a stop condition is met. Keep it concise and include:

- selected mode
- final result
- verification performed
- iteration count
- for Research Loop: baseline, final metric, and kept/reverted decision
- remaining blocker or risk, if any
