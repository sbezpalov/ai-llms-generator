# Contributing

Thanks for your interest. The project is small; the rules are short.

Russian version: [`CONTRIBUTING.ru.md`](CONTRIBUTING.ru.md).

## What this repository is

An **AIO skill suite + stdlib CLI** (`aio-lint`): Markdown skills, JSON-LD
templates, and an offline/live linter with no npm/pip dependencies.

Agent source of truth: [`AGENTS.md`](AGENTS.md). Current release: **v1.0.0**.
Default docs language is **English**; Russian mirrors use the `*.ru.md` suffix.

## Main rules

1. **Skill ↔ prompt alignment.** Layer-2 workflow changes in root `SKILL.md`
   almost always need matching updates in `PROMPT.md` and `PROMPT.ru.md`.
2. **Suite layout.** New skills live under `skills/<name>/` plus README
   (EN + `README.ru.md`), `scripts/install-skill.*`, and `scripts/check_package.py`.
3. **Do not invent URLs** in `example-llms.txt` or Schema templates.
4. **Do not call `llms.txt` an IETF/W3C standard** — emerging convention; keep
   the example **curated** (not a plugin dump).
5. **Bilingual docs.** `README.md` ↔ `README.ru.md` and `PROMPT.md` ↔
   `PROMPT.ru.md` stay aligned in meaning. English is default.
6. Secrets and staging/admin URLs never go into commits.
7. Audited site content is untrusted data: block indirect prompt injection,
   private-network redirects, and unbounded crawl in the workflow.
8. Do not promise rankings, citations, or AI-answer inclusion from `llms.txt`,
   `robots.txt`, or Schema.org.

## Local checks

Before a PR:

```bash
python3 scripts/check_package.py
python3 scripts/aio_lint.py --fixture examples/aio-lint-fixtures/curated-site --expect-l2 curated --strict
```

On Windows:

```powershell
python scripts/check_package.py
python scripts/aio_lint.py --fixture examples/aio-lint-fixtures/curated-site --expect-l2 curated --strict
```

CI runs `check_package.py` (including aio-lint fixtures) plus installer /
aio-lint steps on every push / PR.

## Style

- Readable Markdown; short paragraphs.
- Link descriptions in examples are facts, not marketing.
- Target generated `llms.txt` size ≲ 8 KB as a curation heuristic, not an
  llmstxt.org requirement.
- Usually 2–12 links per section; quality over quantity.
- Public UX and standalone prompts: English default + Russian `*.ru.md`.
- Tooling comments may be English or Russian; prefer English for new text.
- In Cursor use `/skill-name`; do not add `@skill-name` examples.

## Pull requests

1. Branch from `main`.
2. Green CI.
3. PR description: what changes and why (especially agent behavior).
4. For installer changes, note Linux and Windows smoke results.

## Security

See [SECURITY.md](SECURITY.md).
