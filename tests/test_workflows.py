"""GitHub Actions workflows must not interpolate expressions into shell scripts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
RUN_KEY_RE = re.compile(r"^(\s*)(?:- )?run:\s*(.*)$")


def run_script_lines(text: str) -> list[str]:
    """Lines that belong to `run:` scripts (inline or block scalar)."""
    lines: list[str] = []
    block_indent: int | None = None
    for line in text.splitlines():
        if block_indent is not None:
            indent = len(line) - len(line.lstrip())
            if line.strip() and indent <= block_indent:
                block_indent = None
            else:
                lines.append(line)
                continue
        match = RUN_KEY_RE.match(line)
        if not match:
            continue
        if match.group(2) in {"|", "|-", ">", ">-"}:
            block_indent = len(match.group(1))
        else:
            lines.append(match.group(2))
    return lines


class WorkflowInjectionTests(unittest.TestCase):
    def test_run_scripts_take_inputs_from_env_only(self) -> None:
        workflows = sorted(WORKFLOWS.glob("*.yml"))
        self.assertTrue(workflows)
        for workflow in workflows:
            script = run_script_lines(workflow.read_text(encoding="utf-8"))
            with self.subTest(workflow=workflow.name):
                self.assertTrue(script)
                self.assertEqual([line for line in script if "${{" in line], [])


if __name__ == "__main__":
    unittest.main()
