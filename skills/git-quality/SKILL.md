---
name: git-quality
description: Safe Git operations and change review. Use when the user asks to review a diff, staged changes, a branch or a pull request, write a commit or commit message, create or switch branches, open or update a PR, check CI results, or prepare a release or changelog. Not for writing the code change itself (software-engineering).
---

# Git quality

Keep the repository safe, reviewable and traceable. Permission is narrow: a review does not authorize edits, a commit does not authorize push, and a push does not authorize merge or release.

## 0. Look before acting

Always run first: `git status`, `git branch --show-current`, `git log --oneline -5`, and `git remote -v` when pushing. Note uncommitted work that is not yours — it must survive whatever you do.

Learn the repo's conventions from `CONTRIBUTING.md`, `CLAUDE.md` / `AGENTS.md`, recent commit messages and CI config. If none exist, use `type(scope): summary` (types: feat, fix, refactor, test, docs, chore), imperative, ≤ 72 characters.

## 1. Review a change

1. Establish exactly what is being reviewed: staged index (`git diff --cached`), a commit, a branch against its merge base (`git diff main...HEAD`), or working files. Read callers and tests **from that same version**.
2. Read the full diff, then the surrounding code of each changed function and its consumers.
3. Apply [code review checklist](references/code-review.md).
4. Report findings in this format, most severe first:

```
[high] src/orders/service.py:88 — tenant_id not checked before update
  Impact: any authenticated user can edit another company's order.
  Evidence: update_order() loads by id only; compare get_order() line 41.
  Fix: filter by (id, tenant_id) and return 404 when absent.
```

Severity: `critical` (security breach, data loss), `high` (wrong behavior in a main path), `medium` (edge case, missing test for risky logic), `low` (minor robustness). Style goes under `nit`. Separate confirmed defects from questions. "No material findings" is a valid result — do not invent issues.

## 2. Commit (only when authorized)

1. Stage selectively (`git add <paths>` or `git add -p`), never `git add -A` on a tree with unrelated changes.
2. Inspect `git diff --cached` before committing. **Never stage** `.env` files, credentials, keys, certificates, database dumps, exports with personal data, or large generated artifacts. If one is already tracked, stop and tell the user.
3. Run the project's relevant tests/lint before committing.
4. One logical change per commit, message in the repo convention, body explaining *why* when not obvious.

## 3. Branches, push and PRs

- Use a task branch for non-trivial work when the repo workflow allows.
- For authorized PR creation or CI follow-up, load [PR delivery](references/pr-delivery.md).
- **Always require explicit approval for:** push to a shared branch, merge, rebase or history rewrite of shared commits, force-push, tag/release, deploy, deleting branches.
- On CI failure, read the log, separate code defects from infrastructure/flaky failures, fix only in-scope problems.

## 4. Release (only when asked)

Check the changelog and version convention, list included changes since the last tag (`git log <last-tag>..HEAD --oneline`), flag migrations and breaking changes with rollback notes. Prepare; do not publish without approval.

## Deliver

```
**Operation:** what was done (review / commit abc123 / PR #12 opened)
**Checks:** command → result, with failures, skips and truncation visible
**Pending human action:** e.g. approve merge, rotate exposed key
```

Missing tools or credentials mean *unverified*, never *passed*.
