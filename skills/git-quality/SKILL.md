---
name: git-quality
description: Manage safe Git workflows, focused commits, CI, code review, security checks, and releases. Use when changing branches, preparing commits, reviewing versioned changes, or planning a release.
---

# Git quality

Use for versioned review, branches, commits, CI and releases. A review does not authorize edits; a commit does not authorize push or publication.

## Preserve and scope

Inspect status, branch, remote and recent commits. Preserve uncommitted/unrelated work and authorship. Use a task branch for significant changes where permitted. Selectively stage mixed files; ask only if ownership cannot be resolved safely. Never stage credentials, private customer data, large unrelated generated files or environment files.

## Review

Establish the requested revision/index/diff and inspect its consumers and relevant checks. Report actionable findings with location, failure scenario, impact and evidence; distinguish defects from uncertainty and style. The existing Quality Reviewer is the optional independent role. For architecture, public contracts, dependencies or security boundaries, read [Architecture and regression review](../software-engineering/references/design-review.md).

## Deliver authorized Git work

Inspect staged content and run appropriate checks before committing. Prefer focused, coherent commits and the repository's commit conventions. Commit only when authorized; reuse authorization already given for the operation. Do not merge, force-push, rewrite history, publish or deploy without explicit approval.

For authorized PR creation or CI follow-up, load [PR delivery](references/pr-delivery.md). Use existing CI and tooling; do not install scanners or add release mechanisms automatically. Treat migrations with appropriate rollback and update changelog/version information when relevant.

Report the operation, checks and remaining action. Test summaries keep command/scope, exit status, failures, errors, skips and truncation visible; missing tools or credentials mean unverified/blocked, never passed. Keep necessary sanitized failure details recoverable without exporting secrets. Avoid repeated narrative reports after the evidence is complete.

Improve instructions from observed failures, one bounded change at a time, with representative positive/negative evaluation cases. Reuse still-current checks; never claim savings from shorter prose alone.
