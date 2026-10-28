"""Versioned state and explicit lifecycle invariants."""

from datetime import datetime, timezone
import re


class HarnessError(ValueError):
    pass


TRANSITIONS = {
    "pending": {"planning", "cancelled"},
    "planning": {"running", "blocked", "failed", "cancelled"},
    "running": {"validating", "blocked", "failed", "cancelled"},
    "validating": {"completed", "blocked", "failed", "cancelled"},
    "blocked": {"planning", "cancelled"},
    "failed": {"planning", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}
ID = re.compile(r"[a-z][a-z0-9_-]{0,47}\Z")
TASK_ID = re.compile(r"[0-9a-f]{32}\Z")


def now():
    return datetime.now(timezone.utc).isoformat()


def text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise HarnessError(f"Invalid {name}: use 1..2000 characters")
    # Defense in depth for common credentials, not a general secret detector.
    if re.search(r"(?i)(?:api[_ -]?key|password|token|secret)\s*[:=]\s*\S+|\b(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{8,}|BEGIN .*PRIVATE KEY", value):
        raise HarnessError("Possible credential: use a non-sensitive description")
    return value


def event(task, kind, **data):
    task["history"].append({"time": now(), "kind": kind, **data})


def transition(task, target):
    source = task["state"]
    if target not in TRANSITIONS[source]:
        raise HarnessError(f"Invalid transition: {source} -> {target}")
    task["state"] = target
    event(task, "transition", source=source, target=target)


def validate(task):
    from .planner import normalize
    from .execution import validate_result

    keys = {"schema_version", "id", "request", "workspace", "plan", "state", "steps", "gates", "history", "decisions", "revision"}
    if not isinstance(task, dict) or set(task) != keys or type(task["schema_version"]) is not int or task["schema_version"] != 1:
        raise HarnessError("Unsupported or invalid checkpoint schema")
    if not isinstance(task["id"], str) or not TASK_ID.fullmatch(task["id"]):
        raise HarnessError("Invalid task ID")
    text(task["request"], "request")
    if not isinstance(task["workspace"], str) or task["state"] not in TRANSITIONS:
        raise HarnessError("Invalid workspace/state")
    if type(task["revision"]) is not int or task["revision"] < 0:
        raise HarnessError("Invalid revision")
    if normalize(task["plan"]) != task["plan"]:
        raise HarnessError("Checkpoint plan is not normalized")
    steps = task["steps"]
    if not isinstance(steps, dict) or set(steps) != {s["id"] for s in task["plan"]["steps"]}:
        raise HarnessError("Invalid step states")
    for spec in task["plan"]["steps"]:
        state = steps[spec["id"]]
        if not isinstance(state, dict) or set(state) != {"status", "attempts", "evidence", "failure"}:
            raise HarnessError("Invalid step checkpoint")
        if state["status"] not in {"pending", "running", "completed", "failed"}:
            raise HarnessError("Invalid step status")
        if type(state["attempts"]) is not int or not 0 <= state["attempts"] <= spec["max_attempts"]:
            raise HarnessError("Invalid attempts")
        if state["status"] != "pending" and state["attempts"] == 0:
            raise HarnessError("Missing execution attempt")
        if state["failure"] not in {None, "execution", "timeout", "interrupted"}:
            raise HarnessError("Invalid failure classification")
        if not isinstance(state["evidence"], list):
            raise HarnessError("Invalid evidence")
        if len(state["evidence"]) > state["attempts"]:
            raise HarnessError("Evidence exceeds attempts")
        for result in state["evidence"]:
            validate_result(result)
        if state["status"] == "completed":
            if not state["evidence"] or state["evidence"][-1].get("ok") is not True:
                raise HarnessError("Completed step lacks evidence")
            if any(steps[d]["status"] != "completed" for d in spec["depends_on"]):
                raise HarnessError("Completed step has incomplete dependencies")
    if not isinstance(task["gates"], dict) or not set(task["gates"]).issubset({g["id"] for g in task["plan"]["gates"]}):
        raise HarnessError("Invalid gate evidence")
    for result in task["gates"].values():
        if not isinstance(result, dict) or result.get("status") not in {"running", "passed", "failed", "blocked"}:
            raise HarnessError("Invalid gate status")
    for key in ("history", "decisions"):
        if not isinstance(task[key], list):
            raise HarnessError(f"Invalid {key}")
    for entry in task["history"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("time"), str) or not isinstance(entry.get("kind"), str):
            raise HarnessError("Invalid history entry")
    for decision in task["decisions"]:
        text(decision, "decision")
    if task["state"] in {"validating", "completed"} and any(s["status"] != "completed" for s in steps.values()):
        raise HarnessError("Validation requires all steps completed")
    if task["state"] == "completed" and (len(task["gates"]) != len(task["plan"]["gates"]) or any(g["status"] != "passed" for g in task["gates"].values())):
        raise HarnessError("Completion requires passing gates")
