#!/usr/bin/env python3
"""Generate native Claude Code or Codex agent configuration from agents/*.md."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "agents"
EXPECTED = {
    "software-engineer",
    "ai-engineer",
    "quality-reviewer",
}


def parse_agent(path: Path) -> tuple[dict[str, object], str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path.name}: YAML frontmatter must start on line 1")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path.name}: missing closing frontmatter") from exc

    fields: dict[str, object] = {}
    list_key: str | None = None
    for line in lines[1:end]:
        if line.startswith("  - "):
            if list_key is None:
                raise ValueError(f"{path.name}: list item without a list field")
            fields[list_key].append(line[4:].strip())  # type: ignore[union-attr]
            continue
        if ":" not in line:
            raise ValueError(f"{path.name}: invalid metadata line: {line}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value:
            fields[key] = value
            list_key = None
        else:
            fields[key] = []
            list_key = key
    body = "\n".join(lines[end + 1 :]).strip() + "\n"
    required = {"name", "description", "skills", "read_only"}
    missing = required - fields.keys()
    if missing:
        raise ValueError(f"{path.name}: missing metadata: {', '.join(sorted(missing))}")
    if not isinstance(fields["skills"], list) or not fields["skills"]:
        raise ValueError(f"{path.name}: skills must be a non-empty list")
    for skill in fields["skills"]:
        if not (ROOT / "skills" / str(skill) / "SKILL.md").is_file():
            raise ValueError(f"{path.name}: unknown skill '{skill}'")
    if fields["read_only"] not in {"true", "false"}:
        raise ValueError(f"{path.name}: read_only must be true or false")
    return fields, body


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_instructions(metadata: dict[str, object], body: str) -> str:
    skills = ", ".join(f"`{skill}`" for skill in metadata["skills"])
    return (
        f"The canonical skill library is available; load only the relevant skill(s) from {skills} when needed. "
        "Do not reproduce skill procedures in this agent definition.\n\n"
        + body
    )


def generate(target: str, output: Path) -> list[Path]:
    if target not in {"claude", "codex"}:
        raise ValueError(f"Unsupported target: {target}")
    agent_files = sorted(AGENTS.glob("*.md"))
    names = {path.stem for path in agent_files}
    if names != EXPECTED:
        raise ValueError(f"Expected agents {sorted(EXPECTED)}, found {sorted(names)}")
    definitions = [(source, *parse_agent(source)) for source in agent_files]

    output.mkdir(parents=True, exist_ok=True)
    marker = output / ".engineering-os-generated"
    if marker.is_file():
        if marker.read_text(encoding="utf-8").strip() != target:
            raise ValueError(f"Refusing to reuse output directory for a different adapter: {output}")
    elif any(output.iterdir()):
        raise ValueError(f"Refusing to write into a non-empty unmarked directory: {output}")
    else:
        marker.write_text(target + "\n", encoding="utf-8")

    written: list[Path] = []
    if target == "claude":
        agent_dir = output / ".claude" / "agents"
        skill_dir = output / ".claude" / "skills"
        for source, metadata, body in definitions:
            frontmatter = [
                "---",
                f"name: {metadata['name']}",
                f"description: {metadata['description']}",
            ]
            if metadata["read_only"] == "true":
                frontmatter.append("tools: Read, Glob, Grep, Skill")
            frontmatter.append("---")
            destination = agent_dir / source.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                "\n".join(frontmatter) + "\n\n" + render_instructions(metadata, body),
                encoding="utf-8",
            )
            written.append(destination)
        for skill in sorted((ROOT / "skills").iterdir()):
            if skill.is_dir():
                shutil.copytree(skill, skill_dir / skill.name, dirs_exist_ok=True)
    elif target == "codex":
        codex_dir = output / ".codex"
        role_dir = codex_dir / "agents"
        for source, metadata, body in definitions:
            # Codex requires native spawned agent identifiers to use underscores.
            codex_name = str(metadata["name"]).replace("-", "_")
            role_path = role_dir / f"{codex_name}.toml"
            role_path.parent.mkdir(parents=True, exist_ok=True)
            role_text = (
                f"# Generated from the canonical definition in agents/{source.name}.\n"
                f"name = {toml_string(codex_name)}\n"
                f"description = {toml_string(str(metadata['description']))}\n"
                f"developer_instructions = {toml_string(render_instructions(metadata, body))}\n"
            )
            role_path.write_text(role_text, encoding="utf-8")
            written.append(role_path)
        skill_dir = output / ".agents" / "skills"
        for skill in sorted((ROOT / "skills").iterdir()):
            if skill.is_dir():
                shutil.copytree(skill, skill_dir / skill.name, dirs_exist_ok=True)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("claude", "codex"), required=True)
    parser.add_argument("--output", type=Path, required=True, help="Directory for generated native config and skills")
    args = parser.parse_args()
    try:
        files = generate(args.target, args.output.resolve())
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Generated {len(files)} agent configuration files for {args.target} in {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
