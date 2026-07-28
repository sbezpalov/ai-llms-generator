# GEMINI.md — Google Antigravity / Gemini

> Antigravity reads both `AGENTS.md` and `GEMINI.md`; on conflict, `GEMINI.md`
> wins. **Project source of truth is `AGENTS.md` — read it first.** This file is
> Antigravity/Gemini-specific.

Russian agent mirror: [`AGENTS.ru.md`](AGENTS.ru.md).

## Agent mode

- Work through a plan: decompose the task and show steps before execution.
- Human-in-the-loop: for production data/core changes — stop and ask.
- Form artifacts (diff, file list, rollback plan) before applying; store them in
  `.antigravity/artifacts/`.
- Do not run shell commands against production servers/databases.
- Keep changes atomic and explain WHAT and WHY.
