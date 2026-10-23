#!/usr/bin/env python3
"""Run real provider smoke tests in isolated synthetic Git workspaces.

Raw logs and transcripts are written only beneath .local-evidence/ (gitignored).
No model-authored claim is accepted as evidence of agent/skill activation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_agent_adapters import parse_agent

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".local-evidence" / "agent-smoke"
CODEX_PACKAGE = os.environ.get("CODEX_MANAGED_PACKAGE_ROOT")
CODEX_JS = Path(CODEX_PACKAGE) / "bin" / "codex.js" if CODEX_PACKAGE else None


@dataclass(frozen=True)
class Case:
    name: str
    agent: str | None
    prompt: str
    files: dict[str, str]
    checks: dict[str, str]
    unchanged: bool = False
    commands: tuple[tuple[str, ...], ...] = ()
    output_contains: tuple[str, ...] = ()


CASES = (
    Case("feature", "software-engineer", "Use the configured software-engineer specialist and explicitly activate `$software-engineering` to implement this feature. In calculator.py add subtract(a, b), and add a unittest in test_calculator.py that verifies subtract(9, 4) == 5. Keep the change minimal and run the test.", {"calculator.py": "def add(a, b):\n    return a + b\n", "test_calculator.py": "import unittest\nfrom calculator import add\n\nclass CalculatorTests(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n"}, {"calculator.py": "def subtract(a, b):", "test_calculator.py": "subtract(9, 4)"}, commands=((sys.executable, "-B", "-m", "unittest", "test_calculator.py"),)),
    Case("bug-fix", "software-engineer", "Use the configured software-engineer specialist and explicitly activate `$software-engineering` to diagnose and fix this bug. The multiply function is intended to multiply but is wrong. Correct calculator.py, add a regression test in test_calculator.py, and run the test.", {"calculator.py": "def multiply(a, b):\n    return a + b\n", "test_calculator.py": "import unittest\nfrom calculator import multiply\n\nclass CalculatorTests(unittest.TestCase):\n    def test_multiply(self):\n        self.assertEqual(multiply(3, 4), 12)\n"}, {"calculator.py": "return a * b", "test_calculator.py": "self.assertEqual(multiply(3, 4), 12)"}, commands=((sys.executable, "-B", "-m", "unittest", "test_calculator.py"),)),
    Case("llm-agent", "ai-engineer", "Use the configured ai-engineer specialist and explicitly activate `$ai-engineering` and `$software-engineering`. Implement a small model-backed sentiment agent in sentiment_agent.py using an injected client protocol with classify(text); do not call a real provider. Add a unittest using a fake client that verifies delegation to the injected client and its result.", {"sentiment_agent.py": "", "test_sentiment_agent.py": ""}, {"sentiment_agent.py": "class SentimentAgent", "test_sentiment_agent.py": "FakeClient"}, commands=((sys.executable, "-B", "-m", "unittest", "test_sentiment_agent.py"),)),
    Case("review", "quality-reviewer", "Use the configured quality reviewer specialist. Explicitly activate `$git-quality` to review this code read-only. Identify the correctness/security issue with file and line evidence. Do not edit any file.", {"auth.py": "API_KEY = 'placeholder-secret-for-review-fixture'\n\ndef authorize(user):\n    return True\n"}, {"auth.py": ""}, unchanged=True, output_contains=("auth.py", "authorize")),
    Case("concept", None, "In one short paragraph, explain what idempotent means in software. Do not delegate." , {}, {}),
    Case("explain-code", None, "Explain what this function does in one sentence: def add(a, b): return a + b. Do not delegate.", {}, {}),
    Case("docs-typo", None, "In README.md, change only the word 'recieve' to 'receive'. Do this tiny documentation fix directly without delegation.", {"README.md": "# Fixture\n\nPlease recieve this.\n"}, {"README.md": "Please receive this."}),
    Case("no-delegation", None, "Tell me the command to run the Python unittest suite in this repository. Do not run commands or delegate.", {}, {}),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.parts}


def run(command: list[str], *, cwd: Path, timeout: int = 180) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout, check=False)


def provider_command(provider: str, workspace: Path, prompt: str, read_only: bool) -> tuple[list[str], str]:
    if provider == "codex":
        if not CODEX_JS or not CODEX_JS.is_file():
            raise FileNotFoundError("Codex CLI package not found; set CODEX_MANAGED_PACKAGE_ROOT or put codex on PATH")
        cli = ["node", str(CODEX_JS)]
        version = run(["node", str(CODEX_JS), "--version"], cwd=workspace, timeout=20).stdout.strip()
        sandbox = "read-only" if read_only else "workspace-write"
        return cli + ["exec", "--json", "--sandbox", sandbox, "--cd", str(workspace), prompt], version
    executable = shutil.which("claude")
    if not executable:
        raise FileNotFoundError("Claude Code CLI (claude) is not installed or not on PATH")
    version = run([executable, "--version"], cwd=workspace, timeout=20).stdout.strip()
    return [executable, "-p", prompt, "--output-format", "stream-json", "--verbose", "--include-partial-messages", "--forward-subagent-text"], version


def event_records(provider: str, output: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in output.splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        events.append(record)
    return events


def dispatches(provider: str, events: list[dict[str, Any]]) -> list[str]:
    found: list[str] = []
    def visit(value: Any) -> None:
        if isinstance(value, dict):
            tool = value.get("name") or value.get("tool_name")
            payload = value.get("input") or value.get("arguments") or {}
            if provider == "claude" and tool in {"Agent", "Task"} and isinstance(payload, dict):
                role = payload.get("subagent_type") or payload.get("agent_type") or payload.get("name")
                if isinstance(role, str):
                    found.append(role)
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)
    # These are provider-native structured tool/collaboration records. Never scan prose.
    for event in events:
        if provider == "claude":
            visit(event)
        else:
            item = event.get("item") if isinstance(event.get("item"), dict) else event
            kind = item.get("type") or item.get("kind")
            if kind in {"collab_tool_call", "agent_tool_call", "subagent_tool_call"} and item.get("tool") in {"spawn_agent", "spawn_subagent", "delegate_task"}:
                role = item.get("agent_type") or item.get("agent_name") or item.get("name") or item.get("recipient")
                if isinstance(role, str):
                    found.append(role)
    return found


def skill_events(provider: str, events: list[dict[str, Any]]) -> list[str]:
    found: list[str] = []
    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if (value.get("name") or value.get("tool_name")) == "Skill":
                payload = value.get("input") or value.get("arguments") or {}
                if isinstance(payload, dict) and isinstance(payload.get("skill"), str):
                    found.append(payload["skill"])
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)
    for event in events:
        if provider == "claude":
            visit(event)
        else:
            item = event.get("item") if isinstance(event.get("item"), dict) else event
            if item.get("type") in {"skill_invocation", "skill_load", "skill_tool_call"}:
                name = item.get("name") or item.get("skill")
                if isinstance(name, str):
                    found.append(name)
    return found


def provider_quota_blocked(stdout: str, stderr: str) -> bool:
    """Recognize provider errors, not ordinary model text that mentions quotas."""
    markers = ("usage limit", "rate limit", "insufficient_quota", "payment required")
    if any(marker in stderr.casefold() for marker in markers):
        return True
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "error":
            message = str(event.get("message", "")).casefold()
        elif event.get("type") == "turn.failed":
            error = event.get("error", {})
            message = str(error.get("message", "") if isinstance(error, dict) else error).casefold()
        else:
            continue
        if any(marker in message for marker in markers):
            return True
    return False


def codex_trace_evidence(stdout: str, skills: list[str]) -> tuple[list[str], list[str]]:
    """Read only native role/skill metadata from this CLI run's private session trace."""
    events = event_records("codex", stdout)
    thread_id = next((event.get("thread_id") for event in events if event.get("type") == "thread.started"), None)
    if not isinstance(thread_id, str):
        return [], []
    session_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
    parent_files = list(session_root.rglob(f"*-{thread_id}.jsonl")) if session_root.exists() else []
    if len(parent_files) != 1:
        return [], []
    parent = parent_files[0]
    role_names: list[str] = []
    trace_files = [parent]
    for path in parent.parent.glob("*.jsonl"):
        if path == parent:
            continue
        try:
            first = json.loads(path.open(encoding="utf-8").readline())
        except (OSError, json.JSONDecodeError):
            continue
        meta = first.get("payload", {})
        if meta.get("parent_thread_id") == thread_id:
            role = meta.get("agent_role")
            if isinstance(role, str):
                role_names.append(role.replace("_", "-"))
            trace_files.append(path)
    activated: list[str] = []
    # Codex does not emit a dedicated skill event in `exec --json`; internal session
    # records are checked for the exact installed skill body, never for response prose.
    log_strings: list[str] = []
    def collect_strings(value: Any) -> None:
        if isinstance(value, str):
            log_strings.append(value)
        elif isinstance(value, dict):
            for nested in value.values():
                collect_strings(nested)
        elif isinstance(value, list):
            for nested in value:
                collect_strings(nested)
    for path in trace_files:
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    collect_strings(json.loads(line))
                except json.JSONDecodeError:
                    continue
        except OSError:
            pass
    for skill in skills:
        source = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        body = source.split("---", 2)[-1].strip()
        if body and any(body in text for text in log_strings):
            activated.append(skill)
    return role_names, activated


def prepare_workspace(provider: str, case: Case, workspace: Path) -> tuple[dict[str, str], dict[str, str]]:
    for name, content in case.files.items():
        path = workspace / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    staging = workspace / ".adapter-staging"
    result = run([sys.executable, str(ROOT / "scripts" / "build_agent_adapters.py"), "--target", provider, "--output", str(staging)], cwd=ROOT)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    for native in (".claude", ".agents", ".codex"):
        source = staging / native
        if source.exists():
            shutil.copytree(source, workspace / native, dirs_exist_ok=True)
    shutil.rmtree(staging)
    init = run(["git", "init", "-q"], cwd=workspace)
    if init.returncode:
        raise RuntimeError("Unable to initialize isolated fixture Git project")
    config_hashes = {p.relative_to(workspace).as_posix(): sha256(p) for p in sorted(workspace.rglob("*")) if p.is_file() and ("agents" in p.parts or "skills" in p.parts)}
    return snapshot(workspace), config_hashes


def codex_config_path() -> Path:
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"


def add_smoke_trust_entry(workspace: Path) -> tuple[bool, bool]:
    """Temporarily trust this synthetic project so Codex can discover custom agents."""
    config = codex_config_path()
    existed = config.is_file()
    current = config.read_text(encoding="utf-8") if existed else ""
    normalized = str(workspace.resolve()).replace("/", "\\").casefold()
    header = f"[projects.'{normalized}']".casefold()
    lines = current.splitlines(keepends=True)
    if any(line.strip().casefold() == header for line in lines):
        return not existed, False
    if current and not current.endswith(("\n", "\r")):
        current += "\n"
    config.write_text(current + f"\n{header}\ntrust_level = \"trusted\"\n", encoding="utf-8")
    return not existed, True


def remove_smoke_trust_entry(workspace: Path, config_created: bool = False, entry_added: bool = True) -> None:
    """Remove only this synthetic fixture's temporary trust table."""
    config = codex_config_path()
    if not entry_added or not config.is_file():
        return
    normalized = str(workspace.resolve()).replace("/", "\\").casefold()
    header = f"[projects.'{normalized}']".casefold()
    lines = config.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if line.strip().casefold() == header), None)
    if start is None:
        return
    end = next((index for index in range(start + 1, len(lines)) if lines[index].lstrip().startswith("[")), len(lines))
    remainder = "".join(lines[:start] + lines[end:])
    if config_created and not remainder.strip():
        config.unlink()
    else:
        config.write_text(remainder, encoding="utf-8")


def run_case(provider: str, case: Case, evidence_dir: Path, timeout: int) -> dict[str, Any]:
    case_dir = evidence_dir / case.name
    case_dir.mkdir(parents=True, exist_ok=True)
    local_runs = ROOT / ".smoke-runs"
    local_runs.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{provider}-{case.name}-", dir=local_runs) as temporary:
        workspace = Path(temporary)
        initial, config_hashes = prepare_workspace(provider, case, workspace)
        prompt = case.prompt
        if provider == "codex" and case.agent:
            native_agent = case.agent.replace("-", "_")
            native_task = case.name.replace("-", "_")
            prompt = f"Use the configured custom agent_type `{native_agent}` and task_name `{native_task}`. {prompt}"
        command, version = provider_command(provider, workspace, prompt, case.unchanged)
        created_config, trust_entry_added = add_smoke_trust_entry(workspace) if provider == "codex" else (False, False)
        try:
            result = subprocess.run(command, cwd=workspace, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
            stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
            (case_dir / "stdout.jsonl").write_text(stdout, encoding="utf-8")
            (case_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
            raise RuntimeError(f"{case.name}: timed out after {timeout}s") from exc
        finally:
            if provider == "codex":
                remove_smoke_trust_entry(workspace, created_config, trust_entry_added)
        (case_dir / "stdout.jsonl").write_text(result.stdout, encoding="utf-8")
        (case_dir / "stderr.txt").write_text(result.stderr, encoding="utf-8")
        events = event_records(provider, result.stdout)
        invoked = dispatches(provider, events)
        skill_activated = skill_events(provider, events)
        if provider == "codex":
            codex_roles, codex_skills = codex_trace_evidence(result.stdout, [str(s) for s in parse_agent(ROOT / "agents" / f"{case.agent}.md")[0]["skills"]] if case.agent else [])
            invoked.extend(codex_roles)
            skill_activated.extend(codex_skills)
        final = snapshot(workspace)
        fixture_final = {name: final.get(name) for name in case.files}
        checks = {name: expected in (workspace / name).read_text(encoding="utf-8") for name, expected in case.checks.items()}
        unchanged = all(initial.get(name) == final.get(name) for name in case.files)
        validations = []
        for validation in case.commands:
            checked = run(list(validation), cwd=workspace, timeout=60)
            validations.append({"command": list(validation), "exit_code": checked.returncode})
        response_contains = {text: text.casefold() in result.stdout.casefold() for text in case.output_contains}
        expected_dispatch = case.agent is None or any(case.agent in role for role in invoked)
        unexpected_dispatch = case.agent is None and bool(invoked)
        execution_ok = all(checks.values()) and all(item["exit_code"] == 0 for item in validations) and all(response_contains.values()) and (not case.unchanged or unchanged)
        passed = result.returncode == 0 and expected_dispatch and not unexpected_dispatch and execution_ok
        return {
            "case": case.name,
            "result": "passed" if passed else "failed",
            "exit_code": result.returncode,
            "expected_agent": case.agent,
            "structured_agent_dispatches": invoked,
            "structured_skill_activations": skill_activated,
            "skill_event_visibility": "observable" if skill_activated else "no_structured_skill_event_observed",
            "checks": checks,
            "independent_fixture_validations": validations,
            "review_output_checks": response_contains,
            "fixture_initial_sha256": {k: v for k, v in initial.items() if k in case.files},
            "fixture_final_sha256": {k: v for k, v in fixture_final.items() if k in case.files},
            "fixture_unchanged": unchanged,
            "config_sha256": config_hashes,
            "transcript_path": str((case_dir / "stdout.jsonl").relative_to(ROOT)),
            "stderr_path": str((case_dir / "stderr.txt").relative_to(ROOT)),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("claude", "codex", "all"), required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--case", action="append", choices=[case.name for case in CASES], help="Run selected case(s); defaults to all eight")
    args = parser.parse_args()
    providers = ["claude", "codex"] if args.provider == "all" else [args.provider]
    selected = [case for case in CASES if not args.case or case.name in args.case]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = EVIDENCE / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {"run_id": run_id, "started_utc": datetime.now(timezone.utc).isoformat(), "providers": {}}
    unavailable = False
    failed = False
    blocked = False
    for provider in providers:
        provider_root = run_root / provider
        provider_root.mkdir(parents=True, exist_ok=True)
        try:
            # Verify availability before launching scenarios.
            probe = Path(tempfile.mkdtemp(prefix=f"engos-{provider}-probe-"))
            _, version = provider_command(provider, probe, "", False)
            shutil.rmtree(probe)
        except (FileNotFoundError, RuntimeError, subprocess.TimeoutExpired) as exc:
            summary["providers"][provider] = {"status": "not_run", "reason": str(exc)}
            unavailable = True
            continue
        outcomes = []
        provider_blocked = False
        for case in selected:
            if provider_blocked:
                outcomes.append({"case": case.name, "result": "not_run", "reason": "provider quota or access limit blocked this run"})
                continue
            try:
                outcome = run_case(provider, case, provider_root, args.timeout)
                case_stdout = (provider_root / case.name / "stdout.jsonl").read_text(encoding="utf-8", errors="replace")
                case_stderr = (provider_root / case.name / "stderr.txt").read_text(encoding="utf-8", errors="replace")
                if provider_quota_blocked(case_stdout, case_stderr):
                    outcome["result"] = "blocked"
                    outcome["block_reason"] = "provider quota or access limit"
                    provider_blocked = True
                    blocked = True
                outcomes.append(outcome)
            except Exception as exc:  # Keep recording subsequent cases; the error is in sanitized summary only.
                outcomes.append({"case": case.name, "result": "failed", "error": f"{type(exc).__name__}: {exc}"})
        provider_failed = any(outcome.get("result") == "failed" for outcome in outcomes)
        failed = failed or provider_failed
        provider_status = "failed" if provider_failed else "blocked" if provider_blocked else "passed"
        summary["providers"][provider] = {"status": provider_status, "version": version, "installed_configuration": "generated native project adapter", "cases": outcomes}
    summary["finished_utc"] = datetime.now(timezone.utc).isoformat()
    summary["limits"] = ["Claude activation uses native structured tool events; Codex role activation uses session agent_role metadata and skill activation requires the exact installed skill body in session records.", "Provider model answers are retained only in ignored local transcripts."]
    (run_root / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if failed:
        return 1
    if unavailable or blocked:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
