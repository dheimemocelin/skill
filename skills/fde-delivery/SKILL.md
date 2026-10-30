---
name: fde-delivery
description: Turn ambiguous stakeholder or field problems into scoped, measurable software delivery. Use when discovery, real-world constraints, integrations, pilots, adoption, or operational handoff matter.
---

# fde-delivery


## Start with a concrete discovery

Use for “Scope a warehouse pilot across our scanner and ERP.” A well-defined endpoint fix belongs to software-engineering directly.

Ask or infer from artifacts: Who performs the task? What happens today? Where does it fail? What constraints block improvement? Who owns the success measurement and operational support? Ask only unresolved questions that affect the current delivery decision.

For a small integration, a brief acceptance scenario and owner may suffice. For a pilot, agree on baseline, target, representative operator, measurement window, failure handling and go/no-go decision before rollout. Use the cycle below as applicable.

## Work with unavailable dependencies

- No operator access: document the workflow hypothesis from available artifacts and schedule operator validation as an explicit dependency.
- No API or sandbox: inspect contracts and use clearly labeled fixtures for development; track live compatibility separately.
- Unclear ownership or deployment permission: prepare a reviewable handoff and identify the responsible decision-maker before the affected action.

Do useful independent work while dependencies are unresolved. Stop retries when the same external constraint prevents further evidence.

## Completion

A discovery ends with a bounded problem and acceptance scenario. A pilot ends with measured results against agreed targets, unresolved defects and an explicit adoption decision. A handoff identifies owner, support, fallback and remaining dependencies. Example: “The operator completed the fixture workflow; ERP sandbox access is required before integration acceptance.”


## Field-engineering cycle
- Understand user workflow on site or from concrete artifacts; identify decision-maker, operator, constraints, current workaround and measurable pain.
- Identify security/privacy/compliance boundaries, ownership, permissions, unavailable APIs, operational environment and adoption risks.
- Define success in operational terms: baseline, target, measurement owner and go/no-go criteria.
- Deliver the smallest end-to-end useful workflow before integrating every system.
- Build for actual environment: contract discovery, realistic sandbox, integration error handling, network constraints, auditability and support playbook.
- Pilot with a representative operator, record defects and task completion, close the feedback loop.
- Hand off runbook, ownership, incident response, fallback/rollback and maintenance costs. No deployment without approval.

## Artifacts only when useful
One-page problem brief, system/context diagram, integration contract, acceptance scenario, handoff checklist. Avoid lengthy decks for tiny tasks.
