"""Persistent baseline/candidate/best loop. Python standard library only."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

IGNORED = {".git", "__pycache__", ".pytest_cache"}
CONTRACT_FIELDS = ("goal", "mode", "metric", "direction", "target", "min_delta",
                   "max_attempts", "timeout_seconds", "check_names", "guard_names",
                   "source", "baseline_hash", "verifier_sha256")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(folder):
    result = hashlib.sha256()
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder)
        if any(part in IGNORED for part in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError("Symlinks are outside the snapshot contract")
        if path.is_file():
            result.update(rel.as_posix().encode() + b"\0" + bytes.fromhex(digest(path)))
    return result.hexdigest()


def copy_version(source, destination):
    expected = fingerprint(source)
    shutil.copytree(source, destination,
                    ignore=lambda _folder, names: [name for name in names if name in IGNORED])
    if fingerprint(destination) != expected:
        raise ValueError("Snapshot changed while copying; original source was preserved")
    return expected


@contextmanager
def writer_lock(run):
    # OS locks release on process death; a crash cannot leave a permanent lock.
    with (run / ".writer.lock").open("a+b") as handle:
        handle.seek(0)
        if not handle.read(1):
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError("Another process owns this run; inspect status after it finishes") from error
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def load(run):
    state = read(run / "state.json")
    if state.get("schema_version") != 2:
        raise ValueError("Unknown state format; preserve legacy state and use a new run directory")
    contract = read(run / "control/goal.json")
    if digest(run / "control/goal.json") != state["contract_sha256"] or contract != {
            key: state[key] for key in CONTRACT_FIELDS}:
        raise ValueError("Frozen goal contract changed; restore it or start a separately authorized run")
    if digest(run / "control/verifier.py") != state["verifier_sha256"]:
        raise ValueError("Frozen verifier changed; restore its original bytes before resuming")
    if fingerprint(run / "baseline") != state["baseline_hash"]:
        raise ValueError("Immutable baseline changed; restore it before resuming")
    if fingerprint(run / state["best"]) != state["best_hash"]:
        raise ValueError("Verified best version changed; restore it before resuming")
    baseline_evidence = read(run / "evidence/baseline/measurement.json")
    if baseline_evidence != state["baseline_evaluation"] or baseline_evidence.get("source_hash") != state["baseline_hash"]:
        raise ValueError("Baseline measurement no longer matches its saved evidence")
    if state["best"] == "baseline":
        best_evidence = baseline_evidence
    else:
        parts = Path(state["best"]).parts
        if len(parts) != 3 or parts[0] != "attempts" or parts[2] != "version" or not parts[1].isdigit():
            raise ValueError("Best pointer is not an accepted attempt version")
        receipt = read(run / "attempts" / parts[1] / "result.json")
        verify_promotion(run, state, receipt)
        if receipt["new_best"] != state["best"] or receipt["candidate_hash"] != state["best_hash"]:
            raise ValueError("Best pointer no longer matches its decision receipt")
        best_evidence = receipt["evaluation"]
    if best_evidence != state["best_evaluation"]:
        raise ValueError("Best measurement no longer matches its authoritative evidence")
    if state["status"] == "success" and not goal_met(best_evidence, state):
        raise ValueError("Saved success status is unsupported by the verified best")
    return state


def validate(value, state):
    if not isinstance(value, dict):
        raise ValueError("Verifier must return a JSON object")
    checks, guards, metrics = (value.get(key, {}) for key in ("checks", "guards", "metrics"))
    if not isinstance(checks, dict) or not checks or not all(type(v) is bool for v in checks.values()):
        raise ValueError("checks must be a nonempty object of booleans")
    if not isinstance(guards, dict) or not all(type(v) is bool for v in guards.values()):
        raise ValueError("guards must be an object of booleans")
    if not isinstance(metrics, dict) or not all(type(v) in (int, float) and math.isfinite(v) for v in metrics.values()):
        raise ValueError("metrics must contain finite numbers, not booleans")
    if "check_names" in state and (set(checks) != set(state["check_names"]) or set(guards) != set(state["guard_names"])):
        raise ValueError("Acceptance checks or guards changed from the baseline contract")
    if state["metric"] and state["metric"] not in metrics:
        raise ValueError("Declared metric missing from verifier output")
    return {"checks": checks, "guards": guards, "metrics": metrics}


def measure(run, workspace, evidence, state):
    evidence.mkdir(parents=True, exist_ok=True)
    result = {"valid": False, "started_at": datetime.now(timezone.utc).isoformat()}
    try:
        before = fingerprint(workspace)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        command = [sys.executable, "-B", str(run / "control/verifier.py")]
        result.update(command=command, source_hash=before)
        process = subprocess.run(command, cwd=workspace, env=env, capture_output=True,
                                 timeout=state["timeout_seconds"])
        (evidence / "stdout.txt").write_bytes(process.stdout)
        (evidence / "stderr.txt").write_bytes(process.stderr)
        result["exit_code"] = process.returncode
        if fingerprint(workspace) != before:
            raise ValueError("Verifier changed candidate source; result is not admissible")
        if digest(run / "control/verifier.py") != state["verifier_sha256"]:
            raise ValueError("Frozen verifier changed during execution")
        if process.returncode:
            raise ValueError("Verifier failed; inspect the saved stderr")
        result.update(validate(json.loads(process.stdout.decode("utf-8")), state))
        result["valid"] = True
    except subprocess.TimeoutExpired as error:
        (evidence / "stdout.txt").write_bytes(error.stdout or b"")
        (evidence / "stderr.txt").write_bytes(error.stderr or b"")
        result["error"] = "Explicit verification timeout exhausted; partial output preserved"
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        result["error"] = str(error)
    save(evidence / "measurement.json", result)
    return result


def goal_met(value, state):
    if not value["valid"] or not all(value["checks"].values()) or not all(value["guards"].values()):
        return False
    if state["metric"] is None:
        return True
    score = value["metrics"][state["metric"]]
    return score >= state["target"] if state["direction"] == "higher" else score <= state["target"]


def compare(value, best, state):
    if not value["valid"] or not all(value["guards"].values()):
        failed = [key for key, passed in value.get("guards", {}).items() if not passed]
        return False, "Guard failure: " + ", ".join(failed)
    regressed = [key for key, passed in best["checks"].items() if passed and not value["checks"][key]]
    if regressed:
        return False, "Previously passing checks regressed: " + ", ".join(regressed)
    gain = 0
    if state["metric"]:
        gain = value["metrics"][state["metric"]] - best["metrics"][state["metric"]]
        if state["direction"] == "lower":
            gain = -gain
        if gain < 0:
            return False, "Declared metric regressed against the best"
    better = (goal_met(value, state) or
            sum(value["checks"].values()) > sum(best["checks"].values()) or
            not all(best["guards"].values()) or
            (gain > 0 and gain >= state["min_delta"]))
    return better, "Measured improvement" if better else "No meaningful improvement against the best"


def verify_promotion(run, state, receipt):
    relative = f"attempts/{receipt['number']:06d}"
    if receipt["new_best"] != relative + "/version" or receipt["receipt"] != relative + "/result.json":
        raise ValueError("Promotion receipt points outside its recorded attempt")
    value = receipt["evaluation"]
    validate(value, state)
    if not value["valid"] or not all(value["guards"].values()):
        raise ValueError("Promotion has no valid guard-preserving evidence")
    if value.get("source_hash") != receipt["candidate_hash"]:
        raise ValueError("Promotion measurement is not bound to the accepted source")
    if fingerprint(run / receipt["new_best"]) != receipt["candidate_hash"]:
        raise ValueError("Promoted snapshot changed before receipt recovery")
    if receipt["result"] not in {"keep", "pass"}:
        raise ValueError("Best receipt does not record an accepted version")
    if receipt["result"] == "pass" and not goal_met(value, state):
        raise ValueError("Promotion claims success below the frozen goal")


def initialize(args, run):
    source, verifier = args.source.resolve(), args.verifier.resolve()
    if not source.is_dir() or not verifier.is_file():
        raise ValueError("Source directory and verifier file must exist")
    if source == run or source in run.parents or run in source.parents:
        raise ValueError("Source and run directories must be disjoint")
    if verifier == run or run in verifier.parents:
        raise ValueError("Verifier must exist outside the new run directory")
    if args.metric and (args.direction is None or args.target is None):
        raise ValueError("Research requires metric, direction, and numeric target")
    if not args.metric and (args.direction is not None or args.target is not None):
        raise ValueError("Metric, direction, and target must be specified together")
    if not args.goal.strip() or args.min_delta < 0 or not math.isfinite(args.min_delta):
        raise ValueError("A concrete goal and finite nonnegative min-delta are required")
    if args.target is not None and not math.isfinite(args.target):
        raise ValueError("Target must be finite")
    if args.max_attempts is not None and args.max_attempts < 1:
        raise ValueError("Explicit max-attempts must be positive")
    if args.timeout_seconds is not None and args.timeout_seconds <= 0:
        raise ValueError("Explicit timeout must be positive")
    run.mkdir(parents=True, exist_ok=False)
    with writer_lock(run):
        (run / "control").mkdir()
        shutil.copy2(verifier, run / "control/verifier.py")
        baseline_hash = copy_version(source, run / "baseline")
        state = {"schema_version": 2, "goal": args.goal, "mode": "research" if args.metric else "completion",
                 "metric": args.metric, "direction": args.direction, "target": args.target,
                 "min_delta": args.min_delta, "max_attempts": args.max_attempts,
                 "timeout_seconds": args.timeout_seconds, "source": str(source),
                 "verifier_sha256": digest(run / "control/verifier.py"), "baseline_hash": baseline_hash,
                 "best": "baseline", "best_hash": baseline_hash, "attempt": 0,
                 "kept": 0, "reverted": 0, "inconclusive": 0, "active": None,
                 "candidate": None, "last_result": None, "status": "running"}
        copy_version(run / "baseline", run / "baseline-check")
        baseline = measure(run, run / "baseline-check", run / "evidence/baseline", state)
        if not baseline["valid"]:
            raise ValueError("Baseline verification is invalid; evidence and original snapshot were preserved")
        state.update(check_names=list(baseline["checks"]), guard_names=list(baseline["guards"]),
                     baseline_evaluation=baseline, best_evaluation=baseline)
        if goal_met(baseline, state):
            copy_version(run / "baseline", run / "baseline-confirm")
            confirmation = measure(run, run / "baseline-confirm", run / "evidence/baseline-confirm", state)
            if goal_met(confirmation, state):
                state["status"] = "success"
            else:
                raise ValueError("Baseline goal result did not reproduce; inspect evidence before starting a new run")
        save(run / "control/goal.json", {key: state[key] for key in CONTRACT_FIELDS})
        state["contract_sha256"] = digest(run / "control/goal.json")
        save(run / "state.json", state)
        return state


def begin(args, run, state):
    if state["active"]:
        return state  # Recover the already-created candidate after interruption.
    if state["status"] != "running":
        return state
    if state["max_attempts"] is not None and state["attempt"] >= state["max_attempts"]:
        state["status"] = "budget_exhausted"
        save(run / "state.json", state)
        return state
    if not args.hypothesis.strip() or not args.approach.strip():
        raise ValueError("A hypothesis and approach are required")
    if state["last_result"]:
        previous = read(run / state["last_result"])
        if previous["result"] in {"revert", "inconclusive"}:
            if not args.lesson.strip() or args.approach.strip() == previous["approach"]:
                raise ValueError("Diagnose the failed evidence and change approach before the next attempt")
    number = state["attempt"] + 1
    relative = f"attempts/{number:06d}"
    folder = run / relative
    # A completed snapshot may exist if the process died before state was saved.
    if folder.exists():
        raise ValueError("Unrecorded attempt directory exists; inspect it before recovery")
    folder.mkdir(parents=True)
    copy_version(run / state["best"], folder / "candidate")
    active = {"number": number, "folder": relative, "hypothesis": args.hypothesis,
              "approach": args.approach.strip(), "lesson": args.lesson}
    state.update(attempt=number, active=active, candidate=str(folder / "candidate"))
    save(run / "state.json", state)
    return state


def finalize(run, state, receipt):
    if state["active"] is None:
        return receipt
    result = receipt["result"]
    if result in {"keep", "pass"}:
        verify_promotion(run, state, receipt)
        state.update(best=receipt["new_best"], best_hash=receipt["candidate_hash"],
                     best_evaluation=receipt["evaluation"], kept=state["kept"] + 1)
    else:
        key = "reverted" if result == "revert" else "inconclusive"
        state[key] += 1
    state.update(active=None, candidate=None, last_result=receipt["receipt"],
                 status="success" if result == "pass" else "running")
    save(run / "state.json", state)
    return receipt


def evaluate(run, state):
    if not state["active"]:
        if state["last_result"]:
            return read(run / state["last_result"])
        raise ValueError("No candidate is pending")
    active = state["active"]
    folder = run / active["folder"]
    receipt_path = folder / "result.json"
    if receipt_path.exists():
        return finalize(run, state, read(receipt_path))
    receipt = {**active, "result": "revert", "reason": "No candidate source change was made",
               "receipt": f"{active['folder']}/result.json", "previous_best": state["best"],
               "evidence": {}}
    try:
        candidate_hash = fingerprint(folder / "candidate")
        receipt["candidate_hash"] = candidate_hash
        if candidate_hash != state["best_hash"]:
            receipt["evidence"]["first"] = f"{active['folder']}/evidence/first"
            first = measure(run, folder / "candidate", run / receipt["evidence"]["first"], state)
            receipt["evaluation"] = first
            if not first["valid"]:
                receipt.update(result="inconclusive", reason=first["error"])
            elif not compare(first, state["best_evaluation"], state)[0]:
                receipt["reason"] = compare(first, state["best_evaluation"], state)[1]
            else:
                # Verify proposed promotions in a fresh copy before accepting them.
                copy_version(folder / "candidate", folder / "confirmation")
                receipt["evidence"]["confirmation"] = f"{active['folder']}/evidence/confirmation"
                second = measure(run, folder / "confirmation", run / receipt["evidence"]["confirmation"], state)
                if not second["valid"] or not compare(second, state["best_evaluation"], state)[0]:
                    receipt.update(result="inconclusive", reason="Improvement did not reproduce in a fresh copy")
                else:
                    combined = json.loads(json.dumps(second))
                    combined["checks"] = {key: first["checks"][key] and second["checks"][key] for key in state["check_names"]}
                    if state["metric"]:
                        key = state["metric"]
                        conservative = min if state["direction"] == "higher" else max
                        combined["metrics"][key] = conservative(first["metrics"][key], second["metrics"][key])
                    if not compare(combined, state["best_evaluation"], state)[0]:
                        receipt.update(result="inconclusive", reason="Combined evidence does not show improvement")
                    else:
                        copied_hash = copy_version(folder / "candidate", folder / "version")
                        if copied_hash != candidate_hash:
                            raise ValueError("Candidate changed after measurement; promotion is inconclusive")
                        receipt.update(result="pass" if goal_met(combined, state) else "keep",
                                       reason="Improvement reproduced without a guard/check regression",
                                       new_best=f"{active['folder']}/version", candidate_hash=candidate_hash,
                                       evaluation=combined)
    except (ValueError, OSError) as error:
        receipt.update(result="inconclusive", reason=str(error))
    save(receipt_path, receipt)  # Durable receipt makes state recovery idempotent.
    return finalize(run, state, receipt)


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--source", type=Path, required=True)
    init.add_argument("--goal", required=True)
    init.add_argument("--verifier", type=Path, required=True)
    init.add_argument("--metric")
    init.add_argument("--direction", choices=["higher", "lower"])
    init.add_argument("--target", type=float)
    init.add_argument("--min-delta", type=float, default=0)
    init.add_argument("--max-attempts", type=int)
    init.add_argument("--timeout-seconds", type=float)
    candidate = commands.add_parser("begin")
    candidate.add_argument("--hypothesis", required=True)
    candidate.add_argument("--approach", required=True)
    candidate.add_argument("--lesson", default="")
    commands.add_parser("evaluate")
    commands.add_parser("status")
    for command in commands.choices.values():
        command.add_argument("--run", type=Path, required=True)
    return root


def main():
    args = parser().parse_args()
    run = args.run.resolve()
    try:
        if args.command == "init":
            result = initialize(args, run)
        else:
            with writer_lock(run):
                state = load(run)
                if args.command == "begin":
                    result = begin(args, run, state)
                elif args.command == "evaluate":
                    result = evaluate(run, state)
                else:
                    result = state
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
