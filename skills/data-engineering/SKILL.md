---
name: data-engineering
description: Build or investigate data pipelines, SQL, analytics, semantic metrics, and BI dashboards. Use when data quality, lineage, reconciliation, or analytical correctness is part of the task.
---

# data-engineering


## Choose the working path

| Task | Minimum useful work | Completion evidence |
| --- | --- | --- |
| SQL investigation | Confirm grain and keys, inspect joins/filters, reconcile a sample | Explained discrepancy with sample calculations |
| Pipeline | Define contract and refresh needs, implement recoverable processing | Quality checks plus rerun/failure behavior |
| Dashboard | Define audience and KPI formulas, reconcile totals, design decision-oriented views | Validated metrics, freshness and usable states |

“Why did a join double revenue?” belongs here. “Change the dashboard button color” belongs to ui-ux-design. Apply only the workflow steps relevant to the requested output; a SQL fix does not require a dashboard specification.

## Missing context and completion

Represent missing, zero and unavailable values distinctly. Never silently impute or discard records; disclose the rule and its effect. If the authoritative source is inaccessible, provide a provisional analysis with explicit assumptions and identify the reconciliation still required.

Deliver the query/pipeline/specification, relevant reconciliation, quality exceptions and freshness limits. Example: “Revenue reconciles after deduplicating customer keys; 12 records lack a customer ID and are reported separately.”


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
