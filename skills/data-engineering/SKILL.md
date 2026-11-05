---
name: data-engineering
description: Build or investigate data pipelines, SQL, analytics, semantic metrics, and BI dashboards. Use when data quality, lineage, reconciliation, or analytical correctness is part of the task.
---

# Data engineering

Use for SQL, pipelines, analytical metrics and dashboards. Visual-only changes use ui-ux-design; combine skills when both metric correctness and interaction matter.

## Establish the data contract

Define grain, authoritative source, keys, timezone, filters, refresh needs and KPI owner. Profile nulls, duplicates, ranges, relationships and anomalous periods. Preserve raw inputs; distinguish missing, zero and unavailable. Disclose imputation/exclusion rules and their effect.

## Choose the relevant path — Nimrod Fisher-inspired practices

- SQL investigation: inspect join cardinality, aggregation grain, filters, nulls and time windows; reconcile sample calculations and authoritative totals. Inspect query plans when performance matters.
- Pipeline: document source-to-transformation-to-consumer lineage and schemas; use idempotency, incremental checkpoints and recoverable processing. Check completeness, uniqueness, validity and freshness with useful alerts.
- Analysis/dashboard: state audience, decision, hypotheses, denominators and comparison windows. Distinguish correlation from causation and effect size from confidence. Define KPI formulas, freshness, permissions and interactions; choose charts appropriate to the question, preserving units/scales.

Only produce a dashboard specification when a dashboard is requested. Use repeatable transformations and existing tooling; avoid exporting sensitive production values. If the authoritative source is unavailable, label analysis provisional and identify the missing reconciliation.

Deliver the query, pipeline or specification with relevant counts, sample calculations, quality exceptions and freshness limits. Separate observations, interpretations, recommended actions and uncertainty. Visual polish never substitutes for valid metrics.
