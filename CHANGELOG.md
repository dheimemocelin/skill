# Changelog

## Unreleased
- Add six canonical specialist agent roles and generators for native Claude Code and Codex CLI configuration, keeping the seven existing skills as the reusable knowledge library.
- Add adapter loading tests and platform-specific installation guidance; no agent automatically merges, deploys, or publishes.
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
