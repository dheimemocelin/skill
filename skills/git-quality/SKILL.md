---
name: git-quality
description: Manage safe Git workflows, focused commits, CI, code review, security checks, and releases. Use when changing branches, preparing commits, reviewing versioned changes, or planning a release.
---

# git-quality


## Git policy
- Inspect `git status`, current branch, remote and recent commits before modifications; never discard uncommitted work.
- Use a named task branch for significant work where the repository allows; isolate changes from unrelated work.
- Stage only intended files and inspect staged diff. Write focused imperative Conventional Commits where consistent with repo conventions (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`).
- Each commit should leave the branch in a coherent state when practical; do not stage `.env`, credentials, private user data, large generated artifacts or unrelated changes.
- Auto-commit per completed validated task ONLY where explicitly authorized by the user's standing project instructions. Otherwise provide the commit plan without taking action.
- Do not merge, force-push, rewrite history, publish or deploy without explicit approval; pushing is not implied by committing.

## Review and optional PR delivery
- For authorized PR creation or CI follow-up, load [PR delivery](references/pr-delivery.md). PRs and continuous monitoring are optional.
- Review the final diff against the task and branch base; run appropriate tests before committing and inspect staged content. Keep commits small and traceable.

Use existing CI as source of truth; for a new project propose minimally useful formatting/lint, tests, build and secret scanning. Treat migration changes separately with backup/rollback steps. Add a changelog entry/tag for meaningful skill releases; test skill triggers on representative prompts and ensure no conflicts.

## Continuous improvement
Log failures/overheads observed in real tasks; rank by recurrence and impact; change one instruction at a time, evaluate regression examples, version and document results.
