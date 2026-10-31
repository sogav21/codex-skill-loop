"""Real subprocess checks using a synthetic local product and verifier."""
import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/loop_state.py"
VERIFIER = '''import json
from pathlib import Path
d = json.loads(Path("product.json").read_text())
if d.get("crash"):
    raise RuntimeError("synthetic verification failure")
if d.get("mutate"):
    Path("product.json").write_text('{"score":999,"safe":true,"ready":true}')
if d.get("malformed"):
    print("not JSON")
else:
    checks = {"replacement":True} if d.get("rename") else {"ready":d.get("ready",True)}
    print(json.dumps({"checks":checks,
                      "guards":{"safe":d.get("safe",True)},
                      "metrics":{"score":d["score"]}}))
'''


class LoopStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="loop-state-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        self.write(self.source, score=0)
        self.verifier = self.root / "verifier.py"
        self.verifier.write_text(VERIFIER, encoding="utf-8")
        self.run_dir = self.root / "run"

    def write(self, folder, **data):
        (folder / "product.json").write_text(json.dumps(data), encoding="utf-8")

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                                text=True, capture_output=True, encoding="utf-8")
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0)
        return json.loads(result.stdout)

    def init(self, target=3, direction="higher", extra=()):
        return self.cli("init", "--source", self.source, "--run", self.run_dir,
                        "--goal", "Reach the declared synthetic score without losing validity",
                        "--verifier", self.verifier, "--metric", "score", "--direction",
                        direction, "--target", target, *extra)

    def state(self):
        return self.cli("status", "--run", self.run_dir)

    def begin(self, n=1, **kwargs):
        return self.cli("begin", "--run", self.run_dir, "--hypothesis", f"hypothesis {n}",
                        "--approach", kwargs.get("approach", f"approach {n}"),
                        "--lesson", kwargs.get("lesson", ""))

    def evaluate(self):
        return self.cli("evaluate", "--run", self.run_dir)

    def candidate(self):
        return Path(self.state()["candidate"])

    def test_improvement_is_promoted_and_original_is_preserved(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=1)
        result = self.evaluate()
        self.assertEqual(result["result"], "keep")
        self.assertEqual(self.state()["best_evaluation"]["metrics"]["score"], 1)
        self.assertEqual(json.loads((self.source / "product.json").read_text())["score"], 0)
        self.assertEqual(json.loads((self.run_dir / "baseline/product.json").read_text())["score"], 0)
        self.assertTrue((self.run_dir / result["evidence"]["confirmation"] / "stdout.txt").exists())

    def test_regression_keeps_best_and_next_copy_comes_from_best(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=1)
        self.evaluate()
        self.begin(2)
        self.write(self.candidate(), score=-1)
        self.assertEqual(self.evaluate()["result"], "revert")
        self.begin(3, lesson="The evidence rejects lowering the score")
        self.assertEqual(json.loads((self.candidate() / "product.json").read_text())["score"], 1)

    def test_no_improvement_requires_diagnosis_and_changed_approach(self):
        self.init()
        self.begin()
        self.assertEqual(self.evaluate()["result"], "revert")
        self.cli("begin", "--run", self.run_dir, "--hypothesis", "new",
                 "--approach", "approach 1", "--lesson", "No candidate change", ok=False)
        self.cli("begin", "--run", self.run_dir, "--hypothesis", "new",
                 "--approach", "different", ok=False)
        self.begin(2, lesson="No product change was tested; use a different implementation")

    def test_guard_failure_cannot_win_even_with_better_score(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=100, safe=False)
        self.assertEqual(self.evaluate()["result"], "revert")
        self.assertEqual(self.state()["best_evaluation"]["metrics"]["score"], 0)

    def test_goal_requires_checks_and_confirmed_real_measurement(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=3, ready=False)
        self.assertEqual(self.evaluate()["result"], "revert")
        self.begin(2, lesson="A target score does not excuse losing a passing check")
        self.write(self.candidate(), score=3)
        self.assertEqual(self.evaluate()["result"], "pass")
        self.assertEqual(self.state()["status"], "success")

    def test_no_default_iteration_limit(self):
        self.init(target=32)
        for n in range(1, 33):
            self.begin(n)
            self.write(self.candidate(), score=n)
            self.evaluate()
        state = self.state()
        self.assertEqual(state["attempt"], 32)
        self.assertIsNone(state["max_attempts"])
        self.assertEqual(state["status"], "success")

    def test_explicit_budget_is_honored(self):
        self.init(extra=("--max-attempts", 1))
        self.begin()
        self.write(self.candidate(), score=1)
        self.evaluate()
        result = self.begin(2)
        self.assertEqual(result["status"], "budget_exhausted")
        self.assertIsNone(result["candidate"])

    def test_lower_metric_direction(self):
        self.write(self.source, score=10)
        self.init(target=8, direction="lower")
        self.begin()
        self.write(self.candidate(), score=8)
        self.assertEqual(self.evaluate()["result"], "pass")

    def test_resume_pending_candidate_and_idempotent_evaluation(self):
        self.init()
        first = self.begin()
        self.assertEqual(self.state()["candidate"], first["candidate"])
        self.write(Path(first["candidate"]), score=1)
        receipt = self.evaluate()
        self.assertEqual(self.evaluate(), receipt)
        self.assertEqual(self.state()["kept"], 1)

    def test_crash_or_malformed_output_is_inconclusive(self):
        for field in ("crash", "malformed"):
            with self.subTest(field=field):
                if not self.run_dir.exists():
                    self.init()
                n = self.state()["attempt"] + 1
                self.begin(n, lesson="Previous verifier output was invalid" if n > 1 else "")
                self.write(self.candidate(), score=3, **{field: True})
                self.assertEqual(self.evaluate()["result"], "inconclusive")
                self.assertEqual(self.state()["best_evaluation"]["metrics"]["score"], 0)

    def test_verifier_mutating_candidate_cannot_promote(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=3, mutate=True)
        self.assertEqual(self.evaluate()["result"], "inconclusive")
        self.assertEqual(self.state()["best_evaluation"]["metrics"]["score"], 0)

    def test_immutable_baseline_tampering_is_rejected(self):
        self.init()
        self.write(self.run_dir / "baseline", score=100)
        self.cli("status", "--run", self.run_dir, ok=False)

    def test_frozen_verifier_tampering_is_rejected(self):
        self.init()
        (self.run_dir / "control/verifier.py").write_text("print('{}')", encoding="utf-8")
        self.cli("status", "--run", self.run_dir, ok=False)

    def test_target_cannot_be_weakened_in_saved_state(self):
        self.init()
        path = self.run_dir / "state.json"
        state = json.loads(path.read_text())
        state["target"] = 0
        path.write_text(json.dumps(state))
        self.cli("status", "--run", self.run_dir, ok=False)

    def test_multiple_failed_experiments_do_not_impose_a_hidden_limit(self):
        self.init()
        for n in range(1, 5):
            self.begin(n, lesson="The evidence showed no gain; test another mechanism" if n > 1 else "")
            self.write(self.candidate(), score=-n)
            self.assertEqual(self.evaluate()["result"], "revert")
        self.begin(5, lesson="Negative adjustments regress; use the valid correction")
        self.write(self.candidate(), score=3)
        self.assertEqual(self.evaluate()["result"], "pass")

    def test_completion_checklist_without_a_numeric_metric(self):
        self.write(self.source, score=0, ready=False)
        self.cli("init", "--source", self.source, "--run", self.run_dir,
                 "--goal", "Make readiness pass without breaking safety", "--verifier", self.verifier)
        self.begin()
        self.write(self.candidate(), score=0, ready=True)
        self.assertEqual(self.evaluate()["result"], "pass")

    def test_meaningful_delta_is_required_for_metric_only_progress(self):
        self.init(extra=("--min-delta", 1))
        self.begin()
        self.write(self.candidate(), score=0.1)
        self.assertEqual(self.evaluate()["result"], "revert")

    def test_renaming_or_dropping_acceptance_checks_is_inconclusive(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=3, rename=True)
        self.assertEqual(self.evaluate()["result"], "inconclusive")

    def test_nonfinite_metric_is_inconclusive(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=float("nan"))
        self.assertEqual(self.evaluate()["result"], "inconclusive")

    def test_rejected_receipt_has_real_evidence_and_specific_reason(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=100, safe=False)
        receipt = self.evaluate()
        self.assertIn("safe", receipt["reason"])
        self.assertNotIn("confirmation", receipt["evidence"])
        for path in receipt["evidence"].values():
            self.assertTrue((self.run_dir / path / "measurement.json").is_file())

    def test_saved_receipt_recovers_after_state_update_interruption(self):
        self.init()
        self.begin()
        pending = (self.run_dir / "state.json").read_bytes()
        self.write(self.candidate(), score=1)
        receipt = self.evaluate()
        # Reproduce a crash after receipt persistence but before atomic state update.
        (self.run_dir / "state.json").write_bytes(pending)
        self.assertEqual(self.evaluate(), receipt)
        self.assertEqual(self.state()["kept"], 1)

    def test_corrupted_promoted_snapshot_is_rejected_during_receipt_recovery(self):
        self.init()
        self.begin()
        pending = (self.run_dir / "state.json").read_bytes()
        self.write(self.candidate(), score=3)
        receipt = self.evaluate()
        self.write(self.run_dir / receipt["new_best"], score=0)
        (self.run_dir / "state.json").write_bytes(pending)
        self.cli("evaluate", "--run", self.run_dir, ok=False)

    def test_best_measurement_cannot_be_rewritten_in_state(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=1)
        self.evaluate()
        path = self.run_dir / "state.json"
        value = json.loads(path.read_text())
        value["best_evaluation"]["metrics"]["score"] = 0
        path.write_text(json.dumps(value))
        self.cli("status", "--run", self.run_dir, ok=False)

    def test_candidate_change_at_promotion_cannot_report_a_pass(self):
        self.init()
        self.begin()
        self.write(self.candidate(), score=3)
        spec = importlib.util.spec_from_file_location("loop_runtime_test", SCRIPT)
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        original_copy = runtime.copy_version

        def concurrent_change(source, destination):
            if destination.name == "version":
                self.write(source, score=0)
            return original_copy(source, destination)

        with mock.patch.object(runtime, "copy_version", side_effect=concurrent_change):
            result = runtime.evaluate(self.run_dir, runtime.load(self.run_dir))
        self.assertEqual(result["result"], "inconclusive")
        self.assertEqual(self.state()["best_evaluation"]["metrics"]["score"], 0)

    def test_source_and_run_must_be_separate(self):
        self.cli("init", "--source", self.source, "--run", self.source / "loop_project",
                 "--goal", "synthetic", "--verifier", self.verifier, ok=False)


if __name__ == "__main__":
    unittest.main()
