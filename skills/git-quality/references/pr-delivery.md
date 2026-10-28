# Optional PR delivery

Load this procedure only for authorized PR creation or requested CI/review follow-up.

1. Review the final diff against the task and branch base. Run appropriate checks before committing and inspect staged content. Keep commits small and traceable.
2. Create or update a PR only when authorized. State intent, checks, and known gaps. Use a supported Git host interface; GitHub CLI is optional.
3. Check CI and review status with available capabilities. Verify findings against code, fix in-scope issues, and distinguish defects from infrastructure failures or false positives.
4. Monitoring is optional. Prefer a supported native watcher; otherwise use a bounded wait. Never wait indefinitely or run a poll/sleep loop. If monitoring is unavailable or times out, report the last observed state and limitation.
5. Hand off with the PR link and head when available, CI/review state, checks run, unresolved findings, limitations, and next human action. Stop when ready for human approval.

Never merge, enable auto-merge, deploy, or bypass branch protection. Never force-push without explicit authorization or overwrite another contributor's changes.
