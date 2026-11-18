---
name: software-engineering
description: Implement, debug, refactor, test or design application code, backends, APIs, CLIs and integrations. Use when the user asks to fix a bug, add a feature, change an endpoint, refactor a module, write tests, investigate an error or stack trace, or decide a technical design. Not for metric reconciliation (data-engineering), model or prompt behavior (ai-engineering), visual design (ui-ux-design) or commit, PR and release work (git-quality).
---

# Software engineering

Turn a code request into the smallest correct change, proven by checks that actually ran.

## 0. Learn the project before touching it

Read, in this order, only what exists: `CLAUDE.md` / `AGENTS.md`, the README, the manifest (`package.json`, `pyproject.toml`, `go.mod`, `*.csproj`, `pom.xml`), CI config (`.github/workflows/`, `.gitlab-ci.yml`) and lint/format config. From them, record:

- the test, lint, typecheck and build commands (use these; never invent new ones);
- language version, frameworks and the folder layout for code and tests;
- naming, error-handling and logging conventions shown by neighbouring code.

Project rules override this skill whenever they conflict.

## 1. Pick the workflow

| Request | Do this |
|---|---|
| **Bug** | Reproduce → write a failing test or exact repro command → find the cause → fix narrowly → show the test now passes → run the related suite. |
| **Feature** | Write 2–5 acceptance examples (input → expected result, including one edge and one error case) → implement one end-to-end slice → cover the examples with tests. |
| **Refactor** | Confirm existing tests cover the behavior (add characterization tests if not) → change in small steps → tests stay green after each step. Behavior must not change. |
| **Bug that won't reproduce** | Collect exact inputs, environment, versions and logs around the failure time → compare with a working case → add targeted logging or a test at the suspected boundary. Do not ship a speculative fix as if it were confirmed. |
| **Flaky test** | Run it repeatedly in isolation and in the suite; look for time, order, randomness, network or shared state. Fix the cause; never just add retries or sleeps. |
| **Performance** | Measure first (profiler, query plan, timing with realistic data) → fix the largest measured cost → measure again and report before/after numbers. |
| **Design question** | Read [design review](references/design-review.md) and answer with options, trade-offs and a recommendation. No code unless asked. |
| **Review only** | Report findings (format in section 4). Do not edit files unless asked. |

## 2. Investigate with evidence

- Search for the symbol, then read its implementation, **callers** and **tests** before editing. A change without reading callers is a guess.
- Separate what you observed (error text, failing output, line numbers) from hypotheses. Confirm or kill each hypothesis with one focused check.
- Ask the user only when the answer changes the implementation (e.g. two valid business rules). Otherwise choose the conservative option and state it.
- **Stuck rule:** after three hypotheses fail, stop changing code. Report what was observed, what was ruled out and the next experiment, instead of piling up guesses.
- If the project has no tests for the area, add the smallest test harness the stack already supports; if that is not possible, give an exact manual reproduction and label the result *manually verified*.

## 3. Build rules

- Follow the existing architecture and patterns; copy the style of the nearest similar code.
- Validate input at boundaries; make types explicit at public interfaces (TypeScript types, Python type hints, etc. — the project's own idiom).
- APIs: check validation, authorization on the server, error format, idempotency for retried writes, timeouts, pagination and backwards compatibility.
- Migrations: reversible when possible; never drop or rewrite data without explicit approval.
- No new dependency, framework or abstraction unless the task needs it; say why when you add one.
- **Secrets and personal data:** never hardcode credentials, tokens or connection strings — read them from environment variables or the project's secret store, and use placeholders like `<API_KEY>` in examples. Never put real personal data (names with documents, emails, phone numbers, salaries, health data) in code, fixtures, logs or test names; use synthetic data. If a secret appears in the code or chat, do not repeat it; tell the user to rotate it.

### Example — good vs weak bug fix

Weak: "Changed `total = price * qty` to `total = round(price * qty, 2)`. Should work now."

Good: "Repro: `pytest tests/test_cart.py::test_total_with_discount` failed with `0.30000000000000004 != 0.3`. Cause: float arithmetic in `cart.py:42`. Fix: use `Decimal` for money in `Cart.total`. Added the failing case as a regression test; `pytest tests/test_cart.py` → 18 passed. Not run: full suite (needs DB)."

## 4. Review and deliver

Before finishing: run the project's tests for changed code, plus lint/typecheck if configured; re-read your diff for leftovers (debug prints, commented code, unrelated edits). A regression test must fail without the fix.

For architecture, public contract, dependency or security changes, read [Architecture and regression review](references/design-review.md).

Finish with this format (in the user's language):

```
**Result:** what changed and why (1–3 lines)
**Files:** path — one-line purpose each
**Checks run:** exact command → result (passed / failed / skipped, counts)
**Not verified:** what was not run and why
**Next step:** only if there is a real one
```

Findings format for reviews: `[severity] file:line — problem → impact → suggested fix`. Severity is `critical`, `high`, `medium` or `low`; style notes are labelled `nit`. No findings is a valid result.

Never report a check as passed if it was not run, was skipped, timed out or its output was truncated.
