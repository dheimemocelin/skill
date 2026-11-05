# Claude Code adapter

Claude Code discovers project subagents from `.claude/agents/*.md` and skills from `.claude/skills/<skill-name>/SKILL.md`. These native files are generated from `agents/` and `skills/`; edit the canonical files, not generated output.

Agents are optional: installing only the generated skill directories supports direct work. Generate into a fresh staging directory for each installation or update; compare and merge consumer customizations, and explicitly review obsolete files. Never overlay an existing project blindly.

Replace `NEW` with a fresh identifier each time. Generate into a disposable staging directory:

```powershell
python scripts/build_agent_adapters.py --target claude --output ./.generated-claude-NEW
```

Review the output, then copy `.generated-claude-NEW/.claude/agents` and `.generated-claude-NEW/.claude/skills` into the target project's `.claude/` directory. Merge with existing files; do not replace them wholesale. Restart Claude Code if its `.claude/agents/` directory was created after the session started.

The adapter does not preload full skill contents into each subagent. It references relevant skill names in the canonical prompt; install skill directories alongside agents so Claude Code can discover and load them when needed. The Quality Reviewer receives a read-only tool allowlist. All other agents use the session's normal permissions and must follow the canonical side-effect limits. Claude subagents are invoked through Claude's native Agent mechanism; this is not the same dispatch or permission model as Codex.

Official format: [Claude Code custom subagents](https://code.claude.com/docs/en/sub-agents).
