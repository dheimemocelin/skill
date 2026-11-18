# Natural requests and selective context

These examples describe host selection, not required user commands. Load conditional references only when needed. An unavailable skill/tool is a limitation, not proof of activation.

| Natural request | Relevant guidance | Acceptance evidence |
| --- | --- | --- |
| Fix duplicate order submission | software-engineering | Reproduction, targeted regression, unchanged nearby behavior |
| Add an API feature following existing architecture | software-engineering | Contracts, boundary/error tests, reviewed diff |
| Review an authorization change | git-quality; code-review reference | Correct reviewed revision, exploit scenario, location and fix |
| Improve the signup form | ui-ux-design; software-engineering for implementation | Rendered layout, keyboard/states, accessibility and responsive checks |
| Implement and evaluate an AI assistant | ai-engineering; software-engineering as needed | Fake-client checks, representative behavioral cases, authorization |
| Reconcile dashboard totals | data-engineering; ui-ux-design only for changed interactions | Grain/keys, sample calculations and authoritative reconciliation |
| Scope a customer pilot | fde-delivery; relevant implementation skills | Operator acceptance, integration limits and handoff |

Add engineering-os only when combining disciplines needs coordination. Add Git delivery guidance when repository operations are in scope. Three specialist roles remain available through the native adapters; none is mandatory for these requests.

## Boundary cases

| Request | Expected |
| --- | --- |
| "Explain what a JOIN is" | Answer directly; no workflow or delivery template needed |
| "Commit this" while reviewing | git-quality, but only after the user authorizes the commit |
| "Make the chart prettier" | ui-ux-design only; data-engineering only if numbers change |
