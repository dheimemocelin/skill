"""Real Node runtime tests; package entrypoint fixtures are NOT framework smoke tests."""
import json
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

from harness.gates import evaluate
from harness.model import HarnessError
from harness.node_gates import PROFILES, evaluate_node, validate_gate
from harness.orchestrator import Orchestrator


def gate(profile="node-test", **extra):
    return {"id": "node", "kind": "node", "criterion": "Tests pass", "profile": profile,
            "timeout_seconds": 10, **extra}


class NodeGatesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def test_authorization_before_discovery(self):
        with patch("harness.node_gates.shutil.which") as find:
            self.assertEqual(evaluate(gate(), {}, self.root)["status"], "blocked")
            self.assertEqual(evaluate_node(gate(), self.root, {"vitest"})["reason"], "profile_not_authorized")
            find.assert_not_called()

    def test_missing_node_and_tool(self):
        with patch("harness.node_gates.shutil.which", return_value=None):
            self.assertEqual(evaluate_node(gate(), self.root)["reason"], "node_unavailable")
        with patch("harness.node_gates.shutil.which", return_value="node.exe"):
            self.assertEqual(evaluate_node(gate("vitest"), self.root)["reason"], "tool_not_installed")

    def test_reject_commands_flags_and_paths(self):
        for candidate in [gate("npm"), gate([]), gate(args=["--help"]), gate(args=["--eval=bad"]),
                          gate(cwd="../outside"), gate(args=["../private"]), gate(args="shell"),
                          gate("vitest", args=["--passWithNoTests"]), gate("build", args=["custom.js"])]:
            with self.subTest(candidate=candidate), self.assertRaises(HarnessError):
                validate_gate(candidate)

    def test_all_framework_entrypoints_are_structured(self):
        for profile, (package, binary, mandatory) in PROFILES.items():
            if not package:
                continue
            directory = self.root / "node_modules" / package
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "package.json").write_text(json.dumps({"bin": {binary: "cli.js"}}))
            (directory / "cli.js").write_text("// unit fixture, not the framework")
            with patch("harness.node_gates.shutil.which", return_value="node.exe"), patch("harness.node_gates.process", return_value=({"exit_code": 0, "timeout": False, "termination_confirmed": True}, None)) as run:
                self.assertEqual(evaluate_node(gate(profile), self.root)["status"], "passed")
                argv = run.call_args.args[0]
                self.assertEqual(argv[:2], ["node.exe", str(directory / "cli.js")])
                self.assertEqual(argv[2:2 + len(mandatory)], mandatory)

    @unittest.skipUnless(shutil.which("node"), "Node unavailable")
    def test_real_node_success_failure_and_recovery(self):
        file = self.root / "example.cjs"
        file.write_text("require('node:test')('example', () => { throw Error('private detail'); });")
        h = Orchestrator(self.root)
        task = h.create("Validate synthetic Node project", {"steps": [{"id": "inspect", "action": {"kind": "file_exists", "path": "example.cjs"}}], "gates": [gate(args=["example.cjs"])]})
        self.assertEqual(h.run(task["id"])["state"], "blocked")
        failed = h.run(task["id"], resume=True, allow_tests=True)
        self.assertEqual(failed["state"], "failed")
        self.assertNotEqual(failed["gates"]["node"]["exit_code"], 0)
        self.assertNotIn("private detail", h.context.path(task["id"]).read_text())
        file.write_text("require('node:test')('example', () => {});")
        final = h.run(task["id"], resume=True, allow_tests=True)
        self.assertEqual(final["state"], "completed")
        self.assertEqual(final["steps"], failed["steps"])

    @unittest.skipUnless(shutil.which("node"), "Node unavailable")
    def test_timeout_stops_child_process(self):
        from harness.execution import process
        (self.root / "child.cjs").write_text("setTimeout(() => require('fs').writeFileSync('escaped.txt', 'bad'), 1500);")
        (self.root / "parent.cjs").write_text("require('child_process').spawn(process.execPath, ['child.cjs'], {stdio:'ignore'}); setTimeout(() => {}, 5000);")
        evidence, _ = process([shutil.which("node"), "parent.cjs"], self.root, 0.5)
        self.assertTrue(evidence["timeout"])
        # POSIX may conservatively report a surviving zombie; it must never pass.
        time.sleep(1.5)
        self.assertFalse((self.root / "escaped.txt").exists())

    def test_uncertain_gate_requires_confirmation(self):
        h = Orchestrator(self.root)
        task = h.create("Test recovery", {"steps": [{"id": "inspect", "action": {"kind": "fixture"}}], "gates": [gate()]})
        with patch("harness.orchestrator.evaluate", return_value={"status": "blocked", "termination_confirmed": False}):
            h.run(task["id"], allow_tests=True)
        with patch("harness.orchestrator.evaluate", return_value={"status": "passed"}) as run:
            self.assertEqual(h.run(task["id"], resume=True, allow_tests=True)["state"], "blocked")
            run.assert_not_called()
            self.assertEqual(h.run(task["id"], resume=True, allow_tests=True, confirmed_gates=["node"])["state"], "completed")
