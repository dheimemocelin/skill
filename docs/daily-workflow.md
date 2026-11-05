# Daily workflow and simplification decisions

Engineering OS is a library of seven specialties and three optional roles. It does not install a scheduler, proxy, model router or service. The chosen development environment supplies execution tools and enforces permissions. Canonical practices do not require a particular editor or orchestration product; adapters bridge specific native formats. BUILD, REVIEW and DELIVER describe ordinary work, not a new framework.

## Select context and investigate

Use task descriptions to discover relevant skills without user-supplied names. Focused work goes directly to its specialty; engineering-os coordinates only genuinely cross-disciplinary work. Keep native role metadata canonical. Agents can isolate independent responsibility, but delegation itself adds work and model usage.

Find relevant files/symbols with targeted search before reading implementation, consumers and tests. Expand based on evidence; a fixed line budget is not an architecture review. Reuse unchanged reads and project commands, but recheck evidence after relevant source/configuration/dependency changes. Do not create a generic command cache. Matt Pocock-inspired domain modeling, explicit contracts, types appropriate to the stack, test-first risky paths and evidence-driven debugging remain in software-engineering.

## Traceable output and communication

Prefer a test runner's existing concise mode when it preserves useful outcomes. Keep command, scope, exit code, failures, errors, skipped/unexecuted checks and truncation visible. On failure, inspect necessary sanitized diagnostics from the original local source. Do not mask the runner's exit code with a pipe; do not blindly use head/tail as proof of successful execution. A zero exit with no discovered tests is not coverage. Do not persist credentials or customer payloads just to make a log recoverable. If complete safe diagnostics are unavailable, label the evidence incomplete.

Summarize successful routine work once: result, actual verification, remaining limitations. Progress updates communicate discoveries/decisions rather than repeating plans or full logs. Detailed audit/release reports are conditional. Security warnings, authorization boundaries, numbers, negations and needed technical explanations remain intact.

## Visual quality

UI tasks require product identity, hierarchy, typography, spacing/alignment, responsive layout, semantic interactions, keyboard/focus, contrast and useful states. Preserve Impeccable-inspired critique and finishing. DOM/code checks cannot establish visual quality; missing rendering or interaction tools remain an explicit validation gap in that environment. Use any available approved renderer and interaction tools; none is a platform requirement. Never approve an unrendered design merely because its HTML contains accessibility keywords.

## What remains optional

Harness source, checkpoint schema, retries, CLI and opt-in gates are unchanged. Its guide moved out of the README; ordinary tasks need no Harness JSON. Agent adapters retain provider-specific formats and permissions. Installation is project-scoped by default; updates use fresh staging and reviewed merges, not overwriting consumer files. Generated output is disposable; references removed upstream must be reviewed explicitly on update because copytree does not delete stale files.

## Efficiency evidence

These are independently written, bounded process improvements informed by the Caveman review at revision 2e068f735253cce28256744804785f01887d9646. No Caveman code, instructions, hooks, telemetry, proxy or dependencies were copied or installed. See [accounting principles](https://github.com/JuliusBrussee/caveman/blob/2e068f735253cce28256744804785f01887d9646/docs/technical/accounting-and-evidence.md). Shorter Markdown/output is not provider savings.

Natural-request fixtures in examples/behavioral/daily-work-cases.json compare source baseline 06770ff with this branch. The existing evaluator installs each variant's project template and skill bodies; agents are available, not requested. Independent fixture assertions test behavior after the model run. UI assertions check only static structure and are not visual approval. A real model call uses the configured provider/model and explicit sandbox; no service is contacted by the AI-agent fixture itself.

Reuse native session usage counters, including parent and child sessions when supported; missing usage is unknown. Include failed/no-op runs, cache input, output and repeat checks in observations. A single pair, fixed order and different cache hit rates cannot support a general efficiency claim. Keep task quality/security and technical measurement distinct. Native trace/bytecode-scorer limitations and any reclassification must remain visible in the report.
