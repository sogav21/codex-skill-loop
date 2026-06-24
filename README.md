# Loop Codex Skill

`loop` is a Codex skill for iterative, evidence-based task completion. It is designed for tasks where one pass may not be enough, such as debugging, implementation, UI polish, data cleanup, or test fixing.

## What It Does

The skill makes Codex:

- define the target outcome before starting
- set success criteria and a verification method
- iterate up to a bounded limit, defaulting to 5 attempts
- verify each attempt with concrete evidence
- keep task-local memory of attempts and lessons learned
- improve the strategy after each failed attempt
- stop only when success is verified or a clear stop condition is reached

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
