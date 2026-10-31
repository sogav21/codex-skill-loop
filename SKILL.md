---
name: loop
description: Iteratively complete a task or improve a measurable result with /loop or $loop, preserving the best verified version and changing approach after failed experiments.
---

# Loop

## Define and preserve

Establish the requested outcome, editable scope, observable acceptance checks,
verification, and explicit user limits. Research additionally needs a metric,
direction, target, and meaningful delta. Infer available facts; ask only for
missing information that changes correctness. Freeze this compact goal card and
the evaluator. A different goal starts a new run with existing evidence preserved.

Inspect current work. Copy the actual starting version, including relevant
uncommitted files, into an unchanged baseline and measure it. Maintain a separate
best verified version; each experiment starts from that best.

For repeated or resumable work, use `scripts/loop_state.py`. Read
[runtime.md](references/runtime.md) when initializing or resuming it for commands,
verifier output, state, and recovery. The helper enforces version selection;
the agent chooses hypotheses and writes changes. Keep run data private.
Without Python, implement the same snapshot/evidence contract manually and
disclose that enforcement is manual.

## One experiment

1. **Resume:** load the goal, best, pending candidate, and last evidence. Continue
   an interrupted candidate instead of creating a competing copy.
2. **Hypothesize:** choose one coherent change addressing the remaining gap.
   After failure or inconclusive evidence, record what happened, the likely cause,
   and a genuinely different approach. Relabeling the same action is not a strategy.
3. **Copy and change:** create a candidate from the best and edit there. Preserve
   the original, accepted versions, and rejected candidates for inspection.
4. **Measure:** run the fixed evaluator on the real candidate. Save version identity,
   command, exit status, raw output, checks, and metrics. Crashing, malformed,
   missing, or source-mutating evaluation is inconclusive.
5. **Compare:** retain only meaningful improvement without regressing passing checks,
   guards, or the declared metric. Reproduce a proposed promotion in a fresh copy.
   Otherwise retain the best and diagnose. Keep useful lessons from rejected work.
6. **Persist and repeat:** save the decision, evidence, best pointer, counters, and
   next step before continuing. Success requires every acceptance condition and
   numeric target, when present, with fresh confirmation.

Decisions: `keep` = confirmed progress below the goal; `pass` = confirmed goal;
`revert` = rejected/no improvement; `inconclusive` = unreliable evidence.
The best stays unchanged on rejection. Keep targets and checks fixed rather than
weaken them to manufacture a win. For noise, use justified sampling and minimum
meaningful delta; two measurements alone do not establish statistical confidence.

## Continue toward the goal

The default attempt limit is **none**. A plateau, rejected experiment, or empty
hypothesis queue requires investigation and another approach, not an automatic
failure-count stop. Avoid unchanged retries.

Stop for verified success, a user limit/stop request, or a concrete blocker
unresolvable within authorized scope: missing permission/input/tool/resource or
incompatible requirements. Preserve state, identify the prerequisite, and report
the goal as incomplete. A plateau is not success or broader authorization.

Continue while the execution environment permits meaningful work. Persist an exact
resume point before a context/runtime interruption. The next invocation resumes
it; the skill cannot guarantee infinite uptime or an achievable goal. Background
scheduling needs separate authorization and a supported mechanism.

## Deliver

Report goal status, baseline -> best, verification, attempt/decision counts, limit
or `none`, best-version path, and stop reason. Integrate the best into the requested
target with a reviewed narrow diff, preserving unrelated/concurrent work. Verify
the integrated behavior before claiming delivery. Snapshots alone are not the
deliverable. Commit, push, publish, and merge require authorization; a requested
merge-on-success follows verified success.
