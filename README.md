# Engineering OS

Modular skills, agent roles and engineering practices for programming agents: describe the task naturally, then receive a scoped solution with evidence. Seven modular skills cover software, AI/MCP, data, UI/UX, field delivery and Git. Three specialist agents and the local Harness are optional.

## Start with the task

- “Investigate this bug and fix it.”
- “Implement this feature using the existing architecture.”
- “Improve this interface's design and accessibility.”
- “Review this code for real defects.”
- “Build this AI agent and validate its behavior.”

You do not need skill names, agent names or JSON plans. The host selects skills from their descriptions; correct selection still needs behavioral validation. For a focused task, use its specialty directly. `engineering-os` helps only when cross-disciplinary coordination adds value. Agents are used only when bounded independent work benefits the task.

## Install in a project

The practices and canonical instructions do not depend on an editor or orchestration product. This repository provides Codex and Claude Code adapters; their runtime validation differs, as documented below. Other integrations require their own format and behavior validation; no universal platform compatibility is claimed.

Use a reviewed commit of this repository. Python 3.11+ supports the generator and adapter tests. Run from the Engineering OS checkout; generate into a **new, empty staging directory** outside the consumer project:

```bash
engos_stage=$(mktemp -d /tmp/engos-codex.XXXXXX)
python3 scripts/build_agent_adapters.py --target codex --output "$engos_stage"
```

1. Inspect the generated `.agents/skills/` and copy skill folders to `<project>/.agents/skills/` **only when the destination is absent**. Review and merge existing folders instead of overwriting them.
2. Merge the relevant short instructions from [templates/AGENTS.md](templates/AGENTS.md) into the project's existing guidance. Preserve project rules and customizations; never replace its AGENTS.md wholesale.
3. Optional: review/copy generated `.codex/agents/*.toml` into `<project>/.codex/agents/`. Skills work without specialist agents.
4. Open the project in the development environment that uses your selected adapter, respecting its trust and permission settings. Start with a natural request. Installed instructions do not grant new permissions.

For Windows use `python` and a new local staging path instead of the Bash `mktemp` example. For Claude, generate with `--target claude`; install skills in `.claude/skills/` and optionally agents in `.claude/agents/`. See the [Codex adapter](adapters/codex/README.md) and [Claude adapter](adapters/claude/README.md) for native format and permission differences.

## Update safely

Select the new source commit and generate into another fresh staging directory. Compare its files with the installed version and review the diff against your project's modifications. Merge intended changes, check obsolete generated references explicitly, and test the project. Do not overlay generated trees blindly: the generator copies files and does not remove obsolete ones. Record the Engineering OS revision in the consumer's installation/update commit when authorized. Revert that scoped commit to roll back; keep unrelated project work intact.

## How work is done

**BUILD:** investigate existing code and domain; define acceptance examples, plan when needed, implement the smallest compatible change with explicit contracts and appropriate types.

**REVIEW:** check behavior and relevant risks. For UI, inspect hierarchy, identity, typography, spacing, responsiveness, accessibility, states and finishing details. Use available rendering and interaction tools; no particular browser is required. Missing visual tooling in an environment means a recorded gap for that evaluation, not visual approval or a general limitation of Engineering OS.

**DELIVER:** state the result, checks actually run and remaining limitations. Reuse valid evidence, preserve failure/skip/exit information and stop when acceptance is established. These are operating principles, not new commands or agents.

Matt Pocock-inspired engineering discipline and Impeccable-inspired visual quality remain central. Use the project's stack; TypeScript is not imposed on Python or other projects. Never expose credentials or customer data, discard unrelated changes, or merge/deploy/publish without authorization.

## Validate this repository

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
```

Tests cover canonical skills/agents, adapter generation and the optional Harness. JSON Schema checks use an existing `jsonschema` installation; absence is reported as skip, not standards validation. Real provider runs can consume quota and remain separate. See the [evidence policy](tests/evidence/README.md) and [behavioral evaluation procedure](docs/skill-evaluation.md).

## Optional and reference material

- [Harness Lite v1](docs/harness.md#engineering-harness-lite-v1) and [v1.1](docs/harness.md#engineering-harness-lite-v11): local explicit plans, checkpoints and opt-in gates. Not required for everyday work with a programming agent.
- [Daily workflow and decisions](docs/daily-workflow.md) and [simplification validation](docs/simplification-validation.md): actual scope, observed behavior and limitations.
- [Routing examples](examples/routing.md): specialties chosen by task, not commands users must memorize.
- [Sources and licenses](SOURCES.md): original engineering guidance; no external framework is bundled. Repository license: [MIT](LICENSE).
- [AI Templates audit](docs/ai-templates-audit.md), [MCP validation](docs/mcp-release-validation.md), [sandbox results](docs/sandbox-remediation-results.md): scoped historical evidence, not universal performance claims.

## Engineering Harness Lite v1

Documentation moved to [the optional Harness guide](docs/harness.md#engineering-harness-lite-v1).

## Engineering Harness Lite v1.1

See [the v1.1 guide](docs/harness.md#engineering-harness-lite-v11). Existing Harness commands and formats are unchanged.
