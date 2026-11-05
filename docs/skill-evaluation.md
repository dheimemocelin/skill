# Skill change evaluation

Use when changing canonical skills or their activation descriptions. Reuse `scripts/validate_skills.py`, adapter tests and the existing provider smoke runner; do not install a second skill framework.

1. Record the behavior to improve and retain the previous revision for comparison.
2. Choose realistic positive, negative and ambiguous requests. Specify expected outcomes and forbidden side effects before the run; do not prescribe wording.
3. Run structural validation and adapter tests. Verify conditional references are copied and resolve in both provider layouts, without preloading their bodies into agent instructions.
4. When a real provider run is authorized and available, use the existing isolated smoke runner. Compare the same task, fixtures and provider settings with the previous skill. Separate activation evidence, task correctness and cost/latency observations. Capture native events and exact skill/config hashes; self-reported skill use is insufficient.
5. Inspect failures, make bounded corrections and repeat affected cases. Report unexecuted cases explicitly; deterministic routing tests do not establish natural-language selection quality.

## Evaluation requests for this change

| Request | Expected selection/outcome | Failure signal |
| --- | --- | --- |
| Review a staged authorization change while unstaged edits exist | git-quality; inspect the index version and tenant boundary | Finding based only on unstaged code; unauthorized edits |
| Choose between a queue and a synchronous call for a low-volume API | software-engineering; compare constraints and smallest alternative | Adds distributed components without evidence |
| Build an MCP tool that updates a customer record | ai-engineering plus software-engineering; scoped authorization, schema and write replay checks | Treats read-only annotations as enforcement |
| Explain what MCP means | Direct explanation | Starts a server or installs dependencies |
| Correct a typo in the README | Direct edit | Loads architecture/MCP references or dispatches reviewer |
| Improve signup latency with no measured bottleneck | software-engineering; inspect evidence before optimization | Applies framework-specific caching blindly |
| Make the signup error easier to understand | ui-ux-design; preserve input and clarify recovery | Replaces backend architecture |

This table is a manual behavioral evaluation specification, not an executed benchmark. Do not score a skill 9/10 solely because structure or unit tests pass. Runtime records follow the existing [evidence policy](../tests/evidence/README.md).

The [2026-11-05 behavioral evaluation](behavioral-evaluation.md) provides reproducible paired scenarios and actual provider outcomes, including infrastructure blocks. Run the opt-in evaluator only when provider use is intended.
