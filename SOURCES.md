# Sources, attribution, and licensing

Reviewed on 2026-10-22. These repositories informed high-level practices; their skills, scripts, and other files are not bundled in this project.

| Project | Practices consulted | Upstream license |
| --- | --- | --- |
| [Matt Pocock — Skills](https://github.com/mattpocock/skills) | Domain modeling, concise specifications, task slicing, test-first debugging, review, and retrospectives | MIT; see the [upstream license](https://github.com/mattpocock/skills/blob/main/LICENSE) |
| [Nimrod Fisher — Data Analytics Skills](https://github.com/nimrodfisher/data-analytics-skills) | Data quality, semantic metrics, SQL validation, analysis, dashboards, and stakeholder communication | MIT; see the [upstream license](https://github.com/nimrodfisher/data-analytics-skills/blob/main/LICENSE) |
| [pbakaus — Impeccable](https://github.com/pbakaus/impeccable) | Product context, UX shaping, critique, accessibility audits, and visual refinement | Apache-2.0; see the [upstream license](https://github.com/pbakaus/impeccable/blob/main/LICENSE) |

The instructions in this repository are independently written adaptations of general practices. This attribution does not imply endorsement, affiliation, or functional parity. Optional upstream skills, commands, hooks, and engines require separate installation and review.

## Agent configuration formats

The adapters were designed against official documentation checked on 2026-10-22:

| Platform | Format used | Documentation |
| --- | --- | --- |
| Claude Code | Project subagents as Markdown with YAML frontmatter in `.claude/agents/`; project skills in `.claude/skills/` | [Custom subagents](https://code.claude.com/docs/en/sub-agents) |
| Codex CLI | Project custom agents as TOML files in `.codex/agents/`; project skills in `.agents/skills/` | [Subagents](https://developers.openai.com/codex/subagents) and [Skills](https://developers.openai.com/codex/skills) |

These documents informed adapter syntax and discovery behavior only; no upstream agent definitions, skill instructions, or executable components are bundled. Agent roles are canonical in `agents/`; generated platform files are derived artifacts. Claude Code subagents use Markdown frontmatter and Claude's native Agent dispatch; Codex uses TOML roles, native subagent dispatch, and project trust. Codex agents inherit the parent sandbox, so read-only behavior must be enforced by the parent session when required. These mechanisms are not interchangeable. Runtime availability and behavior still require testing with the actual CLI versions in use.

If upstream code, documentation, or other copyrightable material is incorporated later, record its source and pinned revision, preserve required notices, include applicable license texts and `NOTICE` files, and document modifications. The MIT license for this repository does not replace third-party obligations. This source record is not a forensic similarity audit.
