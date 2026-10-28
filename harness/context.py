"""Atomic local checkpoints, corruption detection and a process-wide workspace lock."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

from .model import HarnessError, TASK_ID, event, validate
from .router import route


def encoded(task):
    return json.dumps(task, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")


class ContextManager:
    def __init__(self, workspace):
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise HarnessError("Workspace must exist")
        self.root = self.workspace / ".harness"
        if self.root.is_symlink():
            raise HarnessError("State directory cannot be a symlink")
        self.root.mkdir(mode=0o700, exist_ok=True)
        # Protect checkpoints even when --workspace points at another repository.
        ignore = self.root / ".gitignore"
        try:
            with ignore.open("x", encoding="utf-8") as stream:
                stream.write("*\n")
        except FileExistsError:
            if ignore.is_symlink() or ignore.read_text(encoding="utf-8") != "*\n":
                raise HarnessError("State directory must retain its ignore-all .gitignore")

    @contextmanager
    def lock(self):
        path = self.root / "lock"
        if path.is_symlink():
            raise HarnessError("Invalid lock path")
        with path.open("a+b") as handle:
            if path.stat().st_size == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise HarnessError("Another Harness operation is active in this workspace") from exc
            try:
                yield
            finally:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle, fcntl.LOCK_UN)

    def path(self, task_id):
        if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
            raise HarnessError("Invalid task ID")
        path = self.root / f"{task_id}.json"
        if path.is_symlink():
            raise HarnessError("Checkpoint cannot be a symlink")
        return path

    def _read(self, path):
        try:
            if path.is_symlink() or path.stat().st_size > 4_000_000:
                raise ValueError()
            envelope = json.loads(path.read_text(encoding="utf-8"))
            if set(envelope) != {"sha256", "task"}:
                raise ValueError()
            task = envelope["task"]
            if hashlib.sha256(encoded(task)).hexdigest() != envelope["sha256"]:
                raise ValueError()
            validate(task)
            if task["workspace"] != str(self.workspace):
                raise ValueError()
            return task
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            raise HarnessError("Invalid/missing checkpoint; no execution or automatic rollback performed") from exc

    def load(self, task_id):
        task = self._read(self.path(task_id))
        if task["id"] != task_id:
            raise HarnessError("Checkpoint identity mismatch")
        return task

    def _atomic(self, path, data):
        fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=self.root)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            if os.name != "nt":
                directory = os.open(self.root, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def save(self, task):
        validate(task)
        path = self.path(task["id"])
        if path.exists():
            old = self.load(task["id"])
            if old["revision"] != task["revision"]:
                raise HarnessError("Stale checkpoint revision")
            self._atomic(path.with_suffix(".bak"), path.read_bytes())
        task["revision"] += 1
        data = json.dumps({"sha256": hashlib.sha256(encoded(task)).hexdigest(), "task": task}, indent=2, ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(data) > 4_000_000:
            raise HarnessError("Checkpoint size limit reached")
        self._atomic(path, data)

    def restore(self, task_id):
        """Explicit recovery only: retain damaged file and distrust in-flight work."""
        path = self.path(task_id)
        task = self._read(path.with_suffix(".bak"))
        if task["id"] != task_id:
            raise HarnessError("Backup identity mismatch")
        if path.exists():
            os.replace(path, self.root / f"{task_id}.{uuid.uuid4().hex}.corrupt")
        if task["state"] != "cancelled":
            task["state"] = "blocked"
        for spec in task["plan"]["steps"]:
            step = task["steps"][spec["id"]]
            if step["status"] != "completed":
                # The missing primary may have contained the next start record.
                # Charge that uncertain attempt unless already marked in-flight.
                if step["status"] != "running":
                    step["attempts"] = min(spec["max_attempts"], step["attempts"] + 1)
                step.update(status="failed", failure="interrupted")
        event(task, "backup_restored", reason="Outcome may be uncertain; incomplete non-idempotent steps require confirmation")
        self.save(task)
        return task


def relevant_context(task, spec):
    """Only the objective, dependencies, recent decisions and selected file pointers."""
    return {
        "request": task["request"],
        "dependencies": {sid: task["steps"][sid]["evidence"][-1:] for sid in spec["depends_on"]},
        "decisions": task["decisions"][-5:],
        "references": route(spec["skills"], spec["agent"]),
    }
