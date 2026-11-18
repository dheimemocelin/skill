# Project engineering guidance for Claude Code

Follow existing project guidance and AGENTS.md when present. Select relevant skills from the user's task; engineering-os is optional for cross-disciplinary coordination. Work directly unless a bounded specialist adds value. Agents and the Harness are optional.

Use the project's conventions, approvals and native tool permissions. Do not assume tools or hooks from Codex, Impeccable or other referenced projects exist here. Report actual checks and limitations; do not overwrite project customizations with this template.

## Project conventions (fill in — this is what makes the skills project-specific)

- Stack: <language + version, frameworks>
- Run tests: `<command>` · Lint: `<command>` · Typecheck: `<command>` · Build: `<command>`
- Code layout: <where source, tests and migrations live>
- Commit messages: <convention, e.g. `type(scope): summary`>
- Branches and PRs: <naming, base branch, who approves>
- Never do: <e.g. edit generated files, touch `legacy/`, run migrations locally against shared DBs>

## Data and security policy

- Never write credentials, tokens, keys or connection strings in code, tests, logs, commits or chat; use environment variables or the approved secret store. If one is exposed, do not repeat it and tell the user to rotate it.
- Never use real personal data in code, fixtures, logs, prompts or screenshots; use synthetic data. Follow the organization's AI usage policy and applicable privacy law (e.g. LGPD).
- Replace this section with your organization's policy link and rules when available.
