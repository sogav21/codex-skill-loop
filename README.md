# Loop Codex Skill

`loop` is a unified Codex skill for iterative, evidence-based work. It activates with `/loop`, `$loop`, or requests to keep working until a task is achieved, verified, or improved.

## Modes

- Completion Loop: for binary outcomes such as fixed/not fixed, tests pass/fail, file exists/missing, UI correct/incorrect, or validation clean/dirty.
- Research Loop: for baseline-and-metric work such as improving accuracy, latency, score, Sharpe, drawdown, prompt quality, strategy quality, or performance.

Both modes use bounded iterations, concrete verification, task-local memory, and a strategy update after every failed or inconclusive attempt.

## Usage

Trigger it with:

```text
/loop
```

or:

```text
Use $loop to keep iterating on this task until it is verified done.
```

You can specify an iteration limit:

```text
/loop Fix this failing test, max 8 iterations.
```

For improvement work:

```text
/loop Improve this benchmark score, max 5 iterations.
```

## Installation

Copy this repository's contents into a Codex skill folder named `loop`, for example:

```text
loop/
  SKILL.md
  agents/openai.yaml
```

Then restart or refresh Codex so the skill is discovered.

## Files

- `SKILL.md`: The skill instructions.
- `agents/openai.yaml`: UI metadata for Codex skill listings.
