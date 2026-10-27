# Provider smoke-test evidence

Run the real provider suite with `python scripts/run_agent_smoke_tests.py --provider <claude|codex|all>`. Each case runs in an isolated temporary Git project populated from the generated native adapter. The script stores raw provider JSONL, stderr, fixture snapshots, CLI version, installed configuration hashes, and a sanitized summary under `.local-evidence/agent-smoke/` (ignored by Git).

For Codex, the summary includes per-response input, cached-input, output, and total token counters aggregated across parent and child sessions. These counts cover the whole provider session (host instructions, prompts, skills, agent work, and tool turns); they do not isolate the token cost of an individual skill. Compare equivalent runs with the same provider version and fixtures before attributing a difference to a skill change.

Use `--skill-override NAME=PATH` to run a controlled before/after case with a prior `SKILL.md` body in the isolated fixture. The summary stores only the override's SHA-256, not the source path or its contents.

Only `summary.json` is designed to be safe for sharing/versioning. Review it for accidental sensitive content before adding any evidence to Git. Never commit transcripts, prompt logs, credentials, environment dumps, or fixture data copied from a real project. The committed fixture definitions contain synthetic code only.

## Evidence standard

- **Discovery:** agent/skill files exist at the provider's documented project paths, and the CLI version plus exact installed config hashes are captured.
- **Activation:** count only provider-native structured dispatch or skill-load events. For Codex CLI, the runner inspects the local session metadata's `agent_role` and verifies exact skill bodies in the parent/child session records because `codex exec --json` does not expose all collaboration metadata. A model saying it used an agent or skill is not evidence.
- **Execution:** verify the isolated fixture's expected change/finding and initial/final hashes; for Quality Reviewer also verify the fixture did not change.
- **Negative routing:** conceptual, explanation, documentation typo, and non-delegation prompts must produce no specialist dispatch events.
- **Unavailable or unauthenticated provider:** record as `not_run`/`blocked`; never count as pass.

The providers expose different event formats and capabilities. If a provider does not expose structured skill activation in CLI output or local session records, report that limitation instead of inferring activation from response text or file presence.
