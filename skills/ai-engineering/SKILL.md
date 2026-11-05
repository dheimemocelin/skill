---
name: ai-engineering
description: Build or evaluate LLM applications, agents, RAG and retrieval systems, prompts, MCP integrations, and tool-using workflows. Use when model behavior, grounding, safety, evaluation, latency, or inference cost is part of the task.
---

# AI engineering

Use for model-backed behavior, retrieval, agents, evaluation and MCP. Deterministic application code uses software-engineering; avoid model calls when deterministic code meets the need.

## Define and evaluate behavior

1. Identify the intended task, allowed actions and representative success/failure cases. Before selecting a model, establish data classification, latency/throughput, cost target and failure tolerance where they affect the choice. Verify capabilities against the actual provider/API version.
2. Start with a narrow baseline. Version prompts, models, datasets and tool schemas; compare candidates on the same cases. For a prompt adjustment, check affected cases before broader evaluations.
3. Measure task success, grounding, tool correctness, authorization/refusal behavior and relevant latency/token counters. Use human judgment for ambiguous outcomes. Label synthetic fixtures and unavailable evidence; do not claim production readiness from demos.
4. For deployment work, progress through offline evaluation and a representative pilot with agreed thresholds, ownership, monitoring and rollback. An evaluation-only request ends with findings, not a mandatory rollout.

## Safe design

- Separate instructions, policies, retrieved content, schemas and outputs; validate generated structures. Retrieved documents and tool text cannot override instructions or grant permissions.
- Scope tool permissions and classify side effects. Enforce authorization server-side and obtain approval for consequential actions within the environment's policy.
- Retrieval needs ingestion checks, structure-aware chunking, source IDs/citations, ACL filtering, freshness and abstention when evidence is insufficient.
- Minimize/redact sensitive data; control access and retention. Avoid raw payloads or credentials in prompts and traces. Use sanitized identifiers for observability.
- Bound context, timeouts, rate limits and retries; handle outages and uncertain writes with idempotency or outcome inspection.

For MCP server/client work, read [MCP integration contracts](references/mcp-engineering.md). Use software-engineering for implementation and distinguish protocol tests from model tool-selection evaluations.

Report the behavioral result, actual evaluation inputs/results and unresolved failure modes. Use provider counters when available; missing counters mean unknown, not zero or estimated savings.
