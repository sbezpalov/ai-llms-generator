#!/usr/bin/env python3
"""Deterministic checks for the public ai-llms-generator suite (no network)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from aio_heuristics import LLMS_LINK_RE, dump_signals  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "AGENTS.md",
    "AGENTS.ru.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "CONTRIBUTING.ru.md",
    "GEMINI.md",
    "LICENSE",
    "PERPLEXITY.md",
    "PROMPT.md",
    "PROMPT.ru.md",
    "README.md",
    "README.ru.md",
    "SECURITY.md",
    "SECURITY.ru.md",
    "SKILL.md",
    "example-llms.txt",
    "template-llms.txt",
    ".cursorrules",
    ".cursorignore",
    ".cursor/rules/000-project.mdc",
    ".cursor/rules/010-safety.mdc",
    ".cursor/rules/020-llms-txt.mdc",
    ".claude/settings.json",
    ".github/workflows/ci.yml",
    "examples/aio-audit-report.md",
    "examples/llms-dump-antipattern.txt",
    "docs/replace-rank-math-llms.md",
    "docs/aio-lint.md",
    "scripts/check_package.py",
    "scripts/aio_heuristics.py",
    "scripts/aio_lint.py",
    "scripts/install-skill.sh",
    "scripts/install-skill.ps1",
    "examples/aio-lint-fixtures/curated-site/robots.txt",
    "examples/aio-lint-fixtures/curated-site/llms.txt",
    "examples/aio-lint-fixtures/curated-site/index.html",
    "examples/aio-lint-fixtures/dump-site/robots.txt",
    "examples/aio-lint-fixtures/dump-site/llms.txt",
    "examples/aio-lint-fixtures/dump-site/index.html",
    "skills/audit-robots-ai-bots/SKILL.md",
    "skills/draft-json-ld/SKILL.md",
    "skills/aio-site-audit/SKILL.md",
    "skills/draft-json-ld/templates/organization.json",
    "skills/draft-json-ld/templates/README.md",
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

SKILL_COMMANDS = tuple(SKILL_NAMES.values())
FRONTMATTER_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HIGH_CONFIDENCE_SECRET_PATTERNS = (
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def parse_frontmatter(rel: str, text: str) -> dict[str, str]:
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, flags=re.DOTALL)
    if not match:
        fail(f"{rel}: YAML frontmatter is malformed")

    lines = match.group(1).splitlines()
    fields: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        field = re.match(r"^([a-z0-9-]+):(?:\s*(.*))?$", line)
        if not field:
            fail(f"{rel}: unsupported frontmatter line: {line!r}")
        key, value = field.group(1), field.group(2) or ""
        if key in fields:
            fail(f"{rel}: duplicate frontmatter key: {key}")

        if value in {">", ">-", "|", "|-"}:
            block: list[str] = []
            index += 1
            while index < len(lines) and (
                not lines[index] or lines[index].startswith((" ", "\t"))
            ):
                block.append(lines[index].strip())
                index += 1
            value = " ".join(part for part in block if part)
            fields[key] = value
            continue

        fields[key] = value.strip()
        index += 1

    return fields


def validate_skill(rel: str, expected_name: str) -> None:
    fields = parse_frontmatter(rel, read(rel))
    if fields.get("name") != expected_name:
        fail(f"{rel}: frontmatter name must be {expected_name!r}")
    if not FRONTMATTER_NAME_RE.fullmatch(expected_name):
        fail(f"{rel}: invalid skill name: {expected_name!r}")
    description = fields.get("description", "")
    if len(description) < 40 or "Use when" not in description:
        fail(f"{rel}: description must explain what the skill does and when to use it")
    invocation = fields.get("disable-model-invocation")
    if invocation not in {"true", "false"}:
        fail(f"{rel}: disable-model-invocation must be true or false")


def validate_llms_shape(rel: str, text: str, *, is_template: bool = False) -> None:
    if not text.startswith("# "):
        fail(f"{rel}: must start with H1 (# Title)")
    if not re.search(r"^> \S", text, re.MULTILINE):
        fail(f"{rel}: must include a line-start blockquote summary")
    if "http://" in text:
        fail(f"{rel}: only https:// links are allowed")

    headings: list[str] = []
    links_by_section: dict[str, list[str]] = {}
    current_section: str | None = None
    seen_urls: set[str] = set()

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            current_section = line[3:].strip()
            if not current_section:
                fail(f"{rel}:{line_number}: empty H2 heading")
            if current_section in links_by_section:
                fail(f"{rel}:{line_number}: duplicate H2 heading {current_section!r}")
            headings.append(current_section)
            links_by_section[current_section] = []
            continue

        if line.startswith("- "):
            if current_section is None:
                fail(f"{rel}:{line_number}: link entry appears before an H2 section")
            match = LLMS_LINK_RE.fullmatch(line)
            if not match:
                fail(f"{rel}:{line_number}: malformed llms.txt list entry")
            url = match.group(2)
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc:
                fail(f"{rel}:{line_number}: link must be an absolute https URL: {url}")
            if parsed.username or parsed.password:
                fail(f"{rel}:{line_number}: URL credentials are forbidden: {url}")
            if url in seen_urls:
                fail(f"{rel}:{line_number}: duplicate URL: {url}")
            notes = match.group(3)
            if notes and len(notes) > 160:
                fail(f"{rel}:{line_number}: link description exceeds 160 characters")
            seen_urls.add(url)
            links_by_section[current_section].append(url)

    if not headings:
        fail(f"{rel}: must include at least one H2 section")
    empty_sections = [name for name, links in links_by_section.items() if not links]
    if empty_sections:
        fail(f"{rel}: H2 sections must contain links: {', '.join(empty_sections)}")
    oversized_sections = [
        name for name, links in links_by_section.items() if len(links) > 12
    ]
    if oversized_sections:
        fail(
            f"{rel}: sections exceed the 12-link curation heuristic: "
            + ", ".join(oversized_sections)
        )
    if "Optional" in headings and headings[-1] != "Optional":
        fail(f"{rel}: ## Optional must be the last H2 section")

    updated = re.search(r"^Last updated: (.+)$", text, re.MULTILINE)
    if not updated:
        fail(f"{rel}: must include Last updated:")
    if is_template:
        if updated.group(1) != "YYYY-MM-DD":
            fail(f"{rel}: template must keep the YYYY-MM-DD placeholder")
    elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated.group(1)):
        fail(f"{rel}: Last updated must use YYYY-MM-DD")

    size = len(text.encode("utf-8"))
    if not is_template and size > 8 * 1024:
        fail(f"{rel}: curated example exceeds project heuristic (~8 KB): {size}")


def strip_markdown_code(text: str) -> str:
    text = re.sub(r"(?ms)^```.*?^```\s*$", "", text)
    return re.sub(r"`[^`\r\n]+`", "", text)


def validate_relative_markdown_links() -> None:
    for path in sorted((*ROOT.rglob("*.md"), *ROOT.rglob("*.mdc"))):
        if ".git" in path.parts or "artifacts" in path.parts:
            continue
        text = strip_markdown_code(path.read_text(encoding="utf-8"))
        for target in MARKDOWN_LINK_RE.findall(text):
            target = target.strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = path.parent / path_part
            if not resolved.exists():
                fail(f"{path.relative_to(ROOT)}: broken relative link: {target}")


def validate_no_legacy_invocation() -> None:
    command_group = "|".join(re.escape(command) for command in SKILL_COMMANDS)
    legacy = re.compile(rf"@(?:{command_group})\b")
    for path in sorted((*ROOT.rglob("*.md"), *ROOT.rglob("*.mdc"))):
        if ".git" in path.parts or "artifacts" in path.parts:
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if legacy.search(line):
                fail(
                    f"{path.relative_to(ROOT)}:{line_number}: "
                    "use /skill-name, not @skill-name"
                )


def validate_no_high_confidence_secrets() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "artifacts" in path.parts:
            continue
        if path.suffix.lower() not in {
            ".json",
            ".md",
            ".mdc",
            ".ps1",
            ".py",
            ".sh",
            ".txt",
            ".yml",
            ".yaml",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in HIGH_CONFIDENCE_SECRET_PATTERNS):
            fail(f"{path.relative_to(ROOT)}: possible high-confidence secret")


def validate_curated_golden() -> None:
    example = read("example-llms.txt")
    signals = dump_signals(example)
    if signals:
        fail(f"example-llms.txt looks like a dump: {', '.join(signals)}")
    if "blog.bezpalov.com/about/" not in example:
        fail("example-llms.txt must include verified About URL")
    if "blog.bezpalov.com/privacy/" not in example:
        fail("example-llms.txt must include verified Privacy URL")
    if "github.com/sbezpalov/ai-llms-generator" not in example:
        fail("example-llms.txt must link this public suite repo in Optional")
    if "## About" not in example:
        fail("example-llms.txt must include an ## About section")

    antipattern = read("examples/llms-dump-antipattern.txt")
    anti_signals = dump_signals(antipattern)
    if not anti_signals:
        fail("examples/llms-dump-antipattern.txt must trigger dump heuristics")
    if "rank-math-preamble" not in anti_signals:
        fail("antipattern fixture must retain Rank Math preamble marker")


def validate_public_github_docs() -> None:
    for name in ("README.md", "README.ru.md"):
        text = read(name)
        if "github.com/sbezpalov/ai-llms-generator" not in text:
            fail(f"{name}: must link the public GitHub repository")
        if "actions/workflows/ci.yml/badge.svg" not in text:
            fail(f"{name}: must keep the CI status badge")
        if "License-MIT" not in text:
            fail(f"{name}: must keep the MIT license badge")
        if "replace-rank-math-llms.md" not in text:
            fail(f"{name}: must point to Rank Math dump replacement docs")
        if "aio-lint.md" not in text and "aio_lint.py" not in text:
            fail(f"{name}: must document aio-lint CLI")
    readme = read("README.md")
    if "**English**" not in readme or "README.ru.md" not in readme:
        fail("README.md must be English-default with a link to README.ru.md")
    if "не гарантирует" not in read("README.ru.md"):
        fail("README.ru.md must state that the suite does not guarantee outcomes")
    if "does not guarantee" not in readme:
        fail("README.md must state that the suite does not guarantee outcomes")


def validate_aio_lint_cli() -> None:
    for rel in ("scripts/aio_lint.py", "scripts/aio_heuristics.py"):
        if not (ROOT / rel).is_file():
            fail(f"missing {rel}")
    # Offline fixture smoke (no network).
    import subprocess

    curated = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/aio_lint.py"),
            "--fixture",
            str(ROOT / "examples/aio-lint-fixtures/curated-site"),
            "--expect-l2",
            "curated",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if curated.returncode != 0:
        fail(f"aio-lint curated fixture failed: {curated.stderr or curated.stdout}")
    dump = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/aio_lint.py"),
            "--fixture",
            str(ROOT / "examples/aio-lint-fixtures/dump-site"),
            "--expect-l2",
            "dump",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if dump.returncode != 0:
        fail(f"aio-lint dump fixture failed: {dump.stderr or dump.stdout}")
    refused = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/aio_lint.py"),
            "http://example.com",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if refused.returncode != 2:
        fail("aio-lint must refuse non-https URLs with exit 2")


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing required files:\n  - " + "\n  - ".join(missing))

    license_text = read("LICENSE")
    if "MIT License" not in license_text:
        fail("LICENSE must be MIT")
    if "Sergey Bezpalov" not in license_text:
        fail("LICENSE must retain copyright holder")

    for rel, expected_name in SKILL_NAMES.items():
        validate_skill(rel, expected_name)

    for name in ("README.md", "README.ru.md", "SKILL.md", "AGENTS.md"):
        if "emerging convention" not in read(name):
            fail(f"{name}: must call llms.txt an emerging convention")

    agents = read("AGENTS.md")
    leftovers = re.findall(r"<!--\s*TODO:.*?-->", agents)
    if leftovers:
        fail("AGENTS.md still has scaffold TODO comments")
    for safety_term in ("untrusted data", "private/link-local", "access control"):
        if safety_term not in agents:
            fail(f"AGENTS.md: missing network safety term: {safety_term}")
    if "AGENTS.ru.md" not in agents or "English" not in agents:
        fail("AGENTS.md must declare English default and link AGENTS.ru.md")

    example = read("example-llms.txt")
    template = read("template-llms.txt")
    if "## Optional" not in example or "## Optional" not in template:
        fail("template and golden example must demonstrate ## Optional")
    validate_llms_shape("example-llms.txt", example)
    validate_llms_shape("template-llms.txt", template, is_template=True)
    validate_curated_golden()
    validate_public_github_docs()

    for prompt_name in ("PROMPT.md", "PROMPT.ru.md"):
        prompt = read(prompt_name)
        if "{{URL}}" not in prompt:
            fail(f"{prompt_name}: must keep the {{{{URL}}}} placeholder")
        if "generate-llms-txt" not in prompt:
            fail(f"{prompt_name}: must reference generate-llms-txt")
        if "untrusted" not in prompt and "недоверенными" not in prompt:
            fail(f"{prompt_name}: must include prompt-injection safety")
    if "PROMPT.ru.md" not in read("PROMPT.md"):
        fail("PROMPT.md must link the Russian alternative PROMPT.ru.md")

    robot_skill = read("skills/audit-robots-ai-bots/SKILL.md")
    for token in (
        "OAI-SearchBot",
        "GPTBot",
        "ChatGPT-User",
        "ClaudeBot",
        "Claude-SearchBot",
        "Claude-User",
        "Google-Extended",
        "PerplexityBot",
        "Perplexity-User",
        "CCBot",
    ):
        if token not in robot_skill:
            fail(f"audit-robots-ai-bots: missing current token {token}")

    for rel in (
        "skills/draft-json-ld/templates/organization.json",
        "skills/draft-json-ld/templates/article.json",
        "skills/draft-json-ld/templates/faqpage.json",
        "skills/draft-json-ld/templates/breadcrumb.json",
    ):
        data = json.loads(read(rel))
        if data.get("@context") != "https://schema.org":
            fail(f"{rel}: @context must be https://schema.org")
        if "@type" not in data:
            fail(f"{rel}: missing @type")

    install_sh = read("scripts/install-skill.sh")
    install_ps1 = read("scripts/install-skill.ps1")
    for term in ("aio-site-audit", "PROMPT.ru.md", "--force", "--dry-run"):
        if term not in install_sh:
            fail(f"install-skill.sh: missing {term}")
    for term in ("aio-site-audit", "PROMPT.ru.md", "[switch]$Force", "[switch]$DryRun"):
        if term not in install_ps1:
            fail(f"install-skill.ps1: missing {term}")

    workflow = read(".github/workflows/ci.yml")
    for term in ("permissions:", "contents: read", "ubuntu-latest", "windows-latest"):
        if term not in workflow:
            fail(f"ci.yml: missing {term}")

    validate_no_legacy_invocation()
    validate_relative_markdown_links()
    validate_no_high_confidence_secrets()
    validate_aio_lint_cli()

    print("OK: AIO suite checks passed")


if __name__ == "__main__":
    main()
