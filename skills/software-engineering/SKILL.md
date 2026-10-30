---
name: software-engineering
description: Design, implement, debug, review, or test applications, backends, APIs, CLIs, and integrations. Use for software architecture, domain modeling, code changes, and reliability work.
---

# software-engineering


## Choose a working path

| Task | Essential path | Completion evidence |
| --- | --- | --- |
| Bug | Reproduce, isolate cause, fix narrowly, check regression | Original failure resolved and nearby behavior checked |
| Feature | Define observable behavior, implement one useful slice, check boundaries | Acceptance examples demonstrated |
| Refactor | Identify behavior to preserve, change incrementally | Relevant behavior checks and reviewed diff |
| Review | Inspect requested scope and callers, substantiate findings | Findings with location, impact and evidence; no edits unless requested |

Use this skill for “Fix duplicate order submission.” Use data-engineering for “Explain why the revenue totals disagree”; add this skill if application code needs repair.

For a small change, use existing context and a short acceptance checklist. Create architecture documents or tickets only when they resolve a real coordination or design need. Select checks by changed behavior and risk; do not require every tool listed below for every task.

## Missing context and completion

Inspect callers, configuration and existing conventions before asking questions. If reproduction is unavailable, distinguish observed evidence from hypotheses and identify the smallest missing input. Avoid speculative fixes.

Finish with behavior changed, relevant checks actually run, and any unresolved limitation. Example: “Repeated submissions now reuse the same order; the duplicate-request regression passes; payment-provider integration was unavailable.”


## Workflow (Matt Pocock-inspired, adapted)
- Model the domain: ubiquitous language, entities, state transitions, invariant checks and persistence boundaries.
- Convert the goal into observable acceptance criteria. For large tasks split into tickets ordered by value and dependencies.
- Select the simplest compatible architecture: cohesive modules, explicit contracts, typed boundaries, dependency direction and low coupling.
- Apply test-first for domain invariants, bug reproduction and risky paths; avoid forcing TDD on trivial formatting.
- Diagnose bugs with reproduction -> evidence -> hypotheses -> targeted fix -> regression test. Do not shotgun-change files.
- Implement a thin end-to-end slice before multiplying modules. Keep migrations reversible where feasible.
- Review two axes: requirements/behavior and code health. Consider reliability, accessibility, security, profiling and maintainability.
- For APIs, check versioning, validation, authorization, idempotency, timeouts, pagination and error surfaces as applicable.
- Refactor in separate small commits when possible. Avoid blanket rewrites, 'future proofing' without evidence and overengineering.

## Evidence
Tests, lint, typecheck, build, contract/integration checks appropriate to the stack; note any not executed.
