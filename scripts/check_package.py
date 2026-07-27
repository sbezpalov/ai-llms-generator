#!/usr/bin/env python3
"""Smoke checks for the public ai-llms-generator package (no network)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "GEMINI.md",
    "LICENSE",
    "PERPLEXITY.md",
    "PROMPT.md",
    "README.en.md",
    "README.md",
    "SECURITY.md",
    "SKILL.md",
    "example-llms.txt",
    "template-llms.txt",
    ".cursorrules",
    ".cursorignore",
    ".cursor/rules/000-project.mdc",
    ".cursor/rules/010-safety.mdc",
    ".cursor/rules/020-llms-txt.mdc",
    ".claude/settings.json",
    "scripts/check_package.py",
    "scripts/install-skill.sh",
    "scripts/install-skill.ps1",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
    if missing:
        fail("missing required files:\n  - " + "\n  - ".join(missing))

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "MIT License" not in license_text:
        fail("LICENSE must be MIT")
    if "Sergey Bezpalov" not in license_text:
        fail("LICENSE must retain copyright holder")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---"):
        fail("SKILL.md must start with YAML frontmatter")
    fm_match = re.match(r"^---\n(.*?)\n---\n", skill, flags=re.DOTALL)
    if not fm_match:
        fail("SKILL.md frontmatter is malformed")
    frontmatter = fm_match.group(1)
    if "name: generate-llms-txt" not in frontmatter:
        fail("SKILL.md frontmatter must set name: generate-llms-txt")
    if "description:" not in frontmatter:
        fail("SKILL.md frontmatter must include description")

    for name in ("README.md", "README.en.md", "SKILL.md", "AGENTS.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        if "emerging convention" not in text:
            fail(f"{name}: must mention that llms.txt is an emerging convention")

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    leftover = re.findall(r"<!--\s*TODO:.*?-->", agents)
    if leftover:
        fail(
            "AGENTS.md still has scaffold TODO comments:\n  - "
            + "\n  - ".join(leftover)
        )

    example = (ROOT / "example-llms.txt").read_text(encoding="utf-8")
    if "Last updated:" not in example:
        fail("example-llms.txt must include Last updated:")
    if "https://" not in example:
        fail("example-llms.txt must include absolute https:// URLs")

    template = (ROOT / "template-llms.txt").read_text(encoding="utf-8")
    if "# Site Name" not in template:
        fail("template-llms.txt looks empty or wrong")

    prompt = (ROOT / "PROMPT.md").read_text(encoding="utf-8")
    if "{{URL}}" not in prompt:
        fail("PROMPT.md must keep {{URL}} placeholder for users")

    print("OK: package smoke checks passed")


if __name__ == "__main__":
    main()
