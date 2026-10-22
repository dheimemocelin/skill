# Engineering OS — Modular Agent Skills

A collection of seven focused, portable Agent Skills for Claude Code, OpenAI Codex, and other compatible agents. Each skill has a clear scope; load only the specialist skills relevant to the task.

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

## Install

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

## Validate

Requires Python 3.10 or later; uses only the standard library.

```bash
python scripts/validate_skills.py
```

The validator checks the seven expected skill directories, required frontmatter fields, names, descriptions, and local Markdown links. GitHub Actions runs it on pushes and pull requests.

## Design and attribution

The skills are original instructions informed by the practices described in the projects listed in [SOURCES.md](SOURCES.md). Their code and documents are not bundled here. Optional upstream tools remain separate dependencies and must be installed and reviewed independently.

This project is licensed under the MIT License; see [LICENSE](LICENSE). Third-party licenses apply to any upstream material incorporated in the future and must be preserved as required.

## Contributing

Keep skills focused, state their activation scope in `description`, and add or update validation examples when behavior changes. Use the smallest workflow appropriate to the task; update `CHANGELOG.md` for meaningful changes. Do not commit credentials or publish changes without review.
