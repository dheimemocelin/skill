# PR delivery

Load this procedure only for authorized PR creation or requested CI/review follow-up.

## 1. Prepare

Review the final diff against the task and the branch base (`git diff <base>...HEAD`). Run appropriate checks before committing and inspect staged content. Keep commits small and traceable. Confirm the branch is pushed and tracks its remote (`git status -sb`) before opening the PR.

## 2. Open or update

Create or update a PR only when authorized. Use a supported Git host interface; GitHub CLI is optional. With it:

```bash
gh pr create --base main --head <branch> --title "<type(scope): summary>" --body-file <body.md>
gh pr view --json url,headRefOid,state
```

Use the repository's PR template when one exists (`.github/pull_request_template.md`). Otherwise:

```
## What and why
One paragraph: the problem and the chosen change.

## Checks
- `<command>` → passed (N tests)
- Not run: <check> — <reason>

## Risks and rollback
Migrations, config or contract changes; how to revert.

## Notes for reviewers
Where to look first; open questions.
```

Do not put secrets, personal data or internal hostnames in titles, bodies or comments.

## 3. Follow CI and review

Check CI and review status with available capabilities (e.g. `gh pr checks <n>`). Read the failing job log, verify each finding against the code, fix in-scope issues, and distinguish defects from infrastructure failures, flaky tests or false positives. Reply to review comments with what changed or why not.

Monitoring is optional. Prefer a supported native watcher; otherwise use a bounded wait. Never wait indefinitely or run a poll/sleep loop. If monitoring is unavailable or times out, report the last observed state and limitation (e.g. "macOS job still queued at 14:20").

## 4. Hand off

Report the PR link and head commit when available, CI/review state per job, checks run, unresolved findings, limitations, and the next human action. Stop when ready for human approval.

Never merge, enable auto-merge, deploy, or bypass branch protection. Never force-push without explicit authorization or overwrite another contributor's changes.
