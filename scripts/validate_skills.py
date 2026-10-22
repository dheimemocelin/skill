#!/usr/bin/env python3
"""Validate this repository's Agent Skill structure using only Python's stdlib."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
EXPECTED_SKILLS = {
    "engineering-os",
    "software-engineering",
    "ai-engineering",
    "data-engineering",
    "ui-ux-design",
    "fde-delivery",
    "git-quality",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def frontmatter(path: Path) -> tuple[dict[str, str], str | None]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, f"{path.relative_to(ROOT)}: frontmatter must start on line 1"

    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, f"{path.relative_to(ROOT)}: missing closing frontmatter delimiter"

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return {}, f"{path.relative_to(ROOT)}: malformed frontmatter line: {line}"
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values, None


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    metadata, error = frontmatter(path)
    if error:
        return [error]

    directory = path.parent.name
    name = metadata.get("name", "")
    description = metadata.get("description", "")
    relative = path.relative_to(ROOT)

    if not name:
        errors.append(f"{relative}: missing name")
    elif len(name) > 64 or not NAME_PATTERN.fullmatch(name):
        errors.append(f"{relative}: name must be lowercase kebab-case, at most 64 characters")
    elif name != directory:
        errors.append(f"{relative}: name '{name}' must match directory '{directory}'")

    if not description:
        errors.append(f"{relative}: missing description")
    elif len(description) > 1024:
        errors.append(f"{relative}: description exceeds 1024 characters")

    return errors


def validate_links() -> list[str]:
    errors: list[str] = []
    for document in ROOT.rglob("*.md"):
        if ".git" in document.parts:
            continue
        text = document.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            target = match.group(1).split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            if path_part and not (document.parent / path_part).resolve().exists():
                errors.append(f"{document.relative_to(ROOT)}: broken local link '{target}'")
    return errors


def main() -> int:
    errors: list[str] = []
    if not SKILLS.is_dir():
        print("ERROR: skills/ directory is missing")
        return 1

    actual = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    for name in sorted(EXPECTED_SKILLS - actual):
        errors.append(f"skills/{name}: expected skill directory is missing")
    for name in sorted(actual - EXPECTED_SKILLS):
        errors.append(f"skills/{name}: unexpected skill directory")

    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{skill_file.relative_to(ROOT)}: required file is missing")
            continue
        errors.extend(validate_skill(skill_file))

    errors.extend(validate_links())
    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(EXPECTED_SKILLS)} skills and local Markdown links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
