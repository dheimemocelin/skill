"""Conservative recovery: success is retained, uncertainty is never implicit consent."""

from .model import HarnessError, event, transition


def recover(task, confirmed):
    if task["state"] in {"completed", "cancelled"}:
        raise HarnessError("Terminal tasks cannot resume; create a new task")
    if not set(confirmed).issubset(task["steps"]):
        raise HarnessError("Unknown retry confirmation")
    for sid, state in task["steps"].items():
        if state["status"] == "running":
            state.update(status="failed", failure="interrupted")
            event(task, "interrupted_step", step=sid)
    if task["state"] in {"planning", "running", "validating"}:
        transition(task, "blocked")
    event(task, "resume_requested", confirmed_retries=sorted(confirmed))


def retry_allowed(spec, state, confirmed):
    if state["attempts"] >= spec["max_attempts"]:
        return "attempt_limit"
    if state["attempts"] and not spec["idempotent"] and spec["id"] not in confirmed:
        return "confirmation_required"
    return None
