# Codex adapter

Codex CLI discovers project skills from `.agents/skills/<skill-name>/SKILL.md` and project custom agents from `.codex/agents/<name>.toml`. Each custom agent TOML defines `name`, `description`, and `developer_instructions`. The adapter maps canonical hyphenated role IDs to Codex's native underscore IDs. Codex project-scoped configuration is loaded only when the repository is trusted; delegated task labels must use lowercase letters, digits, and underscores.

Generate into a disposable staging directory:

```powershell
python scripts/build_agent_adapters.py --target codex --output ./.generated-codex
```

The output contains `.codex/agents/*.toml` and `.agents/skills/`. Review the files, then copy the role TOML files beneath the target project's `.codex/agents/` and install the skill directories beneath `.agents/skills/`. Preserve existing files. Codex custom agents inherit the parent session's sandbox and tools; a custom agent cannot assign itself a stricter sandbox. The Quality Reviewer is instructed to review only. To enforce read-only behavior, run it in a read-only parent session and account for any external connector permissions. Canonical instructions prohibit agents from merging, deploying, publishing, or performing destructive Git operations automatically and require human approval for consequential side effects.

Codex subagents are native delegated runs (visible through Codex's subagent interface and structured CLI events), rather than Claude's Agent tool interface. Skills are discovered progressively and available to the parent and its subagents; the TOML adapter does not embed skill bodies. Project agents require a trusted project. Codex custom roles inherit the parent sandbox and tools, so role text alone cannot enforce read-only execution.

Official format: [Codex subagents](https://developers.openai.com/codex/subagents) (custom agent TOML files) and [Codex Skills](https://developers.openai.com/codex/skills) (skill discovery and progressive loading).
