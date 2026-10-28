"""Allowlisted local Node tool profiles. No package install, npm shell or npx."""

import json
from pathlib import Path
import shutil

from .execution import confined_file, process
from .model import HarnessError

# Package, bin name, mandatory argv; resolved from the installed package manifest.
PROFILES = {
    "vitest": ("vitest", "vitest", ["run"]),
    "playwright": ("@playwright/test", "playwright", ["test"]),
    "eslint": ("eslint", "eslint", []),
    "typecheck": ("typescript", "tsc", ["--noEmit"]),
    "build": ("vite", "vite", ["build"]),
    "next-build": ("next", "next", ["build"]),
    "node-test": (None, None, ["--test"]),
}
FLAGS = {
    "vitest": {"--coverage", "--reporter=dot", "--reporter=verbose"},
    "playwright": {"--workers=1", "--reporter=line", "--reporter=list"},
    "eslint": {"--max-warnings=0"},
    "typecheck": set(), "build": set(), "next-build": set(), "node-test": set(),
}


def validate_gate(gate):
    from .planner import relative
    profile = gate["profile"]
    if not isinstance(profile, str) or profile not in PROFILES:
        raise HarnessError("Unknown Node test profile")
    relative(gate.get("cwd", "."))
    args = gate.get("args", [])
    if not isinstance(args, list) or len(args) > 32:
        raise HarnessError("Node args must be an array of at most 32 entries")
    for argument in args:
        if not isinstance(argument, str) or not argument or "\x00" in argument:
            raise HarnessError("Invalid Node argument")
        if argument.startswith("-"):
            if argument not in FLAGS[profile]:
                raise HarnessError("Node option is not allowlisted")
        elif profile in {"build", "next-build", "typecheck"}:
            raise HarnessError("Select the project with cwd for this profile")
        else:
            relative(argument)


def evaluate_node(gate, workspace, allowed_profiles=None):
    profile = gate["profile"]
    if allowed_profiles is not None and profile not in allowed_profiles:
        return {"status": "blocked", "reason": "profile_not_authorized"}
    node = shutil.which("node")
    if not node or Path(node).suffix.lower() in {".cmd", ".bat", ".ps1"}:
        return {"status": "blocked", "reason": "node_unavailable"}
    cwd = confined_file(workspace, gate.get("cwd", "."))
    if not cwd.is_dir():
        return {"status": "blocked", "reason": "cwd_missing"}
    args = gate.get("args", [])
    for argument in args:
        if not argument.startswith("-"):
            confined_file(cwd, argument)
    package, binary, mandatory = PROFILES[profile]
    if package:
        manifest = confined_file(workspace, str((cwd / "node_modules" / package / "package.json").relative_to(Path(workspace))).replace("\\", "/"))
        if not manifest.is_file():
            return {"status": "blocked", "reason": "tool_not_installed"}
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            entry = data["bin"] if isinstance(data["bin"], str) else data["bin"][binary]
            from .planner import relative
            relative(entry)
            script = (manifest.parent / entry).resolve()
            if not script.is_relative_to(manifest.parent) or not script.is_file():
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            return {"status": "blocked", "reason": "invalid_tool_manifest"}
        command = [node, str(script), *mandatory, *args]
        if profile == "eslint" and not args:
            command.append(".")
    else:
        if not args or any(not confined_file(cwd, arg).is_file() for arg in args):
            return {"status": "blocked", "reason": "test_files_missing"}
        command = [node, *mandatory, *args]
    evidence, _ = process(command, cwd, gate["timeout_seconds"])
    status = "passed" if evidence["exit_code"] == 0 and not evidence["timeout"] else "failed"
    if not evidence["termination_confirmed"]:
        status = "blocked"
    return {"status": status, "profile": profile, **evidence}
