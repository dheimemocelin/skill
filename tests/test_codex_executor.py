"""Unit fixtures only: these tests never invoke a paid provider."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from harness.codex import CodexExecutor
from harness.execution import validate_result
from harness.model import HarnessError
from harness.orchestrator import Orchestrator
from harness.planner import normalize


def plan(**options):
    return {"steps": [{"id": "inspect", "action": {"kind": "codex", "prompt": "Inspect sample.txt"},
                       "timeout_seconds": 120, **options}],
            "gates": [{"id": "exists", "kind": "file_exists", "path": "sample.txt", "criterion": "File preserved"}]}


def evidence(**updates):
    return {"ok": True, "failure": None, "executor": "codex-cli", "exit_code": 0,
            "turn_completed": True, "termination_confirmed": True, "uncertain": False, **updates}


class CodexExecutorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / "sample.txt").write_text("preserve contributor work")
        self.h = Orchestrator(self.root)

    def test_permission_and_unavailable_do_not_consume_attempt(self):
        task = self.h.create("Read a fixture", plan())
        with patch("harness.codex.CodexExecutor.execute") as execute:
            final = self.h.run(task["id"])
            self.assertEqual(final["state"], "blocked")
            with patch("harness.codex.resolve_cli", return_value=None):
                final = self.h.run(task["id"], resume=True, allow_codex=True)
            self.assertEqual(final["steps"]["inspect"]["attempts"], 0)
            execute.assert_not_called()

    def test_no_shell_entrypoint_and_project_config_blocked(self):
        (self.root / "codex.cmd").write_text("do not execute")
        from harness.codex import resolve_cli
        self.assertIsNone(resolve_cli(self.root / "codex.cmd"))
        (self.root / ".codex").mkdir()
        (self.root / ".codex" / "config.toml").write_text("# unreviewed MCP/hooks")
        with patch("harness.codex.resolve_cli", return_value=["codex"]):
            self.assertEqual(CodexExecutor().preflight(self.root), "codex_project_config_requires_isolation")

    def test_v1_unchanged_and_codex_non_idempotent(self):
        normalized = normalize(plan())
        self.assertFalse(normalized["steps"][0]["idempotent"])
        self.assertEqual(normalized["steps"][0]["max_attempts"], 1)
        self.assertEqual(normalize(normalized), normalized)
        with self.assertRaises(HarnessError):
            normalize(plan(idempotent=True))

    def test_jsonl_metadata_only_and_fixed_permissions(self):
        checkpoints = []
        def fake_process(command, cwd, timeout, payload, on_line):
            self.assertIn("read-only", command)
            self.assertIn("--ignore-user-config", command)
            self.assertIn("--ephemeral", command)
            self.assertEqual(command[-1], "-")
            self.assertEqual(timeout, 120)
            self.assertNotIn("Inspect sample.txt", command)
            for item in [
                {"type": "thread.started", "thread_id": "12345678-abcd-abcd-abcd-123456789abc"},
                {"type": "item.completed", "item": {"type": "command_execution", "command": "PRIVATE_COMMAND"}},
                {"type": "item.completed", "item": {"type": "agent_message", "text": "PRIVATE_RESPONSE"}},
                {"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 2, "output_tokens": 3}},
            ]:
                on_line(json.dumps(item).encode())
            return {"exit_code": 0, "timeout": False, "seconds": 1, "termination_confirmed": True, "output_truncated": False}, None
        with patch("harness.codex.resolve_cli", return_value=["codex"]), patch("harness.codex.process", side_effect=fake_process):
            executor = CodexExecutor(checkpoint=checkpoints.append)
            executor.version = "0.159.0"
            result = executor.execute(normalize(plan())["steps"][0], {}, self.root, 1)
        validate_result(result)
        self.assertTrue(result["ok"])
        self.assertEqual(result["command_events"], 1)
        self.assertEqual(result["input_tokens"], 10)
        self.assertEqual(len(checkpoints), 1)
        self.assertNotIn("PRIVATE", json.dumps(result))

    def test_exit_zero_without_terminal_event_is_uncertain(self):
        with patch("harness.codex.resolve_cli", return_value=["codex"]), patch("harness.codex.process", return_value=({"exit_code": 0, "timeout": False, "seconds": 1, "termination_confirmed": True, "output_truncated": False}, None)):
            result = CodexExecutor().execute(normalize(plan())["steps"][0], {}, self.root, 1)
        self.assertFalse(result["ok"])
        self.assertTrue(result["uncertain"])

    def test_timeout_and_failure_never_retry_automatically(self):
        for failure in ("timeout", "execution"):
            with self.subTest(failure=failure):
                task = self.h.create("Read a fixture", plan(max_attempts=3))
                with patch("harness.codex.CodexExecutor.preflight", return_value=None), patch("harness.codex.CodexExecutor.execute", return_value=evidence(ok=False, failure=failure, uncertain=True)) as execute:
                    final = self.h.run(task["id"], allow_codex=True)
                    self.assertEqual(final["state"], "blocked")
                    self.h.run(task["id"], resume=True, allow_codex=True)
                    self.assertEqual(execute.call_count, 1)
                    self.h.run(task["id"], resume=True, allow_codex=True, confirmed=["inspect"])
                    self.assertEqual(execute.call_count, 2)

    def test_durable_start_session_and_gate_failure_do_not_repeat_codex(self):
        task = self.h.create("Read a fixture", plan())
        def execute(executor, spec, context, workspace, attempt):
            saved = self.h.context.load(task["id"])
            self.assertEqual(saved["steps"]["inspect"]["status"], "running")
            executor.checkpoint({"session_id": "12345678-abcd-abcd-abcd-123456789abc", "provider_version": "0.159.0"})
            self.assertEqual(self.h.context.load(task["id"])["history"][-1]["kind"], "provider_session")
            return evidence()
        with patch("harness.codex.CodexExecutor.preflight", return_value=None), patch("harness.codex.CodexExecutor.execute", autospec=True, side_effect=execute) as run, patch("harness.orchestrator.evaluate", return_value={"status": "failed"}):
            self.assertEqual(self.h.run(task["id"], allow_codex=True)["state"], "failed")
            self.h.run(task["id"], resume=True, allow_codex=True)
            self.assertEqual(run.call_count, 1)
        self.assertEqual(self.h.run(task["id"], resume=True)["state"], "completed")
        self.assertEqual((self.root / "sample.txt").read_text(), "preserve contributor work")

    def test_restart_interruption_requires_confirmation_and_budget(self):
        task = self.h.create("Read a fixture", plan())
        with patch("harness.codex.CodexExecutor.preflight", return_value=None), patch("harness.codex.CodexExecutor.execute", side_effect=KeyboardInterrupt):
            self.assertEqual(self.h.run(task["id"], allow_codex=True)["state"], "blocked")
        with patch("harness.codex.CodexExecutor.execute") as run:
            final = Orchestrator(self.root).run(task["id"], resume=True, allow_codex=True, confirmed=["inspect"])
            self.assertEqual(final["state"], "failed")
            self.assertEqual(final["steps"]["inspect"]["attempts"], 1)
            run.assert_not_called()
