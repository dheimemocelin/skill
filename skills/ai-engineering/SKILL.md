---
name: ai-engineering
description: Build, evaluate or debug features powered by LLMs, including prompts, agents, tool calling, RAG and embeddings, MCP servers and clients, structured outputs and model evaluation. Use when the user asks to create or improve a chatbot, agent, prompt, retrieval pipeline or MCP tool, compare models, reduce hallucination, latency or token cost, or test model behavior. Not for ordinary deterministic code (software-engineering).
---

# AI engineering

Make model-backed behavior measurable, grounded and safe. If plain deterministic code solves the problem reliably, use it instead of a model call and say so.

## 1. Define the behavior first

Before writing prompts or picking a model, write down:

- **Task:** what the model must do and what it must never do (e.g. never invent a policy, never execute a payment).
- **Data:** what data enters the prompt and its sensitivity. Personal or confidential data needs a reason, minimization and masking.
- **Targets:** acceptable latency, cost per request and error tolerance.
- **Eval set:** 10–30 representative cases — typical, edge, adversarial (prompt injection, out-of-scope) — each with the expected outcome. Store them in the repo (e.g. `evals/cases.jsonl`).

Verify model names, parameters and SDK features against the provider's current docs and the installed SDK version; do not rely on memory.

## 2. Build iteratively

1. Start with the simplest baseline (one prompt, one model, no agent loop).
2. Version prompts, model IDs, tool schemas and datasets in the repo.
3. Change one thing at a time and re-run the affected eval cases; compare against the previous version on the same cases.
4. Escalate complexity (retrieval, tools, multi-step agents) only when the eval shows the simpler version fails.

## 3. Design rules

- **Separate trust levels:** system instructions, user input, retrieved documents and tool outputs stay in distinct, labelled sections. Retrieved or tool text can never override instructions or grant permissions.
- **Structured outputs:** request JSON with a schema and validate it in code before use; handle invalid output with retry or a safe fallback.
- **Tools:** give each tool the narrowest permission; enforce authorization on the server, not in the prompt; require human approval for consequential actions (send, pay, delete, publish).
- **RAG:** chunk by document structure, keep source IDs, filter by the user's access rights before retrieval, show citations, and answer "not found" when evidence is insufficient.
- **Data protection:** no credentials in prompts, code or traces (use environment variables); mask personal data in logs and traces; respect retention rules.
- **Resilience:** set timeouts, bounded retries with backoff, max tokens and max agent steps; make retried writes idempotent.

For MCP servers or clients, read [MCP integration contracts](references/mcp-engineering.md).

## 4. Evaluate and report

Measure on the eval set: task success, grounding/citation accuracy, correct tool choice and arguments, correct refusals, latency and tokens (from provider counters — missing counters are *unknown*, not zero). Use human judgment for ambiguous cases. Demos and synthetic fixtures do not prove production readiness; label them.

```
**Behavior:** what the system does now
**Eval:** N cases → X passed, Y failed (list failed case IDs and why)
**Cost/latency:** measured values or "not measured"
**Risks:** open failure modes, untested inputs
**Next step:** pilot criteria or fixes
```

An evaluation-only request ends with findings, not a rollout plan.
