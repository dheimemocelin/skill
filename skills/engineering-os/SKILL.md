---
name: engineering-os
description: Orchestrate end-to-end or cross-disciplinary engineering work across software, AI, data, UX, and delivery. Use when a request spans specialties or needs a proportional plan from discovery through review; use a specialist directly for a narrowly scoped task.
---

# engineering-os


## First principles
Build the smallest safe increment that solves a real problem. Preserve existing code and user edits. Inspect project instructions, repository status, runtime constraints and tests before changing files. Avoid architecture theater, speculative abstractions and undisclosed assumptions.

## Select specialist skills
- `software-engineering`: application, API, integration, performance, debugging, architecture and tests.
- `ai-engineering`: agents, LLM prompts/tools, RAG, evals, guardrails and costs.
- `data-engineering`: ETL/ELT, data quality, SQL, semantic metrics, BI and analysis.
- `ui-ux-design`: UI flows, design systems, accessibility and frontend finish.
- `fde-delivery`: client problem discovery, constraints, deployment and measurable outcomes.
- `git-quality`: branches, commits, CI, security scans, changelog and release controls.

Read ONLY relevant specialists. Compose specialists for cross-cutting tasks (e.g. dashboard -> data + UI + software + Git; AI assistant -> AI + software + FDE + Git). Specialist directions never override project restrictions or human approvals.

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
