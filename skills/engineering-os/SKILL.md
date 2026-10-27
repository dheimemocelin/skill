---
name: engineering-os
description: Coordinate multi-stage engineering work across disciplines; use a focused skill or agent directly for narrow tasks.
---

# Engineering OS

Use this router only when coordination materially improves a cross-disciplinary or multi-stage task. For a focused request, work directly with the relevant skill.

## Route work

- Skills provide reusable knowledge; agents perform bounded work. The `skills` metadata in `agents/<role>.md` is the canonical agent-to-skill mapping.
- The available agents are Software Engineer, AI Engineer, and Quality Reviewer. Data Engineering, UI/UX Design, and FDE remain skills.
- Load only skills needed for this task. Check that the provider's native adapter supports an agent before dispatch; if unavailable, work directly.
- Default to direct work or one specialist. Delegate only when specialist ownership materially improves correctness or isolates substantial independent work. Parallelize only independent work that will not edit the same files.

## Execute proportionally

1. Inspect the request, relevant repository guidance, files, Git state, and available tests. Preserve unrelated user changes.
2. Define observable acceptance criteria. Use a short checklist for small tasks; specify, plan, and split complex or risky work.
3. Implement the smallest safe change using project conventions and evidence-based assumptions.
4. Run focused checks that cover changed behavior and likely regressions. Review the diff, security, error handling, observability, and documentation where relevant. Report only checks actually run.
5. Record meaningful changes and leave a reviewable result. Commit only when authorized and on the task branch.

## Safety and completion

Preserve existing work; use secure defaults, clear failure signals, and reversible changes. Reuse existing dependencies. Never expose secrets or claim unrun checks. Follow project restrictions and current documentation for version-sensitive work. Human approval is required for consequential external actions, destructive operations, merge, deploy, or publication.

Report the outcome, focused validation, limitations, and any needed handoff. Skip formal planning for routine edits; do not skip checks needed to establish correctness.
