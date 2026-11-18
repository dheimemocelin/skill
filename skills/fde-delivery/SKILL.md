---
name: fde-delivery
description: Turn a vague business or operational problem into a scoped, measurable software delivery. Use when the user brings a stakeholder request, a manual process to automate, an integration with an external system or ERP, a pilot or proof of concept, adoption problems, or a handoff to operations. Not for a clearly specified code change (software-engineering).
---

# Field delivery

Go from "we have a problem" to a small working solution that real users adopt, with a measurable result.

## 1. Discover

Use real artifacts first (spreadsheets, screenshots, current process, tickets, system docs) and fill this brief. Ask only for what is missing and blocks delivery.

```
Problem: what hurts, in the user's words
Who: operator (does the work) / decision-maker / system owner
Today: current workaround and its cost (time, errors, rework)
Systems: what must be read or written, and who controls access
Constraints: security, personal data, approvals, deadlines
Success: one measurable outcome (e.g. "closing takes 1 day instead of 3")
```

Example, filled:

```
Problem: "Every month-end we retype 400 supplier invoices from e-mail into the ERP."
Who: 3 AP clerks / controller / ERP admin team
Today: ~2 days per closing, ~3% retyping errors found in audit
Systems: shared mailbox (read), ERP payables API (write, sandbox available)
Constraints: invoices contain supplier tax IDs; ERP writes need controller approval
Success: invoice entry under 4 hours per closing, errors under 1%
```

## 2. Scope the smallest useful slice

Write one acceptance scenario in plain language: *"Given …, when the operator …, then …"*. Cut everything not needed for it. For a pilot, agree upfront: baseline, target, who measures, measurement window and the go/no-go rule.

## 3. Integrate safely

- Discover the real contract of each external system (API docs, sample payloads, rate limits, error behavior, test environment) before building around it.
- Request access through the official channel; never ask users to share passwords, and never store credentials in code, spreadsheets or chat — use environment variables or the approved secret store.
- Read-only first; writes to external systems need explicit approval and must be idempotent.
- Personal data: collect only what the workflow needs, mask it in logs and demos, and confirm who may see it.

## 4. Build and pilot

Build the end-to-end flow for the acceptance scenario. Test it with one representative operator, observe where they hesitate or fail, measure task completion, time and errors, and iterate.

When something is unavailable, keep moving and label it:
- No operator access → list assumptions to validate.
- No API or sandbox → use labelled fixtures; live compatibility is *unverified*.
- Unclear owner or deploy permission → prepare a handoff package and stop before the action.
Do not retry an unchanged external blocker repeatedly.

## 5. Hand off

| Stage | Deliverable |
|---|---|
| Discovery | Filled brief + acceptance scenario + open questions |
| Pilot | Baseline vs. result, defects found, adoption decision (go / adjust / stop) |
| Operation | Owner, runbook, support contact, monitoring, rollback, maintenance cost |

Never deploy without approval, and never present fixture success as proof that the live integration works. Write deliverables in the user's language.
