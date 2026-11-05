---
name: fde-delivery
description: Turn ambiguous stakeholder or field problems into scoped, measurable software delivery. Use when discovery, real-world constraints, integrations, pilots, adoption, or operational handoff matter.
---

# FDE delivery

Use for ambiguous stakeholder problems, field constraints, integrations and pilots. A well-defined application fix goes directly to software-engineering.

## Discover and scope

Infer from real artifacts where possible: operator, workflow, decision-maker, current workaround, measurable pain, security/privacy boundaries, system owner and adoption constraints. Ask only unresolved questions affecting delivery. Define an acceptance scenario; for a pilot, agree baseline, target, measurement owner/window and go/no-go criteria.

## Deliver in the actual environment

Build the smallest useful end-to-end workflow. Discover integration contracts, permissions, API/network constraints, failure behavior and audit requirements before expanding scope. Pilot with a representative operator, measure task completion and defects, and close the feedback loop.

Unavailable operator: label workflow assumptions and the validation dependency. Unavailable API/sandbox: use labeled fixtures and keep live compatibility unverified. Unclear ownership or deployment permission: prepare a reviewable handoff before the affected action. Continue independent work; do not retry an unchanged external blocker indefinitely.

## Handoff

A discovery delivers a bounded problem and acceptance scenario. A pilot delivers measured outcomes and an adoption decision. Operational handoff identifies owner, runbook, support/incident response, fallback/rollback and maintenance cost. Use briefs/diagrams/checklists only when useful. No deployment without approval; do not claim fixture success proves live operation.
