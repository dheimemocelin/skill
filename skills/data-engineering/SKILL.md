---
name: data-engineering
description: Write or debug SQL, build or fix data pipelines and ETL, define metrics and KPIs, analyze datasets, and specify or check BI dashboards. Use when the user asks for a query, a report number that looks wrong, a reconciliation, a data quality check, an ingestion job, or a KPI definition. Not for dashboard visual styling alone (ui-ux-design).
---

# Data engineering

Numbers must be correct and explainable before they are pretty.

## 1. Fix the data contract

Answer these before writing the query or pipeline (from schemas, existing queries and docs; ask only what cannot be found):

- **Grain:** one row = what? (one order, one order line, one customer per day)
- **Source of truth:** which table/system is authoritative for each figure.
- **Keys and joins:** primary keys, expected cardinality of each join (1:1, 1:N).
- **Time:** time zone, date field used (created vs. paid vs. delivered), period boundaries.
- **Filters:** cancelled, test, internal and deleted records — included or not?
- **Owner:** who decides the KPI definition.

## 2. Profile before trusting

Check row counts, nulls, duplicates on the key, value ranges, orphan foreign keys and gaps by date. Distinguish *missing*, *zero* and *not applicable*. Report any exclusion or imputation and how many rows it affects.

## 3. Build

**SQL**
- Check every join for fan-out: compare `COUNT(*)` before and after the join.
- Aggregate at the declared grain; never `SUM` a value already repeated by a join.
- Use CTEs with clear names; comment the business rule next to each filter.
- For performance issues, read the query plan before rewriting.

**Pipelines**
- Document lineage: source → transformations → destination → consumers.
- Make loads idempotent (re-running gives the same result) with incremental checkpoints.
- Add checks for completeness, uniqueness, validity and freshness, with alerts that say what to do.
- Keep raw input untouched; transform into new tables.

**Analysis and dashboards**
- State the decision the analysis supports, the audience and the comparison period.
- Define each KPI: formula, numerator/denominator, filters, refresh frequency, who can see it.
- Prefer simple charts that match the question (trend → line, comparison → bar); keep units and scales honest.
- Separate correlation from causation, and observation from recommendation.

## 4. Reconcile

Recalculate one or two figures by hand from a small sample and compare with the authoritative total (e.g. ERP closing report). If they differ, explain the gap or label the result **provisional**.

### Example

> "Revenue Oct/2026 = R$ 1.284.310,22 (paid date, BRT, excluding cancelled and internal orders). Reconciled with the finance closing: difference R$ 0,00. Profile: 0 duplicate order IDs, 12 orders without customer (kept, flagged)."

## 5. Data protection

Work with aggregates whenever possible. Do not export, paste or log personal data (names with documents, contact details, salaries, financial or health data); use anonymized or synthetic samples. Credentials for databases come from environment variables or the secret store — never in queries, notebooks or code.

## Deliver

```
**Result:** query / pipeline / KPI definition delivered
**Numbers:** key figures with grain, period and filters
**Checks:** row counts, duplicates, reconciliation result
**Limitations:** freshness, provisional parts, exclusions
```
