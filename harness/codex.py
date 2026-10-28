"""Optional Codex CLI executor. Read-only, ephemeral, no automatic provider replay."""
import json
import os
from pathlib import Path
import re
import shutil

from .execution import process


def resolve_cli(explicit=None):
    """Operator-selected executable, native PATH binary, or managed npm entrypoint."""
    candidates = [Path(explicit)] if explicit else []
    if not explicit:
        found = shutil.which("codex")
        if found:
            candidates.append(Path(found))
        managed = os.environ.get("CODEX_MANAGED_PACKAGE_ROOT")
        if managed:
            candidates.append(Path(managed) / "bin" / "codex.js")
    for path in candidates:
        if not path.is_file():
            continue
        path = path.resolve()
        if path.suffix.lower() in {".ps1", ".cmd", ".bat"}:
            continue
        if path.suffix.lower() == ".js":
            node = shutil.which("node")
            if node and Path(node).suffix.lower() not in {".ps1", ".cmd", ".bat"}:
                return [node, str(path)]
        elif os.name != "nt" or path.suffix.lower() == ".exe":
            return [str(path)]
    return None


class CodexExecutor:
    def __init__(self, executable=None, checkpoint=None):
        self.command = resolve_cli(executable)
        self.checkpoint = checkpoint
        self.version = None
        self.windows_sandbox = None

    def preflight(self, workspace):
        if not self.command:
            return "codex_unavailable"
        # Project MCP servers/hooks can have effects outside the shell sandbox.
        # v1.1 deliberately refuses such configuration instead of silently overriding it.
        user_config = (Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "config.toml").resolve()
        for parent in (Path(workspace).resolve(), *Path(workspace).resolve().parents):
            candidate = parent / ".codex" / "config.toml"
            if candidate.exists() and candidate.resolve() != user_config:
                return "codex_project_config_requires_isolation"
        if os.name == "nt" and user_config.is_file():
            import tomllib
            settings = tomllib.loads(user_config.read_text(encoding="utf-8"))
            mode = settings.get("windows", {}).get("sandbox")
            if mode in {"mxc", "elevated", "unelevated"}:
                self.windows_sandbox = mode
        for args in (["--version"], ["exec", "--help"]):
            result, out = process([*self.command, *args], workspace, 10, capture=True)
            if result["exit_code"] or result["timeout"] or not result["termination_confirmed"] or result["output_truncated"]:
                return "codex_preflight_failed"
            output = out.decode("utf-8", errors="replace")
            if args == ["--version"]:
                match = re.fullmatch(r"codex-cli ([0-9]+\.[0-9]+\.[0-9]+(?:[-.a-zA-Z0-9]*)?)\s*", output)
                if not match:
                    return "codex_version_unknown"
                self.version = match[1]
            elif any(flag not in output for flag in ("--json", "--ephemeral", "--ignore-user-config", "--sandbox")):
                return "codex_interface_unsupported"
        return None

    def execute(self, spec, context, workspace, attempt):
        metadata = {"session_id": None, "turn_completed": False, "provider_error": False,
                    "command_events": 0, "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}

        def consume(line):
            data = json.loads(line)
            kind = data.get("type")
            if kind == "thread.started":
                sid = data.get("thread_id")
                if isinstance(sid, str) and re.fullmatch(r"[a-f0-9-]{32,36}", sid):
                    metadata["session_id"] = sid
                    if self.checkpoint:
                        self.checkpoint({"session_id": sid, "provider_version": self.version})
            elif kind == "turn.completed":
                metadata["turn_completed"] = True
                for key in ("input_tokens", "cached_input_tokens", "output_tokens"):
                    value = data.get("usage", {}).get(key, 0)
                    if type(value) is int and 0 <= value < 10**12:
                        metadata[key] += value
            elif kind in {"turn.failed", "error"}:
                metadata["provider_error"] = True
            elif kind == "item.completed" and data.get("item", {}).get("type") == "command_execution":
                metadata["command_events"] += 1

        command = [*self.command, "exec", "--json", "--ephemeral", "--ignore-user-config",
                   "--sandbox", "read-only", "--cd", str(workspace), "--skip-git-repo-check",
                   "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
                   "-c", "features.multi_agent=false", "-"]
        if self.windows_sandbox:
            command[-1:-1] = ["-c", 'windows.sandbox="' + self.windows_sandbox + '"']
        prompt = ("Perform only the explicit read-only task below. Do not edit files, merge, push, deploy, "
                  "publish, access credentials or invoke external services/tools. No delegation. "
                  "Use only the necessary canonical references if relevant.\nTask: " + spec["action"]["prompt"] +
                  "\nContext: " + json.dumps(context, ensure_ascii=False))
        result, _ = process(command, workspace, spec["timeout_seconds"], payload=prompt.encode("utf-8"), on_line=consume)
        uncertain = not result["termination_confirmed"] or result["timeout"] or result["output_truncated"] or not metadata["turn_completed"]
        ok = result["exit_code"] == 0 and not uncertain and not metadata["provider_error"]
        return {"ok": ok, "failure": None if ok else "timeout" if result["timeout"] else "execution",
                "executor": "codex-cli", "provider_version": self.version, "uncertain": uncertain,
                **metadata, **result}
