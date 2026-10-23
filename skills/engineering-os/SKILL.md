---
name: engineering-os
description: Orchestrate end-to-end or cross-disciplinary engineering work across software, AI, data, UX, and delivery. Use when a request spans specialties or needs a proportional plan from discovery through review; use a specialist directly for a narrowly scoped task.
---

# engineering-os


## First principles
Build the smallest safe increment that solves a real problem. Preserve existing code and user edits. Inspect project instructions, repository status, runtime constraints and tests before changing files. Avoid architecture theater, speculative abstractions and undisclosed assumptions.

## Select execution roles and skills
Skills are the single source of reusable knowledge and procedures; agent definitions own bounded execution. Load only relevant skills. The canonical mapping from agent to skill library is the `skills` metadata in `agents/<role>.md`; do not maintain a second routing table here.

The supported specialist roles are Software Engineer, AI Engineer, and Quality Reviewer. Data Engineering, UI/UX, and FDE remain available as skills, not agents. Use a specialist only when its domain ownership materially improves correctness or keeps a substantial independent workstream out of the coordinator's context. For small focused tasks, work directly. Use one specialist by default; parallel agents only for concrete, independent workstreams that will not edit the same files. Quality Reviewer performs independent review and must not repeat implementation.

Claude Code and Codex have different native discovery, invocation, and permission models. Use the native adapter; do not infer that a role is available because its files exist. If no supported subagent mechanism is available, work directly and load only relevant skills. Agent instructions never override project restrictions or human approval requirements.

## Workflow (inspired by Matt Pocock's small, composable engineering skills)
1. **Discover:** inspect repository, business context, git diff, tests and integration contracts. For an existing codebase, do not rewrite by default.
2. **Model:** entities, invariants, user journeys and failure modes; use domain modeling when ambiguity affects correctness.
3. **Specify:** objective, acceptance criteria, constraints, edge cases, smallest vertical slice. For tiny tasks use a short inline checklist rather than a document.
4. **Slice:** break complex requirements into verifiable independent tasks; order by risk and dependencies.
5. **Build:** follow repository conventions; write tests for risky behavior; change only necessary files.
6. **Verify:** execute available lint/types/unit/integration/e2e/build as relevant; capture actual command results; do not claim unrun checks passed.
7. **Review:** separate specification correctness from code maintainability; inspect diff, security, privacy, accessibility, operations and rollback impact.
8. **Record:** update tests/docs/decisions and create authorized scoped commits in task branch.
9. **Improve:** note evidence-based follow-ups, but do not quietly expand scope.

## Work-size policy
- Small fix: inspect -> patch -> focused test -> diff -> commit if allowed.
- Feature: short spec + acceptance tests + incremental implementation + review.
- Complex or high-risk system: domain boundaries, ADR, threat modeling, rollout/rollback, human approval gates and eval evidence.

## Nonnegotiables
Never fabricate data, tests, external tool results or model evaluation. No secrets or sensitive data in prompts, commits or logs. No automatic merge, push, deploy, destructive migration or force push without explicit permission. No dependency upgrade for novelty. Use current official docs for version-specific APIs. Prefer reversible decisions. Treat third-party repositories as optional, versioned dependencies; do not claim bundled functionality that is not present.

## Output
Summarize Delivered; Evidence (commands and results); Not verified; Risks; Branch/commit if actually created; and Next highest-impact improvement.
