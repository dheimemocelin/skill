---
name: git-quality
description: Manage safe Git workflows, focused commits, CI, code review, security checks, and releases. Use when changing branches, preparing commits, reviewing versioned changes, or planning a release.
---

# git-quality


## Risk-focused review

When reviewing architecture, public contracts, dependencies or security boundaries, read [Architecture and regression review](../software-engineering/references/design-review.md). The existing Quality Reviewer remains the independent review role.


## Select the requested operation

| Request | Work to perform | Completion evidence |
| --- | --- | --- |
| Review changes | Inspect diff, context and relevant checks | Actionable findings with file locations and severity |
| Prepare or create commit | Inspect state, isolate intended changes, inspect staged diff | Proposed commit or authorized commit hash |
| Create/update PR | Read the conditional PR delivery reference below | PR link, scope and checks/review state |
| Release | Confirm version scope, compatibility, changelog and rollback | Release artifacts and authorized publication status |

“Review this diff” activates this skill without authorizing edits or commits. A plain text correction can use direct editing; load this skill when Git delivery or review is part of the task.

## Existing changes and blockers

Inspect unrelated edits and leave them intact. If intended and unrelated changes share a file, use selective staging and inspect the staged result; ask only when ownership cannot be established safely. Reuse authorization already given for the specific operation; do not infer permission for a later external action.

If tests, remotes or credentials are unavailable, complete local preparation and report the exact blocked action. Never label unavailable checks as passed. For a review-only request, test execution depends on available authorization and value to the finding.

## Completion

Report the operation performed, relevant diff/check evidence and remaining action. Example: “The requested commit contains only the retry fix; focused tests passed; no PR was requested.” Apply the policies below only to the operation in scope.


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
