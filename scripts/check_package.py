#!/usr/bin/env python3
"""Smoke checks for the public ai-llms-generator AIO suite (no network)."""

from __future__ import annotations

import json
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
    "skills/audit-robots-ai-bots/SKILL.md",
    "skills/draft-json-ld/SKILL.md",
    "skills/aio-site-audit/SKILL.md",
    "skills/draft-json-ld/templates/organization.json",
    "skills/draft-json-ld/templates/article.json",
    "skills/draft-json-ld/templates/faqpage.json",
    "skills/draft-json-ld/templates/breadcrumb.json",
]

SKILL_NAMES = {
    "SKILL.md": "generate-llms-txt",
    "skills/audit-robots-ai-bots/SKILL.md": "audit-robots-ai-bots",
    "skills/draft-json-ld/SKILL.md": "draft-json-ld",
    "skills/aio-site-audit/SKILL.md": "aio-site-audit",
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def validate_llms_shape(path: Path, text: str) -> None:
    if not text.lstrip().startswith("# "):
        fail(f"{path.name}: must start with H1 (# Title)")
    if "> " not in text and not re.search(r"^> ", text, re.M):
        fail(f"{path.name}: should include a blockquote summary (llmstxt.org)")
    if "## " not in text:
        fail(f"{path.name}: should include at least one H2 section")
    if "https://" not in text and path.name.startswith("example"):
        fail(f"{path.name}: example must include https:// URLs")
    size = len(text.encode("utf-8"))
    if size > 8 * 1024 and path.name.startswith("example"):
        fail(f"{path.name}: curated example exceeds ~8KB ({size} bytes)")


def main() -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
    if missing:
        fail("missing required files:\n  - " + "\n  - ".join(missing))

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "MIT License" not in license_text:
        fail("LICENSE must be MIT")
    if "Sergey Bezpalov" not in license_text:
        fail("LICENSE must retain copyright holder")

    for rel, expected_name in SKILL_NAMES.items():
        skill = (ROOT / rel).read_text(encoding="utf-8")
        if not skill.startswith("---"):
            fail(f"{rel}: must start with YAML frontmatter")
        fm_match = re.match(r"^---\n(.*?)\n---\n", skill, flags=re.DOTALL)
        if not fm_match:
            fail(f"{rel}: frontmatter is malformed")
        frontmatter = fm_match.group(1)
        if f"name: {expected_name}" not in frontmatter:
            fail(f"{rel}: frontmatter must set name: {expected_name}")
        if "description:" not in frontmatter:
            fail(f"{rel}: frontmatter must include description")

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
    if "## Optional" not in example:
        fail("example-llms.txt must include ## Optional (llmstxt.org)")
    validate_llms_shape(ROOT / "example-llms.txt", example)

    template = (ROOT / "template-llms.txt").read_text(encoding="utf-8")
    if "# Site Name" not in template:
        fail("template-llms.txt looks empty or wrong")
    if "## Optional" not in template:
        fail("template-llms.txt must include ## Optional")
    validate_llms_shape(ROOT / "template-llms.txt", template)

    prompt = (ROOT / "PROMPT.md").read_text(encoding="utf-8")
    if "{{URL}}" not in prompt:
        fail("PROMPT.md must keep {{URL}} placeholder for users")
    if "generate-llms-txt" not in prompt:
        fail("PROMPT.md must reference skill folder generate-llms-txt")

    for rel in (
        "skills/draft-json-ld/templates/organization.json",
        "skills/draft-json-ld/templates/article.json",
        "skills/draft-json-ld/templates/faqpage.json",
        "skills/draft-json-ld/templates/breadcrumb.json",
    ):
        raw = (ROOT / rel).read_text(encoding="utf-8")
        data = json.loads(raw)
        if data.get("@context") != "https://schema.org":
            fail(f"{rel}: @context must be https://schema.org")
        if "@type" not in data:
            fail(f"{rel}: missing @type")

    install_sh = (ROOT / "scripts/install-skill.sh").read_text(encoding="utf-8")
    if "aio-site-audit" not in install_sh:
        fail("install-skill.sh must install aio-site-audit")

    print("OK: AIO suite smoke checks passed")


if __name__ == "__main__":
    main()
