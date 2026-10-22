# Engineering OS — Modular Agent Skills

A modular engineering system with seven reusable Agent Skills and six specialized agent roles. Agents define who handles a task; skills supply reusable knowledge and procedures. Load only the agent and skills relevant to the task.

## Skills

| Skill | Use it for |
| --- | --- |
| `engineering-os` | Routing end-to-end or cross-disciplinary engineering work |
| `software-engineering` | Application, API, integration, architecture, debugging, and tests |
| `ai-engineering` | LLM applications, agents, retrieval, evaluations, and operations |
| `data-engineering` | Data quality, pipelines, SQL, metrics, analytics, and BI |
| `ui-ux-design` | Product flows, interfaces, accessibility, and design systems |
| `fde-delivery` | Field discovery, integration constraints, pilots, and handoff |
| `git-quality` | Git workflows, CI, review, security, and releases |

## Agents

Canonical, vendor-neutral role definitions live in `agents/`. They define responsibility, activation, boundaries, and completion criteria while referring to skills instead of repeating their procedures.

| Agent | Primary scope |
| --- | --- |
| `software-engineer` | Application and API behavior, implementation, reliability |
| `ai-engineer` | LLM applications, agents, retrieval, evaluation |
| `data-engineer` | Data pipelines, SQL, metrics, analytics, BI |
| `design-engineer` | Product flows, frontend, accessibility, visual quality |
| `fde` | Field discovery, integrations, measurable delivery, handoff |
| `quality-reviewer` | Independent, read-only evidence-based review |

Adapter instructions live in `adapters/`. Generated files are disposable; edit only `agents/` and `skills/`.

## Install skills

Copy the skill directories into the directory your agent scans. Review any same-named skill before replacing it.

```powershell
# Codex, from this repository root
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
Copy-Item -Recurse -Path "./skills/*" -Destination "$HOME/.agents/skills/"

# Claude Code, from this repository root
New-Item -ItemType Directory -Force "$HOME/.claude/skills" | Out-Null
Copy-Item -Recurse -Path "./skills/*" -Destination "$HOME/.claude/skills/"
```

For project-scoped installation, use `<project>/.agents/skills` for Codex or `<project>/.claude/skills` for Claude Code. Merge `templates/AGENTS.md` and `templates/CLAUDE.md` with existing project guidance; do not replace project instructions wholesale.

## Generate agent adapters

The generator writes native configuration and a copy of the seven skills into a staging directory. Review and merge the output into a target project; it never edits an agent's home directory or overwrites existing project configuration.

```powershell
python scripts/build_agent_adapters.py --target claude --output ./.generated-claude
python scripts/build_agent_adapters.py --target codex --output ./.generated-codex
```

Follow [Claude Code adapter instructions](adapters/claude/README.md) or [Codex adapter instructions](adapters/codex/README.md) to install. Claude Code loads project subagents from `.claude/agents/`; Codex CLI loads project custom agents from `.codex/agents/`. Claude's Quality Reviewer gets a read-only tool allowlist. Codex custom agents inherit their parent session's sandbox, so run the reviewer in a read-only session when enforcement is needed. No adapter performs merge, deploy, or publication actions.

## Validate

Structural validation uses Python 3.10 or later and only the standard library. Adapter loading tests use Python 3.11 or later to parse TOML with `tomllib`.

```bash
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

The validator checks the seven expected skill directories, required frontmatter fields, names, descriptions, and local Markdown links. GitHub Actions runs it on pushes and pull requests.

## Design and attribution

The skills are original instructions informed by the practices described in the projects listed in [SOURCES.md](SOURCES.md). Their code and documents are not bundled here. Optional upstream tools remain separate dependencies and must be installed and reviewed independently.

This project is licensed under the MIT License; see [LICENSE](LICENSE). Third-party licenses apply to any upstream material incorporated in the future and must be preserved as required.

## Contributing

Keep skills focused, state their activation scope in `description`, and add or update validation examples when behavior changes. Use the smallest workflow appropriate to the task; update `CHANGELOG.md` for meaningful changes. Do not commit credentials or publish changes without review.
