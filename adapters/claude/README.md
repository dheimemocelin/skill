# Claude Code adapter

Claude Code discovers project subagents from `.claude/agents/*.md` and skills from `.claude/skills/<skill-name>/SKILL.md`. These native files are generated from `agents/` and `skills/`; edit the canonical files, not generated output.

Generate into a disposable staging directory:

```powershell
python scripts/build_agent_adapters.py --target claude --output ./.generated-claude
```

Review the output, then copy `.generated-claude/.claude/agents` and `.generated-claude/.claude/skills` into the target project's `.claude/` directory. Merge with existing files; do not replace them wholesale. Restart Claude Code if its `.claude/agents/` directory was created after the session started.

The adapter does not preload full skill contents into each subagent. It gives agents skill names and procedures through the canonical prompt; install the skill directories alongside agents so Claude Code can discover them when needed. The Quality Reviewer receives a read-only tool allowlist. All other agents use the session's normal permissions and must follow the canonical side-effect limits.

Official format: [Claude Code custom subagents](https://code.claude.com/docs/en/sub-agents).
