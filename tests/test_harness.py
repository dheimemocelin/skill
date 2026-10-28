"""Real local execution and recovery tests; no LLM calls or external services."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from harness.context import ContextManager, relevant_context
from harness.model import HarnessError, TRANSITIONS, transition
from harness.orchestrator import Orchestrator
from harness.planner import normalize
from harness.router import route

ROOT = Path(__file__).resolve().parents[1]


def plan(action=None, **options):
    return {
        "steps": [{"id": "inspect", "action": action or {"kind": "fixture"}, **options}],
        "gates": [{"id": "done", "kind": "step_succeeded", "step": "inspect", "criterion": "Inspection finished"}],
    }


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.workspace = Path(self.directory.name).resolve()
        self.h = Orchestrator(self.workspace)

    def create(self, spec=None):
        return self.h.create("Inspect a synthetic fixture", spec or plan())

    def test_create_round_trip_and_schema(self):
        task = self.create()
        self.assertEqual(self.h.context.load(task["id"]), task)
        self.assertEqual(task["schema_version"], 1)
        self.assertEqual(task["state"], "pending")
        self.assertEqual(task["steps"]["inspect"]["attempts"], 0)

    def test_all_lifecycle_edges(self):
        for source in TRANSITIONS:
            for target in TRANSITIONS:
                with self.subTest(source=source, target=target):
                    task = {"state": source, "history": []}
                    if target in TRANSITIONS[source]:
                        transition(task, target)
                        self.assertEqual(task["state"], target)
                    else:
                        with self.assertRaises(HarnessError):
                            transition(task, target)
                        self.assertEqual(task["state"], source)

    def test_actual_deterministic_execution_and_retry_budget(self):
        task = self.create(plan({"kind": "fixture", "fail_until": 1}))
        final = self.h.run(task["id"])
        state = final["steps"]["inspect"]
        self.assertEqual(final["state"], "completed")
        self.assertEqual(state["attempts"], 2)
        self.assertEqual([r["ok"] for r in state["evidence"]], [False, True])
        self.assertTrue(all(r["synthetic"] for r in state["evidence"]))

    def test_attempt_budget_survives_resume(self):
        task = self.create(plan({"kind": "fixture", "fail_until": 5}, max_attempts=2))
        final = self.h.run(task["id"])
        self.assertEqual(final["state"], "failed")
        again = self.h.run(task["id"], resume=True)
        self.assertEqual(again["steps"]["inspect"]["attempts"], 2)
        self.assertEqual(again["state"], "failed")

    def test_failure_and_dependent_step_not_run(self):
        spec = plan({"kind": "fixture", "fail_until": 5}, max_attempts=1)
        spec["steps"].append({"id": "second", "action": {"kind": "fixture"}, "depends_on": ["inspect"]})
        final = self.h.run(self.create(spec)["id"])
        self.assertEqual(final["steps"]["second"]["attempts"], 0)

    def test_non_idempotent_failure_requires_single_use_confirmation(self):
        task = self.create(plan({"kind": "fixture", "fail_until": 2}, idempotent=False, max_attempts=3))
        blocked = self.h.run(task["id"])
        self.assertEqual(blocked["state"], "blocked")
        self.assertEqual(blocked["steps"]["inspect"]["attempts"], 1)
        blocked = self.h.run(task["id"], resume=True)
        self.assertEqual(blocked["steps"]["inspect"]["attempts"], 1)
        blocked = self.h.run(task["id"], resume=True, confirmed=["inspect"])
        self.assertEqual(blocked["state"], "blocked")
        self.assertEqual(blocked["steps"]["inspect"]["attempts"], 2)
        final = self.h.run(task["id"], resume=True, confirmed=["inspect"])
        self.assertEqual(final["state"], "completed")

    def test_real_timeout_is_recorded(self):
        task = self.create(plan({"kind": "fixture", "delay_seconds": 2}, timeout_seconds=0.1, max_attempts=1))
        final = self.h.run(task["id"])
        self.assertEqual(final["state"], "failed")
        self.assertEqual(final["steps"]["inspect"]["failure"], "timeout")

    def test_interrupt_has_checkpoint_and_resume_keeps_attempt(self):
        task = self.create(plan(idempotent=False))
        with patch.object(self.h.executor, "execute", side_effect=KeyboardInterrupt):
            interrupted = self.h.run(task["id"])
        self.assertEqual(interrupted["state"], "blocked")
        self.assertEqual(interrupted["steps"]["inspect"]["status"], "running")
        blocked = self.h.run(task["id"], resume=True)
        self.assertEqual(blocked["steps"]["inspect"]["attempts"], 1)
        final = self.h.run(task["id"], resume=True, confirmed=["inspect"])
        self.assertEqual(final["state"], "completed")

    def test_hard_interruption_inflight_checkpoint_recovers(self):
        task = self.create()
        with self.h.context.lock():
            transition(task, "planning")
            transition(task, "running")
            task["steps"]["inspect"].update(status="running", attempts=1)
            self.h.context.save(task)
        final = Orchestrator(self.workspace).run(task["id"], resume=True)
        self.assertEqual(final["state"], "completed")
        self.assertEqual(final["steps"]["inspect"]["attempts"], 2)

    def test_completed_steps_preserved_when_gate_fails_and_recovers(self):
        spec = plan()
        spec["gates"] = [{"id": "ready", "kind": "file_exists", "path": "ready.txt", "criterion": "Artifact exists"}]
        task = self.create(spec)
        failed = self.h.run(task["id"])
        self.assertEqual(failed["state"], "failed")
        (self.workspace / "ready.txt").write_text("ready", encoding="utf-8")
        final = self.h.run(task["id"], resume=True)
        self.assertEqual(final["state"], "completed")
        self.assertEqual(final["steps"], failed["steps"])

    def test_real_file_hash_gate_and_preservation(self):
        import hashlib
        content = b"Existing contributor work\n"
        (self.workspace / "work.txt").write_bytes(content)
        spec = plan({"kind": "file_exists", "path": "work.txt"})
        spec["gates"] = [{"id": "hash", "kind": "file_sha256", "path": "work.txt", "sha256": hashlib.sha256(content).hexdigest(), "criterion": "Original content preserved"}]
        final = self.h.run(self.create(spec)["id"])
        self.assertEqual(final["state"], "completed")
        self.assertEqual((self.workspace / "work.txt").read_bytes(), content)
        self.assertEqual(final["steps"]["inspect"]["evidence"][0]["executor"], "local-file")

    def test_tests_require_approval_and_use_real_exit_status(self):
        (self.workspace / "tests").mkdir()
        test_file = self.workspace / "tests" / "test_example.py"
        test_file.write_text("import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertEqual(1, 2)\n", encoding="utf-8")
        spec = plan()
        spec["gates"] = [{"id": "test", "kind": "tests", "suite": "unittest", "criterion": "Local suite passes"}]
        task = self.create(spec)
        self.assertEqual(self.h.run(task["id"])["state"], "blocked")
        failed = self.h.run(task["id"], resume=True, allow_tests=True)
        self.assertEqual(failed["state"], "failed")
        self.assertNotEqual(failed["gates"]["test"]["exit_code"], 0)
        test_file.write_text("import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertEqual(1, 1)\n", encoding="utf-8")
        final = self.h.run(task["id"], resume=True, allow_tests=True)
        self.assertEqual(final["state"], "completed")
        self.assertEqual(final["steps"]["inspect"]["attempts"], 1)

    def test_unavailable_review_is_blocked_not_faked(self):
        spec = plan()
        spec["gates"] = [{"id": "review", "kind": "review", "criterion": "Independent review"}]
        final = self.h.run(self.create(spec)["id"])
        self.assertEqual(final["state"], "blocked")
        refs = final["gates"]["review"]["references"]
        self.assertFalse(refs["agent_dispatched"])
        self.assertTrue(refs["agent"].endswith("quality-reviewer.md"))

    def test_corruption_never_silently_rolls_back_or_executes(self):
        task = self.create()
        self.h.note(task["id"], "Synthetic decision")
        path = self.h.context.path(task["id"])
        path.write_text('{"broken":', encoding="utf-8")
        with self.assertRaises(HarnessError):
            self.h.run(task["id"], resume=True)
        self.assertEqual(path.read_text(encoding="utf-8"), '{"broken":')
        with self.h.context.lock():
            restored = self.h.context.restore(task["id"])
        self.assertEqual(restored["state"], "blocked")
        self.assertEqual(len(list(self.h.context.root.glob("*.corrupt"))), 1)
        self.assertEqual(self.h.run(task["id"], resume=True)["state"], "completed")

    def test_partial_atomic_write_leaves_previous_checkpoint(self):
        task = self.create()
        before = self.h.context.path(task["id"]).read_bytes()
        with patch("harness.context.os.replace", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                self.h.note(task["id"], "New decision")
        self.assertEqual(self.h.context.path(task["id"]).read_bytes(), before)
        self.assertEqual(self.h.context.load(task["id"])["decisions"], [])

    def test_backup_restore_does_not_replay_uncertain_non_idempotent_step(self):
        task = self.create(plan(idempotent=False))
        with self.h.context.lock():
            transition(task, "planning")
            transition(task, "running")
            task["steps"]["inspect"].update(status="running", attempts=1)
            self.h.context.save(task)
            task["steps"]["inspect"].update(status="completed", evidence=[{"ok": True, "failure": None, "executor": "deterministic-fixture"}])
            self.h.context.save(task)
            self.h.context.path(task["id"]).write_text("broken", encoding="utf-8")
            self.h.context.restore(task["id"])
        blocked = self.h.run(task["id"], resume=True)
        self.assertEqual(blocked["state"], "blocked")
        self.assertEqual(blocked["steps"]["inspect"]["attempts"], 1)

    def test_executor_raw_output_is_not_persisted(self):
        task = self.create(plan(max_attempts=1))
        with patch.object(self.h.executor, "execute", return_value={"ok": True, "failure": None, "executor": "builtin", "stdout": "PRIVATE_VALUE"}):
            final = self.h.run(task["id"])
        self.assertEqual(final["state"], "failed")
        self.assertNotIn("PRIVATE_VALUE", self.h.context.path(task["id"]).read_text(encoding="utf-8"))

    def test_backup_before_start_still_requires_confirmation_and_charges_attempt(self):
        task = self.create(plan(idempotent=False))
        with self.h.context.lock():
            transition(task, "planning")
            transition(task, "running")
            self.h.context.save(task)
            task["steps"]["inspect"].update(status="running", attempts=1)
            self.h.context.save(task)
            self.h.context.path(task["id"]).write_text("broken", encoding="utf-8")
            self.h.context.restore(task["id"])
        blocked = self.h.run(task["id"], resume=True)
        self.assertEqual(blocked["state"], "blocked")
        self.assertEqual(blocked["steps"]["inspect"]["attempts"], 1)
        self.assertEqual(self.h.run(task["id"], resume=True, confirmed=["inspect"])["state"], "completed")

    def test_malformed_state_and_schema_rejected_even_with_checksum(self):
        from harness.context import encoded
        import hashlib
        task = self.create()
        for change in ({"schema_version": 99}, {"state": "completed"}, {"steps": {}}):
            bad = {**task, **change}
            envelope = {"sha256": hashlib.sha256(encoded(bad)).hexdigest(), "task": bad}
            self.h.context.path(task["id"]).write_text(json.dumps(envelope), encoding="utf-8")
            with self.assertRaises(HarnessError):
                self.h.context.load(task["id"])

    def test_lock_excludes_other_process_and_releases_after_exit(self):
        code = "from harness.context import ContextManager; from pathlib import Path; import sys\nwith ContextManager(Path(sys.argv[1])).lock(): print('acquired')"
        with self.h.context.lock():
            other = subprocess.run([sys.executable, "-c", code, str(self.workspace)], cwd=ROOT, capture_output=True, timeout=10)
            self.assertNotEqual(other.returncode, 0)
        other = subprocess.run([sys.executable, "-c", code, str(self.workspace)], cwd=ROOT, capture_output=True, timeout=10)
        self.assertEqual(other.returncode, 0, other.stderr)

    def test_plan_rejects_cycle_unsafe_command_path_and_unknown_provider(self):
        bad = [plan({"kind": "shell", "command": "git merge main"}), plan({"kind": "codex"}), plan({"kind": "file_exists", "path": "../private"}), plan(depends_on=["inspect"]), plan(max_attempts=0), plan(skills=["unknown"])]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(HarnessError):
                normalize(value)

    def test_credentials_and_path_traversal_not_persisted(self):
        with self.assertRaises(HarnessError):
            self.h.create("api_key=do-not-store-me", plan())
        self.assertEqual(list(self.h.context.root.glob("*.json")), [])
        with self.assertRaises(HarnessError):
            self.h.context.load("../outside")

    def test_router_reuses_canonical_mapping_without_loading_bodies(self):
        refs = route([], "ai-engineer")
        from scripts.build_agent_adapters import parse_agent
        metadata, _ = parse_agent(ROOT / "agents" / "ai-engineer.md")
        self.assertEqual(set(refs["skills"]), set(metadata["skills"]))
        self.assertFalse(refs["agent_dispatched"])
        self.assertEqual(route([])["skills"], {})

    def test_context_omits_history_and_limits_decisions(self):
        task = self.create()
        task["decisions"] = [f"Decision {i}" for i in range(12)]
        context = relevant_context(task, task["plan"]["steps"][0])
        self.assertNotIn("history", context)
        self.assertEqual(len(context["decisions"]), 5)

    def test_cancel_terminal_and_cli_round_trip(self):
        task = self.create()
        self.h.cancel(task["id"])
        with self.assertRaises(HarnessError):
            self.h.run(task["id"], resume=True)
        manifest = self.workspace / "plan.json"
        manifest.write_text(json.dumps(plan()), encoding="utf-8")
        prefix = [sys.executable, "-m", "harness", "--workspace", str(self.workspace)]
        created = subprocess.run(prefix + ["create", "CLI fixture", "--plan", str(manifest)], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(created.returncode, 0, created.stderr)
        tid = json.loads(created.stdout)["id"]
        result = subprocess.run(prefix + ["run", tid], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "completed")
        for command in ("status", "history", "evidence"):
            result = subprocess.run(prefix + [command, tid], cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
