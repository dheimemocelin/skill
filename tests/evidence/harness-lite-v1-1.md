# Engineering Harness Lite v1.1 — audit and execution evidence

Date: 2026-10-28. Local environment: Windows, PowerShell, Python 3.11.5, Node v22.23.2.
Branch: `feat/harness-lite-v1-1`. Baseline: `c5a80af`.

## Audit and preserved contracts

The v1 already provided explicit plans, serial orchestration, atomic checksummed JSON with backups, workspace locking, bounded attempts, conservative non-idempotent recovery, local file inspection and Python test gates. Reused these contracts instead of introducing another runtime. Checkpoint schema remains 1; old normalized plans remain readable.

The gaps addressed are controlled Node validation and optional real Codex dispatch. Windows process containment was strengthened with a Job Object assigned before the execution handshake; POSIX uses a new process group. Unknown process outcomes require inspection before replay. Code under `skills/`, `agents/` and `adapters/` has no diff from baseline: seven skills and three agents remain intact. Existing references and attribution are preserved.

Implementation commits:

- `ef3da38`: Node profiles, structured argv, authorization, process supervision and gate recovery.
- `db7c755`: optional read-only Codex executor, session checkpoints, explicit cost authorization, conservative replay and unit tests.

## Automated and local validation

The suite now contains **53 tests**, including the **38 unchanged original tests**. All passed on Windows during implementation (14.005 seconds in one recorded full run). It includes:

- Native adapter loading and canonical role/skill invariants.
- v1 persistence, transitions, backup restoration, locking, attempts and recovery.
- Actual Node runtime success, nonzero failure, subsequent recovery, and timed-out child-process cleanup.
- Missing Node/tool and authorization blocks; rejected commands, flags and traversal paths.
- All framework profile entrypoints/arguments verified with synthetic package manifests and mocked process execution.
- Codex JSONL parsing, metadata filtering, durable start/session checkpoints, missing provider, permission blocks, incomplete outcomes, timeouts, no automatic replay and exhausted budgets, using unit fixtures only.

Commands executed again during finalization:

```text
py -3 scripts/validate_skills.py
py -3 -m unittest discover -s tests -v
git diff --check
```

Finalization results: **53 tests passed in 18.155 seconds**; skill/link validator exit **0**; `git diff --check` exit **0**; all **six JSON example plans** accepted by the actual planner. The first finalization validator run correctly failed because README linked to this then-missing report; after adding this report the validator passed.

The versioned Node example was also exercised through real `create`, `run --allow-tests --test-profile node-test`, and `evidence` CLI commands. Task `4bb457e7404c4bfc916a09e55015c5e5` completed with one inspection attempt and a passing Node gate (exit 0, 0.734 seconds, termination confirmed). No package installation or provider call was used by these tests.

## One authorized real Codex smoke

Exactly one model invocation was authorized and executed. No retry or second paid smoke was performed during finalization. Preflight `--version` and `exec --help` are local CLI inspection, not model calls.

Command executed:

```text
py -3 scripts/smoke_harness_codex.py --allow-codex --codex-bin <installed @openai/codex/bin/codex.js>
```

- Codex CLI: **0.159.0**, installed authentication, synthetic temporary workspace.
- Fixed `read-only` sandbox, ephemeral execution, user config ignored except recognized Windows sandbox implementation; no bypass flags.
- Timeout: **120 seconds**; maximum attempts: **1**; attempts consumed: **1**.
- Task: `73dfcbd6b0824d5788d6a68deca2207d`.
- Native session: `01a182f2-d9e2-71c1-852b-b9679fd8e382`.
- Native `turn.completed`: true; completed command events: **1**; provider error: false.
- Exit code **0**, execution **11.703 seconds**, no timeout, termination confirmed, no truncated event capture.
- Independent SHA-256 gate passed in **0.266 seconds**; final Harness state **completed**.
- Initial and final fixture SHA-256: `47486da778cc80620af05eab659c27302288aed5cdb22752f6150da012c922b1`.

Durable history records step start at `14:38:35.550736Z`, session checkpoint at `14:38:36.184065Z`, step finish at `14:38:47.268256Z` and task completion at `14:38:47.576626Z`. This is native event evidence of real dispatch/completion plus independent fixture preservation, not a model's textual assertion. It does not prove broad semantic correctness, native specialist activation or hostile-code sandbox resistance.

Reported usage: **26,330 input tokens**, including **17,792 cached input tokens**, and **65 output tokens**. These are provider totals for this run, including native context. They do not isolate Harness overhead, establish a cost in currency, or demonstrate a before/after efficiency improvement. Ordinary local gates use no LLM; skill/agent prompt files did not grow.

The safe local JSON report is retained under ignored `.local-evidence/harness-v1.1/73dfcbd6b0824d5788d6a68deca2207d.json`. Raw stdout/stderr, model responses, transcripts and credentials were not versioned. The session ID is correlation metadata; ephemeral execution is not a persistent native session to resume.

## Added files and functional comparison

```text
harness/
  node_gates.py
  processes.py
  codex.py
scripts/
  smoke_harness_codex.py
tests/
  test_node_gates.py
  test_codex_executor.py
  evidence/harness-lite-v1-1.md
examples/harness/
  node-test.json
  sample.test.cjs
  node-project.json
  codex-inspect.json
```

Existing Harness planner, execution, gates, orchestrator, context, CLI and version metadata were extended. README, CHANGELOG and CI configuration were updated. v1 could inspect local files and execute Python validation; v1.1 additionally executes allowlisted installed Node tools and supervises opt-in Codex inspections. It does not introduce code-writing provider permissions.

## Not executed / limitations

- Actual Vitest, Playwright, ESLint, TypeScript, Vite and Next projects were **not** run. Their command contracts have unit coverage; the real Node demonstration uses `node:test`. PixelQuest was not available in this workspace.
- Linux/macOS runs and GitHub Actions results are **pending**. A three-OS Python/Node CI matrix is configured; no push was performed to trigger it.
- Claude operational smoke and native reviewer dispatch were **not** performed. Existing adapter tests are structural, not runtime compatibility proof.
- Codex is deliberately read-only. Project `.codex/config.toml` is refused by this executor; use an isolated workspace. Custom providers, write-mode execution, T3 integration and automatic specialist activation are not implemented.
- Gates execute trusted project code, not a sandbox. POSIX detached descendants, remote side effects and OS crashes are not comprehensively contained. Uncertain outcomes require human inspection; confirmations are not independent proof of termination.
- Raw outputs are discarded for privacy, reducing postmortem detail. Common-secret checks are not a comprehensive detector. Provider-native transport behavior is separate from the Harness's no-replay policy.
- The nine Gemini observations were referenced in the finalization request but their text was not present in available session context or repository Markdown. No unseen recommendation was treated as approval or claimed as implemented.

## Official interface sources

Consulted during implementation: [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [CLI commands](https://learn.chatgpt.com/docs/developer-commands), [sandbox and approvals](https://learn.chatgpt.com/docs/agent-approvals-security), and [T3 outside agents](https://github.com/pingdotgg/t3code/blob/main/docs/user/outside-agents.md). Installed CLI help confirmed the flags used. T3 has a documented MCP interface, but this Harness uses independent Codex CLI execution and makes no native T3 integration claim. No upstream code was copied.
