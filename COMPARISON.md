# Comparison with the earlier installed loop skill

This compares the installed instruction-only skill before the change with the
updated skill and executable helper. The installed copy was read, not modified.
Comparison inputs and products were entirely synthetic; no personal project data
or machine-specific evidence is published here.

## What changed

| Capability | Earlier installed skill | Updated skill |
|---|---|---|
| Goal and acceptance definition | Required goal card | Same principle, frozen target/check contract in the helper |
| Default attempt count | None, but also a two-repeat stop rule and hypothesis-stagnation stop | None; failed experiments require diagnosis and changed approach, without a failure-count ceiling |
| Baseline and best | Instructions to record diffs/snapshots and best metric | Actual original snapshot, separate best pointer, and each candidate copied from the best |
| Keep/revert | Agent arranges comparison and rollback | Helper rejects regressions, guard failures, ties, and invalid measurements |
| Promotion confirmation | Agent must arrange reproducibility | Proposed promotions evaluated in a fresh copy before acceptance |
| Resume | Agent maintains JSON/JSONL state | Atomic state, OS writer lock, receipt replay, and snapshot/measurement identity checks |
| Failed strategy | Instruction to change strategy | Agent diagnoses; helper additionally requires a lesson and changed approach label |
| Final integration | Agent responsibility | Still agent responsibility; the skill explicitly requires integrated verification |
| Indefinite execution | No runtime mechanism supplied | Persistent continuation, not an autonomous background agent or infinite-uptime guarantee |

The entrypoint was reduced from 696 to 574 whitespace-separated words (about
17.5%), with runtime mechanics in an explicitly linked reference. That is a text
size measurement, not a tokenizer, latency, or agent-quality benchmark. The new
reference and helper add capability, so total distribution size is larger.

## Same practical scenario, two independent runs

Each agent received its skill and an identical isolated local fixture. The task was
to evaluate four supplied normalization implementations in order, retain the best,
and integrate it into the original synthetic app. The target was score 4 across
four actual string-normalization checks, while preserving None as None. Neither
agent could change the verifier, proposals, or target.

The cases were `" a " -> "a"`, `"B" -> "b"`, `" C " -> "c"`, and `"D" -> "d"`.
The separate None guard prevents an implementation from winning by converting
None into a string. This is a functional coverage score, not a performance metric.

| Experiment | Actual score | None guard | Earlier installed skill | Updated skill |
|---|---:|---|---|---|
| Original string conversion | 0 | Pass | Baseline | Baseline |
| Trim whitespace, retain None branch | 1 | Pass | Keep | Keep with fresh confirmation |
| Trim and lowercase, without None branch | 4 | Fail | Revert | Revert: named guard failure |
| Alternative staged trimming | 1 | Pass | Revert: no improvement | Revert: no improvement |
| Trim and lowercase with None branch | 4 | Pass | Pass | Pass with fresh confirmation |

**Both reached 0 -> 4 and passed the actual verifier after final integration.**
The earlier-skill agent wrote a task-local runner to arrange snapshots, selection,
and evidence manually. The updated-skill agent used the supplied helper. This
comparison does not show that the old skill cannot succeed, or that the new one
is faster; fresh confirmations intentionally add verification work.

Selecting meaningful hypotheses, judging a diagnosis, reviewing a verifier,
choosing appropriate statistics, and final integration still require agent judgment.
The helper enforces version/evidence selection, not the quality of every idea.

## Failure and recovery verification

The independent pass found three concrete integrity defects during development.
Each was reproduced before repair and added to regression coverage:

- A modified promoted snapshot could be accepted during interrupted receipt replay.
- A concurrent candidate edit immediately before snapshot copying could report pass
  using measurements from different source bytes.
- Rewriting the saved best score could make an equivalent candidate look improved.

The final focused pass confirmed that all three are now rejected before false
promotion, while valid recovery remains idempotent and the original four-experiment
scenario still succeeds. Goal and verifier mutation controls were also checked.

The executable suite additionally covers completion mode, higher/lower metrics,
meaningful deltas, non-finite/malformed output, source-mutating verification,
explicit budgets, continuation through four failed experiments, and 32 successful
iterations with no default attempt limit:

```text
python -m unittest discover -s tests -v
```

These are controlled local tests and bounded independent agent runs. They do not
prove arbitrary-task success, statistically reliable optimization, every possible
crash interleaving, or a literally infinite process. Run evidence remains private;
only this synthetic summary and reusable regression tests are part of the repository.
