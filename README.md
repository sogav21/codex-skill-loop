# Loop Skill

`loop` is a Codex skill for iterative, evidence-based execution.

It activates on:

- `/loop`
- `$loop`
- phrases like "keep working until", "improve", "optimize", "run until verified"

## Behavior

The skill uses one shared execution engine for both modes:

- completion mode (binary success: pass/fail, exists/missing, fixed/broken)
- research mode (metric success: better/worse, higher/lower score, faster/slower)

Both modes run the same per-iteration loop:

1. load state and pick one hypothesis/action
2. apply one minimal change
3. run verification
4. log attempt and evidence
5. update counters in `loop_project/state.json`
6. continue or stop based on explicit rules

## Goal-first contract

Before editing, the skill must state a compact goal card:

- objective
- measurable success criterion
- verification command(s) + expected evidence
- stop rule
- scope and constraints
- keep/revert rule
- hypothesis ordering

## Logging

When `/loop` runs in a project, the following are maintained:

- `loop_project/state.json`
- `loop_project/attempts.jsonl`
- `loop_project/metrics.jsonl`
- `loop_project/diff.patch`
- `loop_project/README.md`

## Usage examples

- `/loop Fix this test, 8 rounds.`
- `/loop Improve this score until latency is under 200 ms.`
- `/loop Optimise quality and stop on best verified improvement.`

If no round count is provided, the skill loops until:

- target verified, or
- explicit blocker, or
- no useful non-repeating hypothesis.

When stopping without explicit limit, keep loop state with:

- `attempt_limit`: `explicit N` or `none`
- `iterations_run`: total attempts
- `stopped_for`: `success|budget|blocked|hypothesis_stagnation`

## Install

Copy this repo to:

`<codex-root>/skills/loop/`

with:

- `SKILL.md`
- `agents/openai.yaml`
