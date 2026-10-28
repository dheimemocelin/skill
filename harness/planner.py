"""Normalize explicit verifiable plans; no model or speculative task decomposition."""

import math
from pathlib import PurePosixPath
from .model import HarnessError, ID, text
from .router import route


def fields(obj, allowed, required=()):
    if not isinstance(obj, dict) or set(obj) - set(allowed) or set(required) - set(obj):
        raise HarnessError("Unknown or missing plan fields")


def bounded(value, low, high, integer=False):
    if type(value) not in ((int,) if integer else (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise HarnessError("Plan limit out of range")
    return value


def relative(value):
    text(value, "path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in {"..", ".git", ".harness", ".env"} for part in p.parts) or ":" in value or "\\" in value or any(part.startswith(".env.") for part in p.parts):
        raise HarnessError("Use a workspace-relative, non-sensitive file path")
    return value


def identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise HarnessError("IDs must start with a letter and use lowercase letters, digits, _ or -")
    return value


def normalize(plan):
    fields(plan, {"steps", "gates"}, {"steps", "gates"})
    if not isinstance(plan["steps"], list) or not 1 <= len(plan["steps"]) <= 32 or not isinstance(plan["gates"], list) or not 1 <= len(plan["gates"]) <= 32:
        raise HarnessError("Plans require 1..32 steps and gates")
    steps, seen = [], set()
    for raw in plan["steps"]:
        fields(raw, {"id", "action", "depends_on", "skills", "agent", "idempotent", "max_attempts", "timeout_seconds"}, {"id", "action"})
        sid = identifier(raw["id"])
        deps = raw.get("depends_on", [])
        if sid in seen or not isinstance(deps, list) or any(not isinstance(d, str) or d not in seen for d in deps) or len(deps) != len(set(deps)):
            raise HarnessError("Use unique steps in dependency order; cycles/forward references are invalid")
        action = raw["action"]
        if not isinstance(action, dict):
            raise HarnessError("Invalid action")
        if action.get("kind") == "file_exists":
            fields(action, {"kind", "path"}, {"kind", "path"})
            relative(action["path"])
        elif action.get("kind") == "fixture":
            fields(action, {"kind", "fail_until", "delay_seconds"}, {"kind"})
            bounded(action.get("fail_until", 0), 0, 5, True)
            bounded(action.get("delay_seconds", 0), 0, 60)
        else:
            raise HarnessError("Supported actions: file_exists (real local inspection), fixture (test only)")
        route(raw.get("skills", []), raw.get("agent"))
        if type(raw.get("idempotent", True)) is not bool:
            raise HarnessError("idempotent must be boolean")
        steps.append({
            "id": sid, "action": dict(action), "depends_on": deps,
            "skills": raw.get("skills", []), "agent": raw.get("agent"),
            "idempotent": raw.get("idempotent", True),
            "max_attempts": bounded(raw.get("max_attempts", 2), 1, 5, True),
            "timeout_seconds": bounded(raw.get("timeout_seconds", 10), 0.05, 300),
        })
        seen.add(sid)
    gates, gate_ids = [], set()
    for raw in plan["gates"]:
        fields(raw, {"id", "criterion", "kind", "step", "path", "sha256", "suite", "timeout_seconds"}, {"id", "criterion", "kind"})
        gid = identifier(raw["id"])
        if gid in gate_ids:
            raise HarnessError("Duplicate gate ID")
        gate_ids.add(gid)
        text(raw["criterion"], "acceptance criterion")
        kind = raw["kind"]
        specific = {"step_succeeded": {"step"}, "file_exists": {"path"}, "file_sha256": {"path", "sha256"}, "tests": {"suite"}, "review": set()}
        if kind not in specific:
            raise HarnessError("Unknown gate")
        fields(raw, {"id", "criterion", "kind", "timeout_seconds"} | specific[kind], {"id", "criterion", "kind"} | specific[kind])
        if kind == "step_succeeded" and raw["step"] not in seen:
            raise HarnessError("Unknown gate step")
        if kind in {"file_exists", "file_sha256"}:
            relative(raw["path"])
        if kind == "file_sha256" and (not isinstance(raw["sha256"], str) or len(raw["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in raw["sha256"])):
            raise HarnessError("Invalid SHA-256")
        if kind == "tests" and raw["suite"] not in {"skills", "unittest"}:
            raise HarnessError("Supported test suites: skills, unittest")
        gates.append({**raw, "timeout_seconds": bounded(raw.get("timeout_seconds", 30), 0.05, 300)})
    return {"steps": steps, "gates": gates}
