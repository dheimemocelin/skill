---
name: software-engineering
description: Design, implement, debug, review, or test applications, backends, APIs, CLIs, and integrations. Use for software architecture, domain modeling, code changes, and reliability work.
---

# Software engineering

Use for application/API/CLI implementation, debugging and technical design. Metric reconciliation belongs to data-engineering; add ui-ux-design when interface behavior or appearance changes.

## Investigate and build — Matt Pocock-inspired practices

- Locate relevant symbols, implementations, consumers and tests before editing. Distinguish observed failures from hypotheses; reproduce bugs and falsify causes with focused checks. Ask for missing context only when it changes a decision.
- Model domain language, entities, state transitions, invariants and persistence boundaries. Define observable acceptance examples. Split complex work by value and dependencies; routine changes need no separate tickets or design document.
- Follow existing architecture. Prefer cohesive modules, explicit contracts, typed boundaries and one end-to-end slice. Use TypeScript's type system where applicable; use the project's equivalent in Python or other stacks. Do not force a language, dependency or abstraction.
- Bugs: reproduce, isolate cause, fix narrowly, check regression. Features: implement acceptance examples and boundary cases. Refactors: preserve behavior in small steps. Test-first is useful for invariants and risky paths, not mandatory for formatting.
- For APIs, assess input validation, authorization, versioning, idempotency, timeouts, pagination and error contracts as relevant. Keep migrations reversible where feasible; avoid speculative scaling and blanket rewrites.

## Review and evidence

Review requirements/behavior and code health: error paths, cleanup, security, compatibility, accessibility and performance where affected. Use existing test/lint/typecheck/build tools and avoid repeating unchanged successful checks. A regression check must expose the original defect, not merely mirror the implementation.

For material architecture decisions, changed public contracts, dependency/security review or browser regression planning, read [Architecture and regression review](references/design-review.md). Apply only relevant checks.

Report changed behavior, commands with scope and actual results, and remaining gaps. Preserve failure details, skips and blocked checks; do not treat truncated output or unavailable integration as success. Review-only requests produce findings without edits unless authorized.
