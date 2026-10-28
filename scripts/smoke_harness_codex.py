"""ONE explicitly authorized real read-only Codex call; no retry or raw transcript."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-codex", action="store_true", required=True)
    parser.add_argument("--codex-bin", type=Path)
    args = parser.parse_args()
    # Keep the synthetic workspace for local inspection; never version checkpoints.
    workspace = Path(tempfile.mkdtemp(prefix="harness-codex-smoke-"))
    content = b"Synthetic fixture: 6 * 7 = 42.\n"
    (workspace / "sample.txt").write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    plan = {"steps": [{"id": "inspect", "action": {"kind": "codex", "prompt": "Read sample.txt using a read-only command and report the arithmetic result. Do not modify anything."},
                       "max_attempts": 1, "timeout_seconds": 120}],
            "gates": [{"id": "preserved", "kind": "file_sha256", "path": "sample.txt", "sha256": digest, "criterion": "Original fixture bytes preserved"}]}
    h = Orchestrator(workspace)
    task = h.create("Read an isolated synthetic arithmetic fixture", plan)
    final = h.run(task["id"], allow_codex=True, codex_bin=args.codex_bin)
    report = {"platform": platform.system(), "python": platform.python_version(), "task_id": task["id"],
              "state": final["state"], "sandbox": "read-only", "timeout_seconds": 120, "max_attempts": 1,
              "initial_sha256": digest, "final_sha256": hashlib.sha256((workspace / "sample.txt").read_bytes()).hexdigest(),
              "steps": final["steps"], "gates": final["gates"], "history": final["history"]}
    destination = ROOT / ".local-evidence" / "harness-v1.1"
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / (task["id"] + ".json")
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(target), "workspace": str(workspace), **report}, indent=2))
    return 0 if final["state"] == "completed" else 2


if __name__ == "__main__":
    sys.exit(main())
