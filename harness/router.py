"""Explicit routing to canonical files; never embeds or duplicates skill bodies."""

from pathlib import Path
from scripts.build_agent_adapters import parse_agent
from .model import HarnessError

ROOT = Path(__file__).resolve().parents[1]


def route(skills, agent=None):
    known = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    if not isinstance(skills, list) or any(not isinstance(s, str) or s not in known for s in skills):
        raise HarnessError("Unknown skill selection")
    selected = list(skills)
    if agent is not None:
        if agent not in {p.stem for p in (ROOT / "agents").glob("*.md")}:
            raise HarnessError("Unknown agent")
        metadata, _ = parse_agent(ROOT / "agents" / f"{agent}.md")
        selected.extend(metadata["skills"])
    return {
        "skills": {name: str(ROOT / "skills" / name / "SKILL.md") for name in sorted(set(selected))},
        "agent": str(ROOT / "agents" / f"{agent}.md") if agent else None,
        "agent_dispatched": False,
    }
