"""Acceptance evidence, opt-in trusted tests, and explicit unavailable review gates."""

from pathlib import Path
import sys

from .execution import BuiltinExecutor, confined_file, process
from .router import route


def evaluate(gate, task, workspace, allow_tests=False):
    kind = gate["kind"]
    if kind == "review":
        return {"status": "blocked", "reason": "review_executor_unavailable", "references": route([], "quality-reviewer")}
    if kind == "step_succeeded":
        ok = task["steps"][gate["step"]]["status"] == "completed"
        return {"status": "passed" if ok else "failed", "step": gate["step"]}
    if kind in {"file_exists", "file_sha256"}:
        spec = {"action": {"kind": "file_exists", "path": gate["path"]}, "timeout_seconds": gate["timeout_seconds"]}
        evidence = BuiltinExecutor().execute(spec, {}, workspace, 1)
        ok = evidence["ok"] and (kind == "file_exists" or evidence.get("sha256") == gate["sha256"])
        return {"status": "passed" if ok else "failed", **evidence}
    if not allow_tests:
        return {"status": "blocked", "reason": "test_execution_requires_allow_tests"}
    # Fixed commands only. Tests themselves are trusted project code, not sandboxed.
    if gate["suite"] == "skills":
        target = confined_file(workspace, "scripts/validate_skills.py")
        if not target.is_file():
            return {"status": "failed", "reason": "missing_validator"}
        command = [sys.executable, "-B", str(target)]
    else:
        target = confined_file(workspace, "tests")
        if not target.is_dir() or not any(target.rglob("test*.py")):
            return {"status": "failed", "reason": "no_tests_discovered"}
        command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(target), "-v"]
    evidence, _ = process(command, Path(workspace), gate["timeout_seconds"])
    return {"status": "passed" if evidence["exit_code"] == 0 and not evidence["timeout"] else "failed", "suite": gate["suite"], **evidence}
