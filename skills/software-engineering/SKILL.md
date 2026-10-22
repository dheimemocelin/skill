---
name: software-engineering
description: Design, implement, debug, review, or test applications, backends, APIs, CLIs, and integrations. Use for software architecture, domain modeling, code changes, and reliability work.
---

# software-engineering


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
