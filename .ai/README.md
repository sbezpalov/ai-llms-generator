# .ai/ — AI tooling layout

**Source of truth is [`../AGENTS.md`](../AGENTS.md)** (read natively by Cursor,
Antigravity/Gemini, and others). Other files are thin redirects / tool-specific
notes. Russian agent mirror: [`../AGENTS.ru.md`](../AGENTS.ru.md).

| Tool | File | Artifacts |
|---|---|---|
| All agents | `AGENTS.md` | `.ai/artifacts/` |
| Cursor | `.cursorrules` → AGENTS.md; `.cursor/rules/*.mdc`; `.cursorignore` | `.cursor/artifacts/` |
| Claude (Code / Cowork) | `CLAUDE.md` → AGENTS.md; `.claude/` | `.claude/artifacts/` |
| Antigravity / Gemini | `GEMINI.md` (+ AGENTS.md) | `.antigravity/artifacts/` |
| Perplexity | `PERPLEXITY.md` (pasteable brief) | `.perplexity/artifacts/` |

## Rule

Project changes → edit **`AGENTS.md`**. Tool-specific detail → that tool’s file.
An artifact is a durable session output (plan, research, diff, task list).

<!-- init-ai-tooling v2 (2026-07-27); docs EN-default. -->
