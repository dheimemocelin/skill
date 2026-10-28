"""Run with python -m harness. CLI output is JSON, errors never dump checkpoints."""

import argparse
import json
from pathlib import Path
import sys

from .model import HarnessError
from .orchestrator import Orchestrator


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="Create a task from a reviewed JSON plan")
    create.add_argument("request")
    create.add_argument("--plan", type=Path, required=True)
    for name in ("status", "history", "evidence", "cancel", "restore"):
        sub.add_parser(name).add_argument("task_id")
    for name in ("run", "resume"):
        command = sub.add_parser(name)
        command.add_argument("task_id")
        command.add_argument("--allow-tests", action="store_true", help="Authorize execution of trusted local test code for this invocation")
        from .node_gates import PROFILES
        command.add_argument("--test-profile", choices=sorted(PROFILES), action="append", help="Restrict authorized Node profiles (repeatable)")
        if name == "resume":
            command.add_argument("--confirm-retry", action="append", default=[], metavar="STEP", help="Confirm an uncertain/non-idempotent step is safe to retry once")
            command.add_argument("--confirm-gate", action="append", default=[], metavar="GATE", help="Confirm an interrupted gate's processes have stopped and replay is safe")
    note = sub.add_parser("note")
    note.add_argument("task_id")
    note.add_argument("decision")
    args = parser.parse_args(argv)
    try:
        harness = Orchestrator(args.workspace)
        command = args.command
        if command == "create":
            task = harness.create(args.request, json.loads(args.plan.read_text(encoding="utf-8")))
        elif command in {"run", "resume"}:
            task = harness.run(args.task_id, resume=command == "resume", confirmed=getattr(args, "confirm_retry", ()), allow_tests=args.allow_tests, test_profiles=args.test_profile, confirmed_gates=getattr(args, "confirm_gate", ()))
        elif command == "cancel":
            task = harness.cancel(args.task_id)
        elif command == "note":
            task = harness.note(args.task_id, args.decision)
        elif command == "restore":
            with harness.context.lock():
                task = harness.context.restore(args.task_id)
        else:
            task = harness.context.load(args.task_id)
        if command == "history":
            output = task["history"]
        elif command == "evidence":
            output = {"steps": task["steps"], "gates": task["gates"]}
        elif command == "status":
            output = task
        else:
            output = {"id": task["id"], "state": task["state"], "revision": task["revision"]}
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 2 if command in {"run", "resume"} and task["state"] != "completed" else 0
    except (HarnessError, OSError, ValueError, TypeError, KeyError) as exc:
        print(str(exc) if isinstance(exc, HarnessError) else "Invalid input or local I/O failure; no completion claimed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
