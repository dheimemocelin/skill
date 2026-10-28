"""Bounded executors. Local inspection is real; fixture execution is explicitly synthetic."""

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Protocol


def validate_result(result):
    allowed = {"ok", "failure", "executor", "exists", "sha256", "synthetic", "exit_code", "timeout", "seconds", "reason"}
    if not isinstance(result, dict) or set(result) - allowed or not {"ok", "failure", "executor"}.issubset(result):
        raise ValueError("Invalid executor evidence")
    if type(result["ok"]) is not bool or result["failure"] not in {None, "execution", "timeout"}:
        raise ValueError("Invalid result status")
    if result["ok"] != (result["failure"] is None):
        raise ValueError("Inconsistent result")
    if result["executor"] not in {"builtin", "local-file", "deterministic-fixture", "error"}:
        raise ValueError("Unregistered executor")
    if "reason" in result and result["reason"] != "file_too_large":
        raise ValueError("Unknown result reason")
    for key in {"exists", "synthetic", "timeout"} & result.keys():
        if type(result[key]) is not bool:
            raise ValueError("Invalid result flag")
    if "exit_code" in result and type(result["exit_code"]) is not int:
        raise ValueError("Invalid exit code")
    if "seconds" in result and (type(result["seconds"]) not in {int, float} or not 0 <= result["seconds"] <= 3600):
        raise ValueError("Invalid duration")
    if "sha256" in result and (not isinstance(result["sha256"], str) or len(result["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in result["sha256"])):
        raise ValueError("Invalid digest")
    return result


class Executor(Protocol):
    def execute(self, spec: dict, context: dict, workspace: Path, attempt: int) -> dict:
        """Return JSON evidence with ok/failure/executor; enforce spec timeout.

        Implementations must not persist credentials or raw provider output. Native
        provider permissions remain authoritative. v1 registers only BuiltinExecutor.
        """
        ...


def confined_file(workspace, relative):
    root = Path(workspace).resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root) or any(p in {".git", ".harness"} or p.startswith(".env") for p in candidate.relative_to(root).parts):
        raise ValueError("Unsafe path")
    return candidate


def inspect_file(workspace, relative):
    path = confined_file(workspace, relative)
    if not path.is_file():
        return {"ok": False, "failure": "execution", "executor": "local-file", "exists": False}
    # Bound reads and never record file contents. Large files are outside v1 scope.
    if path.stat().st_size > 16_000_000:
        return {"ok": False, "failure": "execution", "executor": "local-file", "reason": "file_too_large"}
    with path.open("rb") as stream:
        content = stream.read(16_000_001)
    if len(content) > 16_000_000:
        raise ValueError("File grew beyond limit")
    return {"ok": True, "failure": None, "executor": "local-file", "exists": True, "sha256": hashlib.sha256(content).hexdigest()}


def process(command, workspace, timeout, payload=None, capture=False):
    """No shell; discard raw output by default. Terminate the owned tree on timeout."""
    started = time.monotonic()
    child = subprocess.Popen(command, cwd=workspace, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=os.name != "nt")
    try:
        out, _ = child.communicate(payload, timeout=timeout)
        return {"exit_code": child.returncode, "timeout": False, "seconds": round(time.monotonic() - started, 3)}, out
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        interrupted = isinstance(sys.exc_info()[1], KeyboardInterrupt)
        try:
            if os.name == "nt":
                taskkill = str(Path(os.environ["SystemRoot"]) / "System32" / "taskkill.exe")
                subprocess.run([taskkill, "/PID", str(child.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=False)
            else:
                os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        finally:
            child.kill()
            child.communicate(timeout=10)
        if interrupted:
            raise KeyboardInterrupt
        return {"exit_code": child.returncode, "timeout": True, "seconds": round(time.monotonic() - started, 3)}, None


class BuiltinExecutor:
    def execute(self, spec, context, workspace, attempt):
        payload = json.dumps({"action": spec["action"], "workspace": str(workspace), "attempt": attempt}).encode()
        evidence, output = process([sys.executable, "-I", str(Path(__file__).resolve())], workspace,
                                   spec["timeout_seconds"], payload, capture=True)
        if evidence["timeout"]:
            return {"ok": False, "failure": "timeout", "executor": "builtin", **evidence}
        if evidence["exit_code"] != 0:
            return {"ok": False, "failure": "execution", "executor": "builtin", **evidence}
        return {**json.loads(output), **evidence}


def worker():
    data = json.load(sys.stdin)
    action = data["action"]
    if action["kind"] == "file_exists":
        result = inspect_file(data["workspace"], action["path"])
    elif action["kind"] == "fixture":
        time.sleep(action.get("delay_seconds", 0))
        ok = data["attempt"] > action.get("fail_until", 0)
        result = {"ok": ok, "failure": None if ok else "execution", "executor": "deterministic-fixture", "synthetic": True}
    else:
        raise ValueError("Unsupported action")
    print(json.dumps(result))


if __name__ == "__main__":
    worker()
