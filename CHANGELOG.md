# Changelog

## Unreleased
- Make the three agents delivery-focused: action-oriented descriptions that say when to dispatch them and what to hand over; a numbered delivery loop (frame, investigate or eval first, change, prove, self-review, hand off); autonomy and stuck rules; fixed completion reports with done/partial/blocked status, acceptance per check and reviewer pointers; reviewer verdict format and handling of unrun checks.
- Sharpen the skills: pre-commit secret scan, hook/amend/revert/conflict rules and a commit example in git-quality; concrete PR body template and CI follow-up in pr-delivery; non-reproducible bug, flaky test, performance and stuck-after-three-hypotheses rules in software-engineering; design decision template; eval JSONL example, code-based grading, cost/caching and observability in ai-engineering; MCP reference as checklists; fan-out SQL check, bisecting wrong totals, LGPD and report traceability block in data-engineering; filled discovery brief example in fde-delivery; concrete widths, zoom and failure signs in ui-ux-design; deliveries in the user's language.
- Rewrite all seven skills for direct use: trigger-rich descriptions with explicit "not for" boundaries, numbered workflows, project-convention discovery, concrete checks, good-vs-weak examples and fixed delivery formats; add explicit secret and personal-data rules; make git-quality self-contained with a new code-review reference; add a no-generator quick install and a fill-in project conventions section to the Claude template. Attribution for adapted practices stays in SOURCES.md.
- Simplify daily operation around natural requests and BUILD/REVIEW/DELIVER; preserve seven skills, three optional agents and the unchanged optional Harness.
- Move Harness documentation out of the quick start, unify selective routing and document project-scoped installation/update with fresh staging.
- Consolidate domain guidance, preserve Matt Pocock/Impeccable practices and conditional references, and add natural-request implementation fixtures to the existing behavioral evaluator with independent assertions and native usage counters.
- Validate candidate 2.0.1-rc.1: clarify MCP JSON Schema required/instance/contract semantics, add six standards fixtures and paired pre-fix evaluation, and decode native nested tool evidence. See docs/mcp-release-validation.md; no superiority over baseline or published release is claimed.
- Add opt-in paired behavioral evaluation fixtures and evidence; record real Codex sandbox blocks and a passing negative case without claiming skill efficacy. Fix Codex PATH discovery and evaluation result extraction.
- Add conditional architecture/security review and MCP contract guidance; strengthen portable skill-reference validation and adapter regression coverage; document selective AI Templates research and skill evaluation limits.
- Improve all seven skills with task-specific paths, activation boundaries, proportional workflows, dependency handling and observable completion examples.
- Document v1.1 capabilities and measured smoke evidence, preserve runnable examples, and configure Python/Node validation for Windows, Linux and macOS (remote CI execution pending).
- Add Harness Lite v1.1 optional read-only Codex CLI execution with explicit cost authorization, JSONL metadata, session checkpoints and no automatic replay; real Windows smoke passed on CLI 0.159.0.
- Extend Harness gates with explicit local Node profiles, per-invocation authorization, bounded process trees and conservative interrupted-gate recovery; preserve v1 plans.
- Add optional Engineering Harness Lite v1: serial local execution, versioned atomic checkpoints, bounded retries, conservative recovery, opt-in test gates, and a deterministic fixture executor; no native provider integration is claimed.
- Add bounded, severity-based read-only review rounds; optional authorized PR/CI handoff; and evidence-based continuation of existing work, informed by TStack principles.
- Reduce the Engineering OS router context while preserving routing, delegation, verification, and safety criteria; extend smoke evidence with exact skill activation and Codex token-usage counters.
- Restrict canonical specialist roles to Software Engineer, AI Engineer, and Quality Reviewer; keep all seven skills as the reusable knowledge library.
- Map canonical hyphenated agent IDs to native underscore identifiers in generated Codex configuration.
- Add provider smoke-test runner and evidence policy for real Claude Code and Codex CLI discovery, activation, and execution checks.
- Clarify that Claude Code and Codex have distinct subagent invocation and permission models; no agent automatically merges, deploys, or publishes.
- Clarify activation scope for the seven skills and align the README with the `dheimemocelin/skill` repository.
- Record verified upstream license identifiers and attribution boundaries in `SOURCES.md`.
- Add a standard-library skill and local-link validator plus a GitHub Actions workflow.
- Add repository ignores for local secrets, editor state, and generated files.

## 2.0.0 — 2026-10-22
- Split monolithic engineering-os into seven independently discoverable Agent Skills.
- Added new design specialist inspired by Impeccable, independent from its executable tool.
- Added analytical quality, semantic metrics and dashboard practice inspired by Nimrod Fisher.
- Added Matt Pocock-inspired domain/spec/ticket/test/debug/retro practices across workflow.
- Documented separate install paths for Codex/Claude Code, optional dependencies, licensing boundary, Git release policy and starter project templates.
- Package validated structurally; agent behavior and external tool integrations not yet tested.
