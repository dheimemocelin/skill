# Engineering Harness Lite v1 — local evidence

Date: 2026-10-28. Platform: Windows, Python 3.11.5, PowerShell.
Base: `573ba34` (includes the earlier selective TStack integration).
Implementation: `879eae6`; conservative backup recovery fix: `d3e4264`; terminal-state recovery fix: `c44fed3`.

## Automated validation

- `py -3 scripts/validate_skills.py`: exit 0; seven skills and local Markdown links validated.
- `py -3 -m unittest discover -s tests -v`: 38 tests passed, 6.520 seconds in the run after the terminal-state fix (12 existing adapter tests, 26 Harness tests).
- `git diff --check`: exit 0.
- No differences from base under `agents/`, `skills/`, `adapters/` or `scripts/`.

Tests use real local subprocesses and temporary fixtures. Interruption tests inject Ctrl+C/construct a persisted in-flight state; they do not prove process-tree cleanup after an OS crash. The lock test launches a second process and observes exclusion. Corruption tests cover malformed content, incorrect schema/state, failed atomic replacement, and both backups before/after a recorded attempt. Non-idempotent uncertainty is blocked and charged conservatively.

## CLI demonstration

Commands used the three versioned plans in `examples/harness/`. Local snapshots remain in ignored `.harness/`; no raw transcripts or environment data are included here.

1. Inspection task `5beb52db36b84943ae97aae5d1b46569`: `create` + `run` completed. The real `local-file` executor returned a README SHA-256 and the file gate passed.
2. Recovery task `be48a2b4eb4a478abc941152ff50ccdd`: `run` returned `blocked` / exit 2 after a deliberate synthetic failure. `resume` without confirmation remained blocked with one attempt. `resume --confirm-retry simulated-operation` completed on attempt two. Both records identify `executor: deterministic-fixture` and `synthetic: true`.
3. Validation task `a034bb23f8df42718f75ac8641a1e2ae`: `run` blocked before executing tests. `resume --allow-tests` completed; validator and unittest gate exit codes were both 0, with no timeout. The already completed inspection remained at one attempt. Recorded gate durations were 0.187 and 6.359 seconds, respectively. This demonstration preceded the additional backup-before-start and terminal-state regression tests; the final direct suite above includes both tests.

## Scope of evidence

This proves local Windows execution, CLI operation and the listed deterministic safeguards. Durations are single-run observations, not performance benchmarks. No LLM was called by the Harness. Codex/Claude runtime integration, native reviewer activation, Linux/macOS execution, machine-crash durability, network filesystems and detached child cleanup were not verified. Existing adapters pass their structural loading tests; this is not provider execution evidence.
