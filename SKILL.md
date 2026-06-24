---
name: loop
description: Iterative completion workflow triggered by /loop or $loop. Use when Codex must keep working on a task until the requested outcome is achieved and verified, especially for debugging, implementation, data cleanup, UI polish, test fixing, or other tasks where one pass may not be enough. Enforces explicit target definition, bounded iterations, evidence-based verification, task-local memory, and strategy improvement after failures.
---

# Loop

## Core Rule

Keep iterating until the requested outcome is achieved and verified, a stop condition is reached, or continuing would be unsafe. Do not declare success from vibes; use concrete evidence.

## 1. Define Target

Before the first attempt, state:

- Objective: Restate the user's task.
- Desired result: Extract the exact outcome the user wants.
- Success criteria: List observable conditions that must be true.
- Verification method: Name the evidence that will prove the criteria are met.
- Iteration limit: Use the user's limit when specified; otherwise use 5.

If the target is ambiguous but a reasonable assumption is safe, proceed and record the assumption. Ask only when missing information makes progress risky or impossible.

## 2. Iterate

For each attempt, perform the smallest useful move that can advance the task:

1. Plan the next move.
2. Execute it.
3. Capture what changed.
4. Verify with evidence.
5. Compare the result against the success criteria.
6. If it failed, diagnose why.
7. Update the strategy before retrying.

Never repeat the same failed action unchanged. After every failed attempt, improve at least one of:

- plan
- prompt or working framing
- assumptions
- verification method
- implementation approach

## 3. Verify With Evidence

Choose verification that matches the task:

- Code: tests, type checks, linters, targeted scripts, command output.
- UI: browser checks, screenshots, visual inspection, interaction checks, accessibility or console checks when relevant.
- Data: row counts, schema checks, validation scripts, spot checks, before/after comparisons.
- System work: logs, diffs, process status, health checks, command output.
- File work: direct file inspection, rendered previews, checksums, parse/validation commands where relevant.

Before declaring success, state exactly what was verified and what evidence passed.

## 4. Maintain Task-Local Memory

Track the loop state while working:

- attempt number
- action taken
- result
- verification evidence
- failure reason, if any
- lesson learned
- next strategy adjustment

For normal tasks, keep this in working context. For larger, long-running, risky, or multi-file tasks, write a scratch log under `memory/scratch/` in the active workspace. Do not update long-term memory unless the user explicitly says to remember it.

## 5. Stop Conditions

Stop only when one of these is true:

- Success criteria are met and verified.
- The max iteration limit is reached.
- The task is blocked by missing information, permissions, credentials, unavailable tools, or external state.
- Continuing would require destructive or external action without approval.

If the max iteration limit is reached, report the best current result, the evidence gathered, and the next recommended move.

## Final Response

Keep the final response concise and include:

- final result
- verification performed
- iteration count
- remaining blocker or risk, if any
