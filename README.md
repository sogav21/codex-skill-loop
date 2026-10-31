# Loop Skill

A Codex skill for goal-driven experiments: preserve the original, copy the best
verified version, make a change, measure it, and keep only confirmed improvement.
A failed experiment changes the approach, not the goal or the acceptance checks.

## Workflow

1. Define a concrete outcome, source scope, acceptance checks, and verification.
   For research, also define the metric, direction, target, and meaningful delta.
2. Copy and measure the original version. Keep that baseline unchanged.
3. Create each candidate from the best verified version, then make one coherent change.
4. Measure the candidate and reproduce a proposed improvement in a fresh copy.
5. Promote only improvement that preserves guards and passing checks. Otherwise,
   keep the best, diagnose the evidence, and test a different approach.
6. Repeat until every acceptance condition and target is verified. Integrate and
   verify the best version in the requested destination before declaring delivery.

Completion mode uses a fixed acceptance checklist. Research mode adds a numeric
threshold. Both use the same baseline/candidate/best workflow.

## No default attempt ceiling

There is no default iteration count or stop-after-two-failures rule. Rejected or
inconclusive experiments require a recorded lesson and a different approach.
Explicit user limits, stop requests, and genuine external blockers still apply.

This is not a promise of infinite uptime or success on an impossible goal.
The agent chooses changes; the helper does not autonomously generate code or
schedule future chats. Saved state allows the next invocation to resume after a
context/runtime interruption. A background scheduler needs separate authorization.

## Use the skill

Examples:

- `$loop Fix the failing acceptance tests and preserve unrelated work.`
- `$loop Reduce latency below 200 ms while every correctness check passes.`
- `$loop Reach a score of at least 90. Use no fixed attempt limit.`
- `$loop Continue the run saved in loop_project.`
- `$loop Try up to 8 candidates; preserve the best even if the target is not reached.`

When a target or critical constraint is missing, the skill asks for it before
experimentation. It does not invent a measurable objective from the word "optimize."

## Executable state manager

Python 3.10+; standard library only. The helper freezes a Python verifier, snapshots
working files, compares real results, and persists decisions. It leaves the
original source unchanged while experiments run in separate candidate directories.

```text
python scripts/loop_state.py init --source ./app --run ./loop_project --goal "Score at least 90 with all checks passing" --verifier ./verify.py --metric score --direction higher --target 90 --min-delta 1
python scripts/loop_state.py begin --run ./loop_project --hypothesis "Avoid repeated parsing" --approach "Parse once per batch"
# Edit files at the returned candidate path.
python scripts/loop_state.py evaluate --run ./loop_project
python scripts/loop_state.py status --run ./loop_project
```

Supply your own scoped app and verifier. After a rejected candidate, inspect its
receipt, then add a genuine diagnosis with `begin --lesson "..." --approach "..."`.
See [runtime.md](references/runtime.md) for the verifier JSON contract, modes,
comparison, evidence, limits, and crash recovery.

The helper enforces check/guard preservation and numeric comparisons. The agent is
responsible for meaningful hypotheses, honest verifiers, appropriate statistics,
and final integration. Two measurements do not establish statistical confidence.

Each run retains a baseline, frozen verifier, compact state, immutable accepted
versions, rejected candidates, raw verification output, and decision receipts.
State format 2 does not silently overwrite legacy instruction-only state/JSONL
files. Preserve old runs and use a new directory when adopting the helper.

## Install

Copy `SKILL.md`, `agents/`, `scripts/`, and `references/` together into a
supported user skill directory named `loop`, such as `~/.agents/skills/loop/`.
Use your existing user skill root when your installation already has one.
Do not install a duplicate with the same skill name. Existing user work and
instruction files must be preserved when updating.

[Official skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Verify

```text
python -m unittest discover -s tests -v
```

Tests execute real local verifier subprocesses on synthetic products. They cover
promotion, regression/guard rejection, meaningful deltas, recovery, fixed targets,
completion/research modes, explicit budgets, and continuation beyond many attempts.
They do not prove success on arbitrary tasks or indefinite execution.

[Comparison with the earlier installed skill](COMPARISON.md).

Run state and source evidence can contain private code or data. Keep them out of
public repositories; the included .gitignore excludes the standard run directory.
