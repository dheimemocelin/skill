"""Serial lifecycle controller. Every attempted effect has a durable start record."""

import uuid

from .context import ContextManager, relevant_context
from .execution import BuiltinExecutor, validate_result
from .gates import evaluate
from .model import HarnessError, event, text, transition
from .planner import normalize
from .recovery import recover, retry_allowed


class Orchestrator:
    def __init__(self, workspace, executor=None):
        self.context = ContextManager(workspace)
        self.executor = executor or BuiltinExecutor()

    def create(self, request, plan):
        task = {
            "schema_version": 1, "id": uuid.uuid4().hex,
            "request": text(request, "request"), "workspace": str(self.context.workspace),
            "plan": normalize(plan), "state": "pending", "steps": {},
            "gates": {}, "history": [], "decisions": [], "revision": 0,
        }
        task["steps"] = {s["id"]: {"status": "pending", "attempts": 0, "evidence": [], "failure": None} for s in task["plan"]["steps"]}
        event(task, "created")
        with self.context.lock():
            self.context.save(task)
        return task

    def cancel(self, task_id):
        with self.context.lock():
            task = self.context.load(task_id)
            transition(task, "cancelled")
            self.context.save(task)
            return task

    def note(self, task_id, decision):
        with self.context.lock():
            task = self.context.load(task_id)
            task["decisions"].append(text(decision, "decision"))
            event(task, "decision_recorded")
            self.context.save(task)
            return task

    def run(self, task_id, *, resume=False, confirmed=(), allow_tests=False, test_profiles=None, confirmed_gates=(), allow_codex=False, codex_bin=None):
        with self.context.lock():
            task = self.context.load(task_id)
            confirmations = set(confirmed)
            if not set(confirmed_gates).issubset({g["id"] for g in task["plan"]["gates"]}):
                raise HarnessError("Unknown gate confirmation")
            if resume:
                recover(task, confirmations)
            elif task["state"] != "pending":
                raise HarnessError("Use resume for interrupted, blocked or failed tasks")
            transition(task, "planning")
            self.context.save(task)
            transition(task, "running")
            self.context.save(task)
            try:
                return self._execute(task, confirmations, allow_tests, test_profiles, set(confirmed_gates), allow_codex, codex_bin)
            except KeyboardInterrupt:
                event(task, "interrupted", reason="Inspect outstanding processes before resume")
                transition(task, "blocked")
                self.context.save(task)
                return task

    def _stop(self, task, state, reason, step=None):
        event(task, "stopped", reason=reason, step=step)
        transition(task, state)
        self.context.save(task)
        return task

    def _execute(self, task, confirmations, allow_tests, test_profiles=None, confirmed_gates=(), allow_codex=False, codex_bin=None):
        for spec in task["plan"]["steps"]:
            sid, state = spec["id"], task["steps"][spec["id"]]
            if state["status"] == "completed":
                continue
            executor = self.executor
            if spec["action"]["kind"] == "codex":
                if not allow_codex:
                    return self._stop(task, "blocked", "codex_requires_allow_codex", sid)
                from .codex import CodexExecutor
                def checkpoint(metadata):
                    event(task, "provider_session", step=sid, **metadata)
                    self.context.save(task)
                executor = CodexExecutor(codex_bin, checkpoint)
                reason = retry_allowed(spec, state, confirmations)
                if reason:
                    return self._stop(task, "failed" if reason == "attempt_limit" else "blocked", reason, sid)
                try:
                    reason = executor.preflight(self.context.workspace)
                except Exception:
                    reason = "codex_preflight_failed"
                if reason:
                    return self._stop(task, "blocked", reason, sid)
            while state["status"] != "completed":
                reason = retry_allowed(spec, state, confirmations)
                if reason:
                    return self._stop(task, "failed" if reason == "attempt_limit" else "blocked", reason, sid)
                confirmations.discard(sid)  # Confirmation covers one attempt, never the loop.
                state.update(status="running", attempts=state["attempts"] + 1, failure=None)
                event(task, "step_started", step=sid, attempt=state["attempts"])
                self.context.save(task)
                try:
                    result = executor.execute(spec, relevant_context(task, spec), self.context.workspace, state["attempts"])
                    validate_result(result)
                except Exception:
                    # Exceptions/output may contain secrets; keep classification only.
                    result = {"ok": False, "failure": "execution", "executor": "error"}
                    if spec["action"]["kind"] == "codex":
                        result.update(uncertain=True, termination_confirmed=False)
                state["evidence"].append(result)
                state.update(status="completed" if result["ok"] else "failed", failure=result["failure"])
                event(task, "step_finished", step=sid, attempt=state["attempts"], ok=result["ok"])
                self.context.save(task)
                if spec["action"]["kind"] == "codex" and not result["ok"]:
                    return self._stop(task, "blocked" if result.get("uncertain") else "failed", "codex_outcome_requires_inspection", sid)
        transition(task, "validating")
        self.context.save(task)
        # Recheck all acceptance gates on resume; completed steps are never rerun.
        for gate in task["plan"]["gates"]:
            previous = task["gates"].get(gate["id"], {})
            if gate["kind"] in {"tests", "node"} and (previous.get("status") == "running" or previous.get("termination_confirmed") is False) and gate["id"] not in confirmed_gates:
                return self._stop(task, "blocked", "confirm_gate_processes_stopped", gate["id"])
            if gate["id"] in confirmed_gates:
                event(task, "gate_retry_confirmed", gate=gate["id"])
            task["gates"][gate["id"]] = {"status": "running"}
            event(task, "gate_started", gate=gate["id"])
            self.context.save(task)
            try:
                result = evaluate(gate, task, self.context.workspace, allow_tests, test_profiles)
            except Exception:
                result = {"status": "failed", "reason": "gate_execution_error"}
                if gate["kind"] in {"tests", "node"}:
                    result.update(status="blocked", termination_confirmed=False)
            task["gates"][gate["id"]] = result
            event(task, "gate_finished", gate=gate["id"], status=result["status"])
            self.context.save(task)
            if result["status"] != "passed":
                return self._stop(task, "blocked" if result["status"] == "blocked" else "failed", "quality_gate", gate["id"])
        transition(task, "completed")
        self.context.save(task)
        return task
