---
name: ai-engineering
description: Build or evaluate LLM applications, agents, RAG and retrieval systems, prompts, MCP integrations, and tool-using workflows. Use when model behavior, grounding, safety, evaluation, latency, or inference cost is part of the task.
---

# ai-engineering


## MCP integrations

For MCP server/client development or review, read [MCP integration contracts](references/mcp-engineering.md). Use software-engineering for implementation; evaluate model tool selection separately from protocol correctness.


## Choose the starting point

Use for “Evaluate whether our assistant cites the right documents.” A deterministic CSV parser belongs to software-engineering; a query reconciliation belongs to data-engineering.

1. Define the intended task, permitted actions and a representative success/failure example. Collect only constraints that affect the current decision; model selection needs the requirements below.
2. Establish a baseline: existing behavior, deterministic implementation or a narrow model workflow. Avoid adding retrieval or agents without a demonstrated need.
3. Evaluate on representative cases and relevant adversarial cases. Agree on success thresholds for the use case before judging results.
4. Pilot only when measured behavior meets those thresholds and failures have a usable fallback. Broader release needs operational ownership, monitoring and rollback.

For a prompt adjustment, compare the original and revised prompt on affected examples. A production launch requires the broader operating checks below. An evaluation-only request ends with findings and evidence, without requiring a pilot.

## Missing context and completion

If production data or a provider is unavailable, use explicitly labeled synthetic cases to exercise mechanics and report the remaining evidence gap. Do not turn synthetic success into a quality claim. Ask for missing permissions or business thresholds when they determine the next decision.

Deliver the chosen workflow or evaluation, versioned comparison inputs, measured results and remaining failure modes. Example: “Citation accuracy improved on the evaluated set; two access-control cases still fail, so wider rollout remains blocked.”


## Requirements before choosing models
Specify user objective, allowed autonomy, data classification, latency, throughput, target cost, failure tolerance and evaluation dataset. Verify model/API capabilities and provider documentation against the versions actually used; do not hardcode 'best model'.

## Design
- Prefer deterministic software for deterministic operations; use LLM calls only where valuable.
- Separate instructions, policies, retrieval context, tool schemas and outputs; validate generated structured outputs.
- Agent tool calls require scoped permissions, least privilege, explicit side-effect classification and human approval for consequential operations.
- For retrieval: ingestion checks, chunk strategy grounded in document structure, ACL filtering, citations/source IDs, index freshness and abstention when evidence is weak.
- Defend against prompt injection in documents, tools and user-generated content; never treat retrieved text as higher-priority instructions.
- Protect PII: minimize, redact/pseudonymize when needed, access controls, retention controls and avoid raw payloads in traces.
- Handle retries, timeouts, provider outages, context budgets, rate limits and idempotent tool dispatch.

## Evals and operating metrics
Version prompts, models, datasets and tool schemas. Maintain representative golden cases plus adversarial/edge cases. Measure task success, factual grounding, refusal/approval behavior, tool correctness, latency, tokens and cost; use human raters for ambiguous decisions. Compare candidates on the same tasks and record uncertainties. Trace using sanitized identifiers; observe drift and regressions. Never call a demo production-ready without real evals.

## Delivery
Start with narrow workflow plus baseline; run offline evals; controlled pilot with HITL; gradual release with rollback strategy.
