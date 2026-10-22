---
name: ai-engineering
description: Build or evaluate LLM applications, agents, RAG and retrieval systems, prompts, and tool-using workflows. Use when model behavior, grounding, safety, evaluation, latency, or inference cost is part of the task.
---

# ai-engineering


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
