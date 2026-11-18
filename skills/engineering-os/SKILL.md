---
name: engineering-os
description: Coordinate a task that spans several disciplines at once, such as a feature touching backend, database, UI and release, a data pipeline feeding a dashboard, or an AI feature with an API and an interface. Use when the user asks to build or ship something end-to-end, or to resume multi-stage work from an earlier session. For a single-area task, use that specialty skill directly.
---

# Engineering OS

Use only for cross-disciplinary work where coordination helps; otherwise work directly in one specialty.

## Route

| Part of the task | Skill |
|---|---|
| Code, API, bug, tests | software-engineering |
| LLM, RAG, agents, MCP | ai-engineering |
| SQL, pipelines, metrics | data-engineering |
| Screens, flows, accessibility | ui-ux-design |
| Unclear field problem, pilot | fde-delivery |
| Review, commit, PR, release | git-quality |

Load only skills needed for the current step. The metadata in agents/<role>.md is the canonical agent-to-skill mapping. Default to direct work or one specialist; delegate only bounded, independent work.

## Steps

1. **Resume:** for continued work, recover the original goal and user corrections, then compare claims with current branch, commits, files, and validations. Preserve edits and authorship; resume pending work only.
2. **Plan:** write observable acceptance criteria (input → expected outcome) and an ordered list of slices with the skill for each. Order: data contract → backend → UI → review → delivery.
3. **Build:** one slice at a time, smallest compatible change, secure defaults, no unrelated edits.
4. **Review:** focused checks per slice plus the full diff; visual and accessibility checks when UI changed.
5. **Deliver:**

```
**Result:** what works now, per acceptance criterion (met / not met)
**Checks run:** command → result
**Not verified / risks:** …
**Needs approval:** merge, deploy, data change, if any
```

## Guardrails

- Human approval is required for merge, deploy, publication, destructive operations and external side effects.
- Never expose secrets or claim unrun checks. Keep failures, skips and truncation visible.
- No real personal data in code, fixtures, logs or prompts.
- Stop when acceptance criteria are met.
