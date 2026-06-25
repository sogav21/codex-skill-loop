# Loop Codex Skill

`loop` is a unified Codex skill for iterative, evidence-based work. It activates with `/loop`, `$loop`, or requests to keep working until a task is achieved, verified, or improved.

## Modes

- Completion Loop: for binary outcomes such as fixed/not fixed, tests pass/fail, file exists/missing, UI correct/incorrect, or validation clean/dirty.
- Research Loop: for baseline-and-metric work such as improving accuracy, latency, score, Sharpe, drawdown, prompt quality, strategy quality, or performance.

Both modes use concrete verification, task-local memory, and a strategy update after every failed or inconclusive attempt. Goal-driven loops continue until the target is verified, blocked, or no useful next move remains. Research Loop also uses a goal contract, controlled experiments, keep/revert decisions, best-so-far tracking, a revert path before risky edits, and final improvement stats with before/after metrics when measurable.

## Usage

Trigger it with:

```text
/loop
```

or:

```text
Use $loop to keep iterating on this task until it is verified done.
```

You can optionally specify an iteration budget:

```text
/loop Fix this failing test, 8 rounds.
```

Large budgets are allowed when explicit:

```text
/loop Fix this flaky workflow, 100 rounds.
```

For large explicit budgets, the skill keeps a scratch log and checkpoints progress at least every 10 attempts.

For improvement work:

```text
/loop Optimise this benchmark score until the target latency is under 200 ms.
```

Research Loop keeps improving until the target is reached, an explicit user-provided budget is used, no useful next experiment remains, or another stop condition applies. If the user does not provide a round count, the skill must not invent one.

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
