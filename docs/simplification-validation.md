# Daily-use simplification — review report

Branch: refactor/daily-engineering-flow. Baseline: 06770ff. This is a reviewable local change, not a release, merge, deployment or consumer installation.

## Changes and invariants

The README is now an entry point for natural requests, project-scoped installation, safe updates and the BUILD/REVIEW/DELIVER contract. Historical Harness material moved to docs/harness.md with links updated and old README anchors retained. No Harness Python source, schema, executor or behavior changed.

Seven canonical skills retain their names and discovery descriptions. Domain content was consolidated: investigation/domain modeling/contracts/tests remain in software-engineering; model evaluations/retrieval/permissions/MCP remain in ai-engineering; analytical correctness and FDE handoff remain separate. UI keeps identity, hierarchy, typography, spacing, responsive/accessibility states and rendered critique. Git retains authorization, diff scope and evidence. Detailed architecture/MCP/PR references remain conditional and portable.

One routing policy now applies to skills, templates and examples: focused requests use the relevant specialty; engineering-os helps only cross-disciplinary coordination. Users need not name a skill. Existing three roles remain optional; the Software Engineer role now asks for relevant domain guidance before considering delegation. Native Codex/Claude formats and role mappings are preserved. No new role, framework, proxy, dependency, external service or telemetry was added.

The five context adjustments are selective loading; targeted investigation/reuse of unchanged reads; traceable concise results; reuse of deterministic tools/current checks; and a single objective delivery report. They are instructions, not a new compression/cache subsystem. The Harness's existing raw-output privacy policy is unchanged.

## Real evaluation

Used the existing behavioral evaluator with versioned natural-request fixtures. No prompt names skills or agents; direct execution is requested to keep delegation a separate question. The runner now supports scoped implementation fixtures in temporary workspaces, independent post-run assertions, the variant's project template, safe synthetic artifact capture and the existing native token counter. Original read-only scenarios retain their defaults.

Baseline uses skills and AGENTS template from 06770ff; current uses branch content. Generated native adapters remain the same mechanism. Each pair starts from identical product fixtures and user requests. Role bodies were not the subject of this direct-work test. This is real Codex CLI 0.166.0 behavior, not a T3 UI/end-to-end or Claude runtime evaluation.

Run 20261105T152352Z covered all five task shapes. Commands:

```bash
PATH=/usr/local/libexec/engineering-os:$PATH python3 scripts/evaluate_engineering_behavior.py --execute --provider all --baseline 06770ff --cases-file examples/behavioral/daily-work-cases.json --timeout 180
```

The exact first-run case specification is retained alongside evidence because scorer metadata was later corrected and the AI task was clarified. The first specification's hash matches the recorded run hash. Original summaries/streams are unchanged under ignored .local-evidence/behavioral/20261105T152352Z.

## Results and evaluation corrections

- Bug: both implementations multiply price by quantity, handle empty orders and pass independent cases. Generated tests are present. Current loads software-engineering directly; baseline additionally loads engineering-os.
- Feature: both preserve add, implement divide and raise the required ValueError for zero denominators. Independent boundary tests pass; focused generated tests are present. Current avoids the router load seen in baseline.
- Review: both identify cross-tenant authorization failure at auth.py:2, with scenario and fix, and preserve fixture content. Both also discuss the difference between a truthy object and authenticated identity. Current uses software-engineering for this code review without requiring a Git delivery operation or reviewer dispatch.
- Interface: both produce a single-file ceramics-studio design with labels, viewport, email type, styling, responsive rules and feedback. Independent HTML checks pass. Browser/Playwright/Chromium were unavailable, so rendered appearance, real focus/keyboard behavior, contrast and screen-reader behavior remain unverified. No screenshot-free claim of visual excellence is made; this scenario is PARTIAL, not visually approved.
- Initial AI-agent request: both implementations enforce allowed labels, reject blank input and pass injected-client assertions. Current uses typed Protocol/Literal boundaries. Neither loads ai-engineering for this deterministic-wrapper wording, so that run does not establish automatic selection of AI-specific evaluation guidance. A focused follow-up pair explicitly describes model-backed AI behavior and representative fake-model evaluation, without naming a skill. No real provider is called by the produced fixture.

The first mutable-case scorer rejected ordinary __pycache__ files; the review scorer inherited customer.py as its expected file. These are evaluator defects, not implementation failures. Fixes allow only bytecode corresponding to declared Python sources and permit a versioned expected review location. Tests reject unrelated source/config and hidden bytecode. Raw verdicts remain visible. Reclassification uses captured changed-file lists, independent validation exits and actual review output; it does not invent a provider rerun. The original mutable-case summary did not retain its standalone index-unchanged boolean, so corrected source-scope evidence is not retroactively presented as a new index check. New summaries retain it explicitly. Read-only original preservation checks included the index.

Independent validators are trusted synthetic test code versioned with the fixture, executed locally with exit status recorded. Their output stays under ignored local evidence. They verify acceptance behavior, not all production edge cases. No consumer files, credentials or real customer data are involved.

## Efficiency and limitations

Native exact skill-body reads demonstrate narrower loading in the focused first-run cases. The UI still loads software-engineering plus ui-ux-design. Session usage counters are preserved with input/cache/output and model-response fields. First-run model-response counts did not fall in these pairs, so no fewer-step claim is made. Raw session input totals were lower for current in these observed pairs, while cache behavior and output size varied; the UI generated more output. This is a single fixed-order pair per task, not a causal token-saving estimate or general quality gain. Do not convert it to a cost claim, and do not infer task-level savings from Markdown size.

Some agents tried an unavailable python command before using python3. That wasted work remains in the totals. No global runtime or new cache was added to hide it. Delegation, actual T3 orchestration, installation into LIA and Claude execution are untested here. Native telemetry was reused locally; no outside telemetry service was introduced.

Before approving visual quality, use an available approved rendering/interaction environment on both HTML artifacts and record layout, keyboard, error/recovery and responsive evidence. Do not install new browser dependencies just to make this report green. Additional repeated/order-balanced task runs would be needed to characterize efficiency variability.

## Final evidence and review state

Focused follow-up run 20261105T153410Z: the natural request explicitly describes a model-backed AI agent and its fake-model behavioral evaluation. Both variants load ai-engineering; baseline also loads engineering-os, while current also loads software-engineering for implementation. Independent input/label/client-call checks pass, native test output confirms fake-client suites succeeded, and source/config scope plus index checks pass in the corrected runner. This supports task-sensitive selection for the tested request, not universal autonomous routing quality.

[Sanitized outcomes and usage](../tests/evidence/daily-workflow-2026-11-05.json) retain original mechanical verdicts and corrected observable checks, native test-suite evidence, exact fixture/config/stream identities and usage counters. [The original case specification](../tests/evidence/daily-workflow-first-case-spec.json) preserves the initial wording; the current versioned fixture contains the clarified AI task and review-location metadata. No failed raw result was overwritten or counted as a new successful model execution. Complete traces and synthetic artifacts remain ignored under the run directories for local review.

Final checks: 71 unit/regression tests passed in 10.915 seconds, including the original 69 and two focused scorer tests. No skips in this environment. Skill/reference/link validator passes and git diff --check reports no whitespace errors. The adapter tests still verify seven skills, three agents, unchanged mapping/native formats, safe staging and portable references. Harness source has no diff from 06770ff. The old core manifest belongs to its historical release candidate and was not silently rewritten to identify this uncommitted branch.

The five requested task categories were executed against both variants: four have functional evidence, and UI has static evidence plus an explicit visual/interaction gap. No overall superiority or general token-saving percentage is claimed. Paired runs are unreplicated and cache effects differ. No browser dependencies, Caveman components, proxy, telemetry or new metrics subsystem were introduced. Native usage collection reuses the existing helper; when unavailable it reports unknown. No merge, push, release, deployment or consumer-project modification was performed. Changes remain on the task branch for user review.

## Historical final verification requested after Phase 2

The environment/product names and exact errors in this section identify tools actually used during that run. They are historical evidence, not installation requirements, a default environment or required browser. The visual gap belongs to that host; another approved renderer can complete the same acceptance checks.

All work remained on refactor/daily-engineering-flow. Only final checks and evidence/report updates were performed in this verification; no new refactor, feature or infrastructure was added.

### 1. Real visual validation — BLOCKED

The current request explicitly authorized browser verification. T3 preview_status returned available=false. preview_open was then attempted and failed before opening a tab: `Preview automation open failed: This host is missing libraries T3's browser needs`, listing libatk-1.0.so.0, libatk-bridge-2.0.so.0, libXcomposite.so.1, libXdamage.so.1, libXfixes.so.3, libXrandr.so.2, libgbm.so.1, libasound.so.2 and libatspi.so.0. No Chromium/Chrome/Firefox executable or Python Playwright was available locally. [Captured environment result](../tests/evidence/final-visual-environment.json).

No package installation, server, new browser infrastructure or administrative change was performed. No tab opened, so no tab required cleanup. Composition, typography, spacing, actual responsive rendering, accessibility and interaction states were NOT visually validated. Existing static HTML checks remain static evidence only; they were not reclassified as rendered evidence. This is an environment blocker, not a confirmed visual defect in the fixture or an excuse to weaken UI acceptance criteria.

### 2. Clean install and fresh-staging update — PASSED within tested scope

An ephemeral isolated source snapshot of baseline 06770ff and temporary consumer projects were used. The existing adapter generator produced separate fresh staging directories for baseline/current, for both Codex and Claude. No actual consumer repository was touched. Checks verified:

- Seven skill entrypoints at each native discovery location.
- Initial installation preserved existing README and AGENTS bytes.
- Reviewed incorporation of the template retained an existing project-specific authorization rule.
- Baseline-to-current update used a second fresh stage; unchanged upstream-owned files updated to current content.
- A locally edited ai-engineering entrypoint was detected as a conflict and preserved until an explicit reviewed merge, which retained its customization. An extra local-policy.md was also retained.
- The generator refused a nonempty unmarked consumer output directory.

This exercised the documented human-reviewed update procedure; it does not claim an automatic installer/updater or prove every possible merge conflict. [Installation/update evidence](../tests/evidence/final-install-validation.json).

An additional real Codex CLI 0.166.0 read-only probe installed current skills without any custom agents into a clean temporary Git project. The model read AGENTS.md and the exact installed software-engineering body in native tool outputs, returned the project-specific CONTRACT-17 rule and the inspected path, and left all fixture hashes unchanged. [Native discovery evidence](../tests/evidence/final-codex-discovery.json).

The first discovery probe accidentally omitted the VM's approved helper PATH and hit the known bwrap loopback failure. That result remains [recorded separately](../tests/evidence/final-codex-discovery-without-helper.json); it was not counted as success. The successful repeat used `PATH=/usr/local/libexec/engineering-os:$PATH`, as already documented, with no system changes. Full native streams are ignored locally under .local-evidence/final-install-without-helper and .local-evidence/final-install-approved. Claude discovery remains structural only because its CLI is unavailable.

### 3. Final diff review — no additional confirmed defects

Reviewed tracked changes against 06770ff and the new documentation/fixtures/evidence. The review covered selective routing and preserved specialties, conditional references, project-file preservation, approvals/secrets, implementation-fixture write scope, independent test results, provider accounting limits and claims about visual quality. No additional confirmed code or instruction defect was found, so none was corrected in this final verification.

Harness source, adapter generator, AI Engineer and Quality Reviewer definitions have no diff from baseline. Three canonical agents and seven skills remain. Software Engineer's only role change makes domain guidance precede optional delegation; its authorization boundaries and mapping are unchanged. Native Codex/Claude formats and the Codex read-only-parent limitation remain documented. UI rendered checks remain required when available; the environmental gap is not visual approval. Existing tests and historical evidence were preserved; the prior scorer corrections remain explicitly documented rather than hidden.

Commands executed: `python3 -m unittest discover -s tests -q` — 71 tests passed in 11.257 seconds, no skips; `python3 scripts/validate_skills.py` passed; `git diff --check` passed. Additional isolated installation assertions and real native discovery ran as described above. No new model task-quality benchmark or token-saving claim was needed for these final checks.

### Recommendation — still BLOCKED for complete Phase 2 validation

Installation/update, real Codex discovery and structural/regression checks passed; no confirmed code blocker remains from this review. The required real visual/interaction validation is unavailable, so full Phase 2 approval is still blocked on that verification. Use an already approved rendering environment (or a separately authorized browser setup), inspect the preserved interface artifacts at mobile/desktop sizes, and record composition, typography, spacing, keyboard/focus, errors/recovery and responsive evidence before changing this verdict. Claude runtime and T3 end-to-end remain unverified separately from the tested Codex CLI flow.

No merge, push, release, deployment or consumer modification was performed. Changes and evidence remain local on the requested branch for review.


## Platform independence verification

Canonical skills, roles and BUILD/REVIEW/DELIVER practices are independent of editor and orchestration product. README and daily-use/Harness guides now use neutral execution-environment language. Codex and Claude Code retain their real, separate adapters and their documented structural/runtime limits. No claim of tested support for additional platforms was introduced.

Reviewed README, docs, templates, all seven skills, all three agents, adapters and examples using case-insensitive searches for T3 Code and variants (T3, t3code, hyphen/underscore/space forms). Removed the product-specific opening/default setup in README, the daily-workflow execution-provider assumption, and the optional Harness guide's product-specific row, link and supervision example. Templates, skills, agents, adapters and examples already contained no such references and required no edits for this correction.

Retained actual product names only in historical validation descriptions and evidence: the failed browser invocation/error, prior runtime scope statements and old Harness source consultations. These identify what was tested; they are not requirements or compatibility claims. Historical JSON and prior evidence files were not rewritten. The canonical UI guidance requires rendered/interaction validation when tools are available and explicit pending status when they are not, without requiring a specific browser.

This change introduces no new command, dependency, abstraction or architecture. No other project or system configuration was modified. The code/adapters and prior behavior results remain unchanged; no paid behavioral rerun was necessary for these documentation corrections. Visual validation remains pending for the preserved interface fixture because the checked host lacked a working renderer, not because Engineering OS depends on that host or product.

Platform-neutrality checks completed: case-insensitive `rg` for `t3[ _-]*code|\bt3\b` returned no matches in README, templates, skills, agents, adapters, examples, docs/daily-workflow.md or docs/harness.md. A repository-wide repeat, excluding historical tests/evidence and this validation report, also returned no matches (rg exit 1 means no matches). Remaining names in this report are scoped historical observations/search records; archived evidence remains verbatim.

Validation after these edits: `python3 -m unittest discover -s tests -q` — 71 passed in 10.922 seconds, no skips; `python3 scripts/validate_skills.py` passed; `git diff --check` passed. Review confirmed documentation-only changes for this follow-up: README.md, docs/daily-workflow.md, docs/harness.md and this report. Existing adapter support and limitations were preserved. A developer can follow the quick start and the domain practices without knowledge of a particular orchestration product. The platform-independence acceptance criterion is met; real visual validation of the earlier fixture remains a separate pending check.

## Publication authorization

After reviewing the known limitations, the user explicitly authorized concluding Phase 2 and integrating this branch into main. The pending rendered UI/interaction evaluation and the absence of a demonstrated general token-saving benefit remain documented; they are not represented as successful validations and do not block this authorized publication. The earlier blocked verdict records the verification state at that time, not an unresolved instruction to withhold publication after this authorization.

Pre-publication checks: 71 tests passed in 10.702 seconds with no skips, skill/link validator passed, and git diff --check passed. The candidate file set was reviewed and scanned for common private-key/token signatures and sensitive/temporary paths; no findings. This is not a comprehensive secret-detection guarantee. Raw transcripts and temporary fixtures remain excluded. No deploy, tag or release publication is authorized by this integration.
