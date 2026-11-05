"""Portable progressive references; no model-based routing claims."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import validate_skills as validator
from scripts.build_agent_adapters import generate
from harness.router import route

ROOT = Path(__file__).resolve().parents[1]


class SkillReferenceTests(unittest.TestCase):
    def test_reference_validation_rejects_escape_missing_and_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skills = root / 'skills'
            skill = skills / 'sample'
            skill.mkdir(parents=True)
            entry = skill / 'SKILL.md'
            (root / 'outside.md').write_text('outside')
            (skill / 'valid.md').write_text('valid')
            with patch.object(validator, 'ROOT', root), patch.object(validator, 'SKILLS', skills):
                for target in ['../../outside.md', 'missing.md', '.']:
                    with self.subTest(target=target):
                        entry.write_text(f'[reference]({target})')
                        self.assertTrue(validator.validate_references(entry))
                entry.write_text('[reference](valid.md)\n[external](https://example.com)')
                self.assertEqual(validator.validate_references(entry), [])

    def test_progressive_references_survive_both_adapters(self):
        for provider, prefix in [('codex', '.agents'), ('claude', '.claude')]:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as temporary:
                out = Path(temporary)
                generate(provider, out)
                installed = out / prefix / 'skills'
                for source in (ROOT / 'skills').rglob('*.md'):
                    copied = installed / source.relative_to(ROOT / 'skills')
                    self.assertEqual(copied.read_bytes(), source.read_bytes())
                    for match in validator.LINK_PATTERN.finditer(copied.read_text()):
                        target = match.group(1).split('#', 1)[0]
                        if target and not target.startswith(('https://', 'http://', 'mailto:')):
                            resolved = (copied.parent / target).resolve()
                            self.assertTrue(resolved.is_relative_to(installed.resolve()))
                            self.assertTrue(resolved.is_file())
                # Agent definitions reference skill names, not reference bodies.
                for agent in (out / ('.codex' if provider == 'codex' else '.claude') / 'agents').iterdir():
                    self.assertNotIn('## Enforce trust boundaries', agent.read_text())

    def test_explicit_mcp_and_review_routes_keep_canonical_roles(self):
        mcp = route(['ai-engineering'], 'software-engineer')
        self.assertEqual(set(mcp['skills']), {'ai-engineering', 'software-engineering', 'git-quality'})
        review = route([], 'quality-reviewer')
        self.assertEqual(set(review['skills']), {'git-quality'})
        self.assertFalse(review['agent_dispatched'])
        with self.assertRaises(ValueError):
            route(['mcp-builder'])
