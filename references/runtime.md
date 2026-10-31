# Persistent loop runtime

The helper uses Python 3.10+ and the standard library. It manages versions and
evidence; it is not a code writer, sandbox, service, or background scheduler.
The agent supplies hypotheses, edits candidates, diagnoses evidence, and repeats.
Resolve script paths from the installed skill directory.

## Establish the baseline

Choose a small source scope and a separate private run directory. Existing runs
are never overwritten. Nested source/run directories are rejected to prevent
recursive copies. Snapshots include working files, including uncommitted files;
`.git`, `__pycache__`, and `.pytest_cache` are excluded. Symlinks are rejected.
Avoid an unrelated repository, secrets directory, or huge data store as the scope.

Supply a self-contained Python verifier that reads the candidate from its current
working directory and emits one JSON object on stdout. It may run actual project
tests/benchmarks through subprocesses. Translate their results into this contract:

```json
{
  "checks": {"required_behavior": false, "regression_tests": true},
  "guards": {"data_preserved": true},
  "metrics": {"score": 40}
}
```

Exit 0 means a valid measurement, including a measured failing target. Nonzero
means evaluation/tool failure. Send diagnostics to stderr. Checks form the fixed
acceptance checklist. Guards are mandatory constraints; omit them only if none
apply. Check/guard values must be booleans, metrics finite numbers. The baseline
freezes check/guard names. Candidates cannot omit a failing check or replace it.

The verifier is frozen at control/verifier.py and reused. It must not edit candidate
source. It runs with local process permissions; review it first. External benchmark
data and dependencies must stay comparable; the helper does not freeze the OS/network.

```text
python scripts/loop_state.py init --source ./app --run ./loop_project --goal "Score at least 90 with all checks passing" --verifier ./verify.py --metric score --direction higher --target 90 --min-delta 1
```

Omit metric/direction/target for completion mode: all checks and guards must pass.
Research adds the target threshold. `--min-delta` defaults to zero, but a metric-only
promotion still requires strictly positive gain. A newly passing check or a confirmed
goal also counts if no previously passing check or metric regresses.

`--max-attempts N` and `--timeout-seconds N` have no default limit. Set them only
when appropriate to explicit task limits. A target already met at baseline is
confirmed in a fresh copy before reporting success. Invalid baseline verification
preserves its snapshot/evidence without starting an unverifiable run; fix the
prerequisite and choose a new run directory.

## One attempt

```text
python scripts/loop_state.py begin --run ./loop_project --hypothesis "A cached lookup removes repeated work" --approach "Cache the lookup"
```

Read the returned candidate path and edit there. It is copied from the best, not
the last failed experiment. An already pending candidate is returned unchanged.

```text
python scripts/loop_state.py evaluate --run ./loop_project
python scripts/loop_state.py status --run ./loop_project
```

Evaluate saves raw stdout/stderr, measurements, and a decision receipt. A proposed
promotion is verified in a fresh copy; both results must improve against the same
best. The conservative metric of the pair becomes the best. Passing checks cannot
regress, guards must be true, and the declared metric cannot worsen. A goal must
reproduce too. Both outputs remain available rather than concealing disagreement.

No improvement leaves the best untouched. Inspect the receipt, then supply a new
approach and a diagnosis:

```text
python scripts/loop_state.py begin --run ./loop_project --hypothesis "Parsing dominates lookup cost" --approach "Parse once per batch" --lesson "The benchmark showed unchanged lookup cost and repeated parsing"
```

After revert/inconclusive, the helper requires a nonempty lesson and changed approach.
The agent must make the change substantive; labels alone cannot enforce good reasoning.
There is no failure-count ceiling. Two measurements do not establish statistical
confidence; use the task's justified sampling when results are noisy.

## State and recovery

```text
loop_project/
  state.json                 Compact goal, best pointer, counters, pending attempt
  control/verifier.py        Frozen evaluator
  control/goal.json          Frozen target, check names, and declared limits
  baseline/                  Original source snapshot
  evidence/baseline/          Initial measurement
  attempts/000001/
    candidate/               Editable experiment
    confirmation/            Fresh verification copy
    version/                 Sealed snapshot if promoted
    evidence/                Raw and structured measurements
    result.json              Authoritative decision receipt
```

This is state format 2. Legacy instruction-only state/JSONL files are not silently
converted. Preserve them and start a separate directory, or continue their manual
workflow with explicit snapshots.

State uses atomic replacement and an OS writer lock; locks release when a process
exits. A decision receipt saved before a crash is reused on evaluate, without double
counting. Status exposes a pending candidate and best. Repeated evaluate after an
attempt returns that attempt's receipt. Unrecorded/partial snapshots stop for
inspection rather than deleting or guessing which work to retain. Changed
baseline/best/verifier bytes or goal contract block comparison. Saved best metrics
must match their authoritative measurement/receipt. Receipt recovery checks the
accepted snapshot before promotion, and the promoted copy's hash must match the
source bytes that were actually measured, including across a concurrent edit.

Per-attempt receipts are the history. Compact state avoids rereading a growing
ledger on every iteration. Versions/evidence are not automatically deleted. Disk
exhaustion is a real blocker, not permission to remove the baseline or user work.
Keep run directories private and out of Git. To deliver, integrate the best snapshot
with a reviewed diff into the requested target and verify the integrated behavior.
