# Project engineering guidance

Merge only applicable instructions into this project's existing guidance. Project conventions and authorization remain authoritative.

- BUILD: understand the domain and existing architecture, locate relevant code/callers/tests, define acceptance examples and implement a small compatible change. Plan proportionally; use appropriate types for this stack.
- Select relevant skills automatically from the task; users need not name them. Use engineering-os only for useful cross-disciplinary coordination. Work directly by default; specialist agents and the Harness are optional.
- REVIEW: check the diff, behavior, security and affected contracts. For UI, include visual hierarchy/identity, typography, responsive states, accessibility and rendered inspection when available. Never trade necessary validation for fewer tokens.
- Reuse existing tools and unchanged reads/checks. Expand investigation when evidence requires it. Keep test commands, scope, exit status, failures, errors, skips and truncation traceable; expose necessary sanitized details on failure.
- DELIVER: report result, actual verification and unresolved limitations once. Never invent tests, savings or visual approval. Stop when acceptance evidence is sufficient.
- Preserve unrelated work, secrets and sensitive data. Honor approvals; commit/push only when authorized. Never merge, deploy, publish or perform destructive operations without authorization.
