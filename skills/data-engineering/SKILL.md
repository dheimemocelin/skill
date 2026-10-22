---
name: data-engineering
description: Build or investigate data pipelines, SQL, analytics, semantic metrics, and BI dashboards. Use when data quality, lineage, reconciliation, or analytical correctness is part of the task.
---

# data-engineering


## Workflow (adapted from Nimrod Fisher's data analytics skills)
1. Define grain, source-of-truth, keys, timezone, filters, refresh frequency and owner of each KPI before designing charts.
2. Profile inputs (nulls, duplicates, ranges, referential integrity, distribution, anomalous periods). Never silently overwrite raw data.
3. For SQL, verify joins/cardinality, aggregation grain, filters, null behavior, time windows and query plans. Test with reconciled sample cases.
4. Map lineage from source -> transformation -> semantic layer -> report, with schemas, assumptions and reconciliation to authoritative totals.
5. Analyze with clear hypotheses, segments, denominators and comparison windows. Distinguish correlation from causation, effect magnitude from statistical confidence.
6. Choose visual encoding by question (trend, comparison, distribution, composition, funnel); preserve scales and units; explain caveats.
7. Produce a dashboard specification: audience, decision, KPIs (formula + denominator), breakdowns, data freshness, permissions, interactions and acceptance checks.
8. For stakeholder updates, separate observation, interpretation, recommended action and uncertainty.

## Reliability
Prefer repeatable ELT/ETL with idempotency, incremental checkpoints, failure recovery, data contracts, tests for completeness/uniqueness/validity/freshness and alerts. Protect sensitive values and avoid exporting raw production data casually.

## Quality gate
Provide row/count reconciliation, sample calculations and query plans when relevant. A visually impressive dashboard is not proof of valid metrics.
