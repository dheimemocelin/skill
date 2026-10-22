from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover - runtime requirement
    raise RuntimeError("Agent adapter loading tests require Python 3.11 or later") from exc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_agent_adapters import EXPECTED, generate, parse_agent  # noqa: E402


class AgentAdapterLoadingTests(unittest.TestCase):
    def test_claude_agents_and_skills_are_discoverable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            generate("claude", output)
            agent_dir = output / ".claude" / "agents"
            self.assertEqual({path.stem for path in agent_dir.glob("*.md")}, EXPECTED)
            for agent_file in agent_dir.glob("*.md"):
                text = agent_file.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\nname: "))
                self.assertIn("description: ", text.split("---", 2)[1])
                canonical, _ = parse_agent(ROOT / "agents" / agent_file.name)
                self.assertIn("Use the existing skills", text)
                for skill in canonical["skills"]:
                    self.assertIn(f"`{skill}`", text)
            skill_dir = output / ".claude" / "skills"
            self.assertEqual(
                {path.parent.name for path in skill_dir.glob("*/SKILL.md")},
                {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()},
            )
            reviewer = (agent_dir / "quality-reviewer.md").read_text(encoding="utf-8")
            self.assertIn("tools: Read, Glob, Grep, Skill", reviewer)

    def test_generator_refuses_existing_unmarked_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / "important.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-empty unmarked"):
                generate("claude", output)
            self.assertEqual((output / "important.txt").read_text(encoding="utf-8"), "preserve")

    def test_codex_agents_and_skill_references_load_as_toml(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            generate("codex", output)
            agent_dir = output / ".codex" / "agents"
            self.assertEqual({path.stem for path in agent_dir.glob("*.toml")}, EXPECTED)
            for role in EXPECTED:
                role_path = agent_dir / f"{role}.toml"
                role_config = tomllib.loads(role_path.read_text(encoding="utf-8"))
                self.assertEqual(role_config["name"], role)
                self.assertIn("description", role_config)
                self.assertIn("developer_instructions", role_config)
                self.assertIn("## Boundaries", role_config["developer_instructions"])
                canonical, _ = parse_agent(ROOT / "agents" / f"{role}.md")
                for skill in canonical["skills"]:
                    self.assertIn(f"`{skill}`", role_config["developer_instructions"])
            reviewer = tomllib.loads((agent_dir / "quality-reviewer.toml").read_text(encoding="utf-8"))
            self.assertIn("Review only; do not edit files", reviewer["developer_instructions"])
            skill_dir = output / ".agents" / "skills"
            self.assertEqual(
                {path.parent.name for path in skill_dir.glob("*/SKILL.md")},
                {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()},
            )


if __name__ == "__main__":
    unittest.main()
