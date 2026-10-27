from __future__ import annotations

import sys
import os
import json
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
from run_agent_smoke_tests import codex_token_usage, dispatches, provider_quota_blocked, skill_events  # noqa: E402


class AgentAdapterLoadingTests(unittest.TestCase):
    def test_claude_activation_is_detected_only_from_native_tool_events(self) -> None:
        events = [
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Agent", "input": {"subagent_type": "software-engineer"}},
                {"type": "tool_use", "name": "Skill", "input": {"skill": "software-engineering"}},
            ]}},
            {"type": "result", "text": "I used the AI Engineer and ai-engineering skill."},
        ]
        self.assertEqual(dispatches("claude", events), ["software-engineer"])
        self.assertEqual(skill_events("claude", events), ["software-engineering"])

    def test_provider_quota_detection_ignores_model_text(self) -> None:
        self.assertFalse(provider_quota_blocked('{"type":"assistant","text":"implement rate limiting"}', ""))
        self.assertTrue(provider_quota_blocked('{"type":"error","message":"You have hit your usage limit"}', ""))
        self.assertTrue(provider_quota_blocked("", "rate limit exceeded"))

    def test_codex_usage_aggregates_parent_and_child_without_duplicate_responses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            sessions = home / "sessions" / "2026" / "10" / "27"
            sessions.mkdir(parents=True)
            thread_id = "thread-fixture"
            parent = sessions / f"rollout-{thread_id}.jsonl"
            child = sessions / "agent-fixture.jsonl"

            def usage(response_id: str, input_tokens: int, cached_tokens: int, output_tokens: int) -> str:
                values = {
                    "input_tokens": input_tokens,
                    "cached_input_tokens": cached_tokens,
                    "cache_write_input_tokens": 0,
                    "output_tokens": output_tokens,
                    "reasoning_output_tokens": 0,
                    "total_tokens": input_tokens + output_tokens,
                }
                return json.dumps({"type": "token_usage_record", "payload": {"response_id": response_id, "usage": values}})

            parent.write_text(usage("response-1", 100, 40, 20) + "\n", encoding="utf-8")
            child.write_text(
                json.dumps({"type": "session_meta", "payload": {"parent_thread_id": thread_id}})
                + "\n"
                + usage("response-1", 100, 40, 20)
                + "\n"
                + usage("response-2", 80, 20, 10)
                + "\n",
                encoding="utf-8",
            )

            previous = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = str(home)
            try:
                result = codex_token_usage(json.dumps({"type": "thread.started", "thread_id": thread_id}))
            finally:
                if previous is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = previous

        self.assertEqual(result["input_tokens"], 180)
        self.assertEqual(result["cached_input_tokens"], 60)
        self.assertEqual(result["uncached_input_tokens"], 120)
        self.assertEqual(result["output_tokens"], 30)
        self.assertEqual(result["total_tokens"], 210)
        self.assertEqual(result["model_responses"], 2)

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
                self.assertIn("canonical skill library", text)
                for skill in canonical["skills"]:
                    self.assertIn(f"`{skill}`", text)
            skill_dir = output / ".claude" / "skills"
            self.assertEqual(
                {path.parent.name for path in skill_dir.glob("*/SKILL.md")},
                {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()},
            )
            reviewer = (agent_dir / "quality-reviewer.md").read_text(encoding="utf-8")
            self.assertIn("tools: Read, Glob, Grep, Skill", reviewer)

    def test_only_the_three_approved_agents_are_canonical(self) -> None:
        self.assertEqual({path.stem for path in (ROOT / "agents").glob("*.md")}, EXPECTED)
        self.assertEqual(
            {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()},
            {
                "engineering-os", "software-engineering", "ai-engineering",
                "data-engineering", "ui-ux-design", "fde-delivery", "git-quality",
            },
        )
        router = (ROOT / "skills" / "engineering-os" / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("| Agent role | Load these skills", router)
        self.assertIn("canonical agent-to-skill mapping", router)

    def test_engineering_os_is_compact_without_losing_routing_or_guardrails(self) -> None:
        router = (ROOT / "skills" / "engineering-os" / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(router.split()), 320)
        for requirement in (
            "cross-disciplinary",
            "canonical agent-to-skill mapping",
            "Load only skills needed",
            "Default to direct work or one specialist",
            "observable acceptance criteria",
            "focused checks",
            "secure defaults",
            "Human approval is required",
            "Never expose secrets or claim unrun checks",
        ):
            self.assertIn(requirement.casefold(), router.casefold())

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
            codex_names = {name.replace("-", "_") for name in EXPECTED}
            self.assertEqual({path.stem for path in agent_dir.glob("*.toml")}, codex_names)
            for role in EXPECTED:
                native_role = role.replace("-", "_")
                role_path = agent_dir / f"{native_role}.toml"
                role_config = tomllib.loads(role_path.read_text(encoding="utf-8"))
                self.assertEqual(role_config["name"], native_role)
                self.assertIn("description", role_config)
                self.assertIn("developer_instructions", role_config)
                self.assertIn("## Boundaries", role_config["developer_instructions"])
                canonical, _ = parse_agent(ROOT / "agents" / f"{role}.md")
                for skill in canonical["skills"]:
                    self.assertIn(f"`{skill}`", role_config["developer_instructions"])
            reviewer = tomllib.loads((agent_dir / "quality_reviewer.toml").read_text(encoding="utf-8"))
            self.assertIn("Review only; do not edit files", reviewer["developer_instructions"])
            skill_dir = output / ".agents" / "skills"
            self.assertEqual(
                {path.parent.name for path in skill_dir.glob("*/SKILL.md")},
                {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()},
            )


if __name__ == "__main__":
    unittest.main()
